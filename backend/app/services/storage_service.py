"""
Storage service for RF acquisition data.

Handles persistent storage of spectrum snapshots and IQ recordings
to disk in HDF5 format with compression and metadata.
"""

import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import h5py
import numpy as np

from app.api.schemas.acquisition import (
    SpectrumSnapshot,
    IQRecording,
    AcquisitionMetadata,
)


class StorageService:
    """
    Manages storage of RF acquisition data.
    
    Stores data in HDF5 format with:
    - Lossless GZIP compression
    - Embedded metadata
    - SHA256 checksums
    - Organized file structure
    """
    
    def __init__(self, storage_path: str = "./data/recordings"):
        """
        Initialize storage service.
        
        Args:
            storage_path: Root directory for all recordings
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.iq_path = self.storage_path / "iq"
        self.sweep_path = self.storage_path / "sweep"
        self.iq_path.mkdir(exist_ok=True)
        self.sweep_path.mkdir(exist_ok=True)
    
    # ========================================================================
    # IQ RECORDING STORAGE
    # ========================================================================
    
    def save_iq_recording(
        self,
        recording: IQRecording,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Save IQ recording to HDF5 file.
        
        Args:
            recording: IQRecording object
            filename: Custom filename (without extension), defaults to timestamp-based
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"iq_{timestamp}"
        
        filepath = self.iq_path / f"{filename}.h5"
        
        # Ensure unique filename
        counter = 1
        base_path = filepath
        while filepath.exists():
            filepath = self.iq_path / f"{filename}_{counter}.h5"
            counter += 1
        
        # Save to HDF5
        with h5py.File(filepath, "w") as f:
            # Store IQ data with compression
            f.create_dataset(
                "iq_data",
                data=recording.iq_data,
                compression="gzip",
                compression_opts=4,  # Balance compression vs speed
            )
            
            # Store metadata
            meta_group = f.create_group("metadata")
            meta_dict = recording.metadata.to_dict()
            
            for key, value in meta_dict.items():
                if isinstance(value, (str, int, float, bool)):
                    meta_group.attrs[key] = value
                elif value is None:
                    meta_group.attrs[key] = "None"
            
            # Store quality metrics
            quality_group = f.create_group("quality")
            quality_group.attrs["power_watts"] = recording.power_watts
            quality_group.attrs["peak_to_average_ratio_db"] = recording.peak_to_average_ratio_db
            quality_group.attrs["crest_factor"] = recording.crest_factor
            
            # Store optional detector data
            if recording.detector_min is not None:
                quality_group.create_dataset("detector_min", data=recording.detector_min)
            if recording.detector_max is not None:
                quality_group.create_dataset("detector_max", data=recording.detector_max)
            if recording.detector_avg is not None:
                quality_group.create_dataset("detector_avg", data=recording.detector_avg)
        
        # Compute and update file hash
        file_hash = self._compute_file_hash(filepath)
        
        # Update file with hash
        with h5py.File(filepath, "r+") as f:
            f["metadata"].attrs["file_hash"] = file_hash
        
        print(f"[StorageService] Saved IQ recording: {filepath}")
        return filepath
    
    def load_iq_recording(self, filepath: Path) -> IQRecording:
        """
        Load IQ recording from HDF5 file.
        
        Args:
            filepath: Path to HDF5 file
            
        Returns:
            IQRecording object
        """
        with h5py.File(filepath, "r") as f:
            # Load IQ data
            iq_data = np.array(f["iq_data"], dtype=np.complex64)
            
            # Load metadata
            meta_attrs = dict(f["metadata"].attrs)
            
            # Create metadata object
            metadata = AcquisitionMetadata(
                timestamp_utc=float(meta_attrs.get("timestamp_utc", 0)),
                device_id=str(meta_attrs.get("device_id", "Unknown")),
                serial_number=int(meta_attrs.get("serial_number", 0)),
                device_type=str(meta_attrs.get("device_type", "Unknown")),
                firmware_version=str(meta_attrs.get("firmware_version", "")),
                api_version=str(meta_attrs.get("api_version", "")),
                center_frequency_hz=float(meta_attrs.get("center_frequency_hz", 0)),
                span_hz=float(meta_attrs.get("span_hz", 0)),
                start_frequency_hz=float(meta_attrs.get("start_frequency_hz", 0)),
                stop_frequency_hz=float(meta_attrs.get("stop_frequency_hz", 0)),
                rbw_hz=float(meta_attrs.get("rbw_hz", 0)),
                vbw_hz=float(meta_attrs.get("vbw_hz", 0)),
                reference_level_dbm=float(meta_attrs.get("reference_level_dbm", 0)),
                attenuation_db=float(meta_attrs.get("attenuation_db", 0)),
                detector_type=str(meta_attrs.get("detector_type", "average")),
                acquisition_mode=str(meta_attrs.get("acquisition_mode", "iq")),
                sample_rate_sps=meta_attrs.get("sample_rate_sps"),
                sample_count=int(meta_attrs.get("sample_count", len(iq_data))),
                duration_seconds=meta_attrs.get("duration_seconds"),
            )
            
            # Load quality metrics
            quality_attrs = dict(f["quality"].attrs)
            power_watts = float(quality_attrs.get("power_watts", 0))
            par_db = float(quality_attrs.get("peak_to_average_ratio_db", 0))
            crest = float(quality_attrs.get("crest_factor", 0))
            
            # Load optional detector data
            detector_min = np.array(f["quality"]["detector_min"]) if "detector_min" in f["quality"] else None
            detector_max = np.array(f["quality"]["detector_max"]) if "detector_max" in f["quality"] else None
            detector_avg = np.array(f["quality"]["detector_avg"]) if "detector_avg" in f["quality"] else None
            
            return IQRecording(
                metadata=metadata,
                iq_data=iq_data,
                sample_count=len(iq_data),
                power_watts=power_watts,
                peak_to_average_ratio_db=par_db,
                crest_factor=crest,
                detector_min=detector_min,
                detector_max=detector_max,
                detector_avg=detector_avg,
            )
    
    # ========================================================================
    # SWEEP STORAGE
    # ========================================================================
    
    def save_sweep_snapshot(
        self,
        snapshot: SpectrumSnapshot,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Save spectrum snapshot to HDF5 file.
        
        Args:
            snapshot: SpectrumSnapshot object
            filename: Custom filename, defaults to timestamp-based
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"sweep_{timestamp}"
        
        filepath = self.sweep_path / f"{filename}.h5"
        
        with h5py.File(filepath, "w") as f:
            # Store trace
            f.create_dataset("trace", data=snapshot.trace, compression="gzip")
            
            # Store metadata
            meta_group = f.create_group("metadata")
            meta_dict = snapshot.metadata.to_dict()
            for key, value in meta_dict.items():
                if isinstance(value, (str, int, float, bool)):
                    meta_group.attrs[key] = value
                elif value is None:
                    meta_group.attrs[key] = "None"
            
            # Store derived metrics
            metrics_group = f.create_group("metrics")
            metrics_group.attrs["peak_frequency_hz"] = snapshot.peak_frequency_hz
            metrics_group.attrs["peak_power_dbm"] = snapshot.peak_power_dbm
            metrics_group.attrs["noise_floor_dbm"] = snapshot.noise_floor_dbm
            metrics_group.attrs["occupied_bandwidth_hz"] = snapshot.occupied_bandwidth_hz
            
            # Store optional traces
            if snapshot.max_hold is not None:
                metrics_group.create_dataset("max_hold", data=snapshot.max_hold)
            if snapshot.min_hold is not None:
                metrics_group.create_dataset("min_hold", data=snapshot.min_hold)
            if snapshot.average_trace is not None:
                metrics_group.create_dataset("average_trace", data=snapshot.average_trace)
        
        return filepath
    
    def load_sweep_snapshot(self, filepath: Path) -> SpectrumSnapshot:
        """Load sweep snapshot from HDF5 file."""
        with h5py.File(filepath, "r") as f:
            trace = list(f["trace"])
            meta_attrs = dict(f["metadata"].attrs)
            metrics_attrs = dict(f["metrics"].attrs)
            
            # Create metadata
            from app.api.schemas.acquisition import AcquisitionMode
            metadata = AcquisitionMetadata(
                timestamp_utc=float(meta_attrs.get("timestamp_utc", 0)),
                device_id=str(meta_attrs.get("device_id", "Unknown")),
                serial_number=int(meta_attrs.get("serial_number", 0)),
                device_type=str(meta_attrs.get("device_type", "Unknown")),
                firmware_version=str(meta_attrs.get("firmware_version", "")),
                api_version=str(meta_attrs.get("api_version", "")),
                center_frequency_hz=float(meta_attrs.get("center_frequency_hz", 0)),
                span_hz=float(meta_attrs.get("span_hz", 0)),
                start_frequency_hz=float(meta_attrs.get("start_frequency_hz", 0)),
                stop_frequency_hz=float(meta_attrs.get("stop_frequency_hz", 0)),
                rbw_hz=float(meta_attrs.get("rbw_hz", 0)),
                vbw_hz=float(meta_attrs.get("vbw_hz", 0)),
                reference_level_dbm=float(meta_attrs.get("reference_level_dbm", 0)),
                attenuation_db=float(meta_attrs.get("attenuation_db", 0)),
                detector_type=str(meta_attrs.get("detector_type", "average")),
                acquisition_mode=AcquisitionMode.SWEEP,
            )
            
            max_hold = list(f["metrics"]["max_hold"]) if "max_hold" in f["metrics"] else None
            min_hold = list(f["metrics"]["min_hold"]) if "min_hold" in f["metrics"] else None
            avg_trace = list(f["metrics"]["average_trace"]) if "average_trace" in f["metrics"] else None
            
            return SpectrumSnapshot(
                metadata=metadata,
                trace=trace,
                trace_length=len(trace),
                bin_size_hz=float(meta_attrs.get("bin_size_hz", 0)),
                peak_frequency_hz=float(metrics_attrs.get("peak_frequency_hz", 0)),
                peak_power_dbm=float(metrics_attrs.get("peak_power_dbm", 0)),
                noise_floor_dbm=float(metrics_attrs.get("noise_floor_dbm", 0)),
                occupied_bandwidth_hz=float(metrics_attrs.get("occupied_bandwidth_hz", 0)),
                max_hold=max_hold,
                min_hold=min_hold,
                average_trace=avg_trace,
            )
    
    # ========================================================================
    # FILE MANAGEMENT
    # ========================================================================
    
    def list_recordings(self, type_filter: str = "all") -> List[Dict]:
        """
        List all stored recordings.
        
        Args:
            type_filter: "iq", "sweep", or "all"
            
        Returns:
            List of recording dictionaries with metadata
        """
        recordings = []
        
        paths = []
        if type_filter in ["iq", "all"]:
            paths.extend(self.iq_path.glob("*.h5"))
        if type_filter in ["sweep", "all"]:
            paths.extend(self.sweep_path.glob("*.h5"))
        
        for filepath in sorted(paths, reverse=True):
            try:
                with h5py.File(filepath, "r") as f:
                    meta_attrs = dict(f["metadata"].attrs)
                    recordings.append({
                        "filename": filepath.name,
                        "path": str(filepath),
                        "type": "iq" if "/iq/" in str(filepath) else "sweep",
                        "timestamp": float(meta_attrs.get("timestamp_utc", 0)),
                        "size_mb": filepath.stat().st_size / (1024 * 1024),
                        "center_freq_hz": float(meta_attrs.get("center_frequency_hz", 0)),
                    })
            except Exception as e:
                print(f"[StorageService] Error reading {filepath}: {e}")
        
        return recordings
    
    def delete_file(self, filepath: Path) -> None:
        """Delete a recording file."""
        filepath.unlink(missing_ok=True)
        print(f"[StorageService] Deleted: {filepath}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage usage statistics."""
        total_size = 0
        iq_count = 0
        sweep_count = 0
        
        for f in self.iq_path.glob("*.h5"):
            total_size += f.stat().st_size
            iq_count += 1
        
        for f in self.sweep_path.glob("*.h5"):
            total_size += f.stat().st_size
            sweep_count += 1
        
        return {
            "total_size_gb": total_size / (1024 ** 3),
            "iq_recordings": iq_count,
            "sweep_recordings": sweep_count,
            "storage_path": str(self.storage_path),
        }
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    @staticmethod
    def _compute_file_hash(filepath: Path, algorithm: str = "sha256") -> str:
        """Compute hash of file contents."""
        hash_obj = hashlib.new(algorithm)
        
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
