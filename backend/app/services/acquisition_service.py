"""
Acquisition service for RF data capture.

Provides high-level interface for:
- Starting/stopping spectrum sweeps
- Starting/stopping IQ recordings
- Monitoring acquisition status
- Saving acquired data
"""

import threading
import time
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import uuid

from app.devices.bb60c.adapter import BB60CAdapter
from app.devices.bb60c.iq_capture import BB60CIQCapture
from app.api.schemas.acquisition import (
    AcquisitionMetadata,
    AcquisitionMode,
    SpectrumSnapshot,
    IQRecording,
)
from app.services.storage_service import StorageService


class RecordingStatus(str, Enum):
    """Status of an ongoing recording."""
    INITIALIZING = "initializing"
    RECORDING = "recording"
    STOPPING = "stopping"
    STOPPED = "stopped"
    SAVED = "saved"
    ERROR = "error"


@dataclass
class RecordingState:
    """Internal state of a recording session."""
    recording_id: str
    status: RecordingStatus
    start_time: float
    expected_duration: Optional[float]
    expected_samples: Optional[int]
    collected_samples: int
    filename: Optional[str]
    error: Optional[str]


class AcquisitionService:
    """
    High-level acquisition service.
    
    Manages:
    - Sweep acquisition (real-time, short-term)
    - IQ recording (long-term, file-based)
    - Status monitoring
    - Data persistence
    """
    
    def __init__(self, device: BB60CAdapter, storage: StorageService):
        """
        Initialize acquisition service.
        
        Args:
            device: Connected BB60C adapter instance
            storage: StorageService for data persistence
        """
        self.device = device
        self.storage = storage
        self.iq_capture = BB60CIQCapture(device.handle)
        
        # Recording state tracking
        self._recordings: Dict[str, RecordingState] = {}
        self._recordings_lock = threading.Lock()
    
    # ========================================================================
    # SWEEP ACQUISITION
    # ========================================================================
    
    def get_current_sweep(self) -> Optional[SpectrumSnapshot]:
        """
        Get current spectrum sweep snapshot.
        
        Returns:
            SpectrumSnapshot or None if not available
        """
        # Import here to avoid circular imports
        from app.rf.state import spectrum_state
        
        with spectrum_state.lock:
            if spectrum_state.snapshot is None:
                return None
            return spectrum_state.snapshot
    
    # ========================================================================
    # IQ RECORDING
    # ========================================================================
    
    def start_iq_recording(
        self,
        center_frequency_hz: float,
        bandwidth_hz: float,
        sample_rate_sps: float,
        duration_seconds: float,
        location_name: Optional[str] = None,
        operator_name: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        """
        Start a new IQ recording session.
        
        Args:
            center_frequency_hz: Center frequency
            bandwidth_hz: Capture bandwidth
            sample_rate_sps: Sample rate
            duration_seconds: Duration to record
            location_name: Optional location description
            operator_name: Optional operator name
            notes: Optional notes
            
        Returns:
            Recording ID string
        """
        recording_id = str(uuid.uuid4())[:8]
        
        try:
            # Start capture on device
            total_samples, actual_sample_rate = self.iq_capture.start_iq_capture(
                center_frequency_hz=center_frequency_hz,
                bandwidth_hz=bandwidth_hz,
                sample_rate_sps=sample_rate_sps,
                duration_seconds=duration_seconds,
            )
            
            # Track recording state
            with self._recordings_lock:
                self._recordings[recording_id] = RecordingState(
                    recording_id=recording_id,
                    status=RecordingStatus.RECORDING,
                    start_time=time.time(),
                    expected_duration=duration_seconds,
                    expected_samples=total_samples,
                    collected_samples=0,
                    filename=None,
                    error=None,
                )
            
            print(f"[AcquisitionService] Started IQ recording {recording_id}")
            print(f"  Center: {center_frequency_hz/1e6:.2f} MHz")
            print(f"  Bandwidth: {bandwidth_hz/1e6:.2f} MHz")
            print(f"  Sample rate: {actual_sample_rate/1e6:.2f} MSps")
            print(f"  Expected samples: {total_samples:,}")
            
            return recording_id
            
        except Exception as e:
            print(f"[AcquisitionService] Error starting recording: {e}")
            with self._recordings_lock:
                self._recordings[recording_id] = RecordingState(
                    recording_id=recording_id,
                    status=RecordingStatus.ERROR,
                    start_time=time.time(),
                    expected_duration=None,
                    expected_samples=None,
                    collected_samples=0,
                    filename=None,
                    error=str(e),
                )
            raise
    
    def stop_iq_recording(self, recording_id: str) -> Optional[str]:
        """
        Stop an IQ recording and save to disk.
        
        Args:
            recording_id: Recording ID from start_iq_recording()
            
        Returns:
            Path to saved file, or None if error
        """
        with self._recordings_lock:
            if recording_id not in self._recordings:
                raise ValueError(f"Unknown recording ID: {recording_id}")
            
            rec_state = self._recordings[recording_id]
            if rec_state.status != RecordingStatus.RECORDING:
                raise ValueError(f"Recording not in progress: {recording_id}")
            
            rec_state.status = RecordingStatus.STOPPING
        
        try:
            # Stop device capture
            self.iq_capture.stop_iq_capture()
            
            # Get captured data
            iq_data = self.iq_capture.get_iq_data()
            if iq_data is None or len(iq_data) == 0:
                raise RuntimeError("No IQ data captured")
            
            # Create metadata
            device_info = self.device.get_device_info()
            diag = self.device.get_diagnostics()
            
            metadata = AcquisitionMetadata(
                timestamp_utc=time.time(),
                device_id=f"BB60C_SN{device_info.serial_number}",
                serial_number=device_info.serial_number,
                device_type="BB60C",
                firmware_version=str(device_info.firmware_version),
                api_version=self.device.get_api_version(),
                center_frequency_hz=0,  # Would need to capture from device
                span_hz=0,
                start_frequency_hz=0,
                stop_frequency_hz=0,
                rbw_hz=0,
                vbw_hz=0,
                reference_level_dbm=0,
                attenuation_db=0,
                detector_type="iq",
                acquisition_mode=AcquisitionMode.IQ,
                sample_rate_sps=40e6,  # TODO: Get from device config
                sample_count=len(iq_data),
                duration_seconds=(time.time() - rec_state.start_time),
            )
            
            # Create recording object
            iq_recording = IQRecording(
                metadata=metadata,
                iq_data=iq_data,
                sample_count=len(iq_data),
                power_watts=1.0,  # TODO: Calculate
                peak_to_average_ratio_db=0,  # TODO: Calculate
                crest_factor=0,  # TODO: Calculate
            )
            
            # Save to storage
            rec_state.status = RecordingStatus.SAVING
            filepath = self.storage.save_iq_recording(iq_recording)
            rec_state.filename = filepath.name
            rec_state.status = RecordingStatus.SAVED
            
            print(f"[AcquisitionService] Recording {recording_id} saved")
            return str(filepath)
            
        except Exception as e:
            print(f"[AcquisitionService] Error saving recording: {e}")
            with self._recordings_lock:
                if recording_id in self._recordings:
                    self._recordings[recording_id].status = RecordingStatus.ERROR
                    self._recordings[recording_id].error = str(e)
            raise
    
    def get_iq_recording_status(self, recording_id: str) -> Dict:
        """
        Get status of an IQ recording.
        
        Returns:
            Dict with status information
        """
        with self._recordings_lock:
            if recording_id not in self._recordings:
                raise ValueError(f"Unknown recording ID: {recording_id}")
            
            rec_state = self._recordings[recording_id]
            
            elapsed = time.time() - rec_state.start_time
            progress = 0.0
            remaining = None
            
            if rec_state.expected_duration:
                progress = min(elapsed / rec_state.expected_duration, 1.0)
                remaining = max(0, rec_state.expected_duration - elapsed)
            
            return {
                "recording_id": recording_id,
                "status": rec_state.status.value,
                "elapsed_seconds": elapsed,
                "expected_duration_seconds": rec_state.expected_duration,
                "progress_percent": progress * 100,
                "remaining_seconds": remaining,
                "filename": rec_state.filename,
                "error": rec_state.error,
            }
    
    def list_iq_recordings(self) -> List[Dict]:
        """List all stored IQ recordings."""
        return self.storage.list_recordings(type_filter="iq")
    
    def get_iq_recording_file(self, filename: str) -> Optional[IQRecording]:
        """Load an IQ recording from storage."""
        from pathlib import Path
        filepath = self.storage.iq_path / filename
        
        if not filepath.exists():
            return None
        
        return self.storage.load_iq_recording(filepath)
    
    def delete_iq_recording(self, filename: str) -> None:
        """Delete an IQ recording file."""
        from pathlib import Path
        filepath = self.storage.iq_path / filename
        self.storage.delete_file(filepath)
    
    # ========================================================================
    # STATUS & DIAGNOSTICS
    # ========================================================================
    
    def get_storage_status(self) -> Dict:
        """Get storage usage information."""
        return self.storage.get_storage_stats()
