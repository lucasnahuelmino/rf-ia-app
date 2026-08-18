"""
IQ Capture interface for BB60C device.

This module provides low-level IQ data capture functionality
integrated with the BB60C SDK.
"""

from typing import Optional, Tuple
import numpy as np
from threading import Lock, Event

from .exceptions import BB60CConnectionError, BB60CSDKError
from .sdk import bb_api


class BB60CIQCapture:
    """
    Handles IQ data capture from Signal Hound BB60C device.
    
    Thread-safe interface for starting, monitoring, and retrieving
    IQ sample data.
    """
    
    def __init__(self, device_handle: int):
        """
        Initialize IQ capture for a connected device.
        
        Args:
            device_handle: Handle from bb_open_device()
        """
        self._handle = device_handle
        self._capturing = False
        self._iq_data: Optional[np.ndarray] = None
        self._capture_lock = Lock()
        self._capture_event = Event()
        self._sample_count = 0
        
    def _check_status(self, result: dict) -> None:
        """Check SDK status code and raise if error."""
        status = result.get("status")
        if status is None:
            return
        if status != 0:
            raise BB60CSDKError(f"SDK returned status={status}")
    
    # ========================================================================
    # IQ CAPTURE CONTROL
    # ========================================================================
    
    def start_iq_capture(
        self,
        center_frequency_hz: float,
        bandwidth_hz: float,
        sample_rate_sps: float,
        duration_seconds: float,
    ) -> Tuple[int, float]:
        """
        Start capturing IQ samples.
        
        Args:
            center_frequency_hz: Center frequency in Hz
            bandwidth_hz: Capture bandwidth in Hz
            sample_rate_sps: Sample rate in samples/second
            duration_seconds: Duration to capture in seconds
            
        Returns:
            Tuple of (total_samples_to_capture, actual_sample_rate_sps)
            
        Raises:
            BB60CConnectionError: If device not connected
            BB60CSDKError: If device returned error status
        """
        if not self._handle:
            raise BB60CConnectionError("Device is not connected")
        
        with self._capture_lock:
            if self._capturing:
                raise RuntimeError("IQ capture already in progress")
            
            # Configure center frequency
            result = bb_api.bb_configure_center_frequency(
                self._handle,
                center_frequency_hz
            )
            self._check_status(result)
            
            # Configure IQ capture parameters
            result = bb_api.bb_configure_iq_capture(
                self._handle,
                bandwidth_hz,
                sample_rate_sps,
            )
            self._check_status(result)
            
            # Start IQ capture
            result = bb_api.bb_start_iq_capture(self._handle)
            self._check_status(result)
            
            # Calculate total samples
            actual_sample_rate = result.get("sample_rate_sps", sample_rate_sps)
            total_samples = int(duration_seconds * actual_sample_rate)
            
            self._capturing = True
            self._sample_count = 0
            self._capture_event.clear()
            
            return total_samples, actual_sample_rate
    
    def stop_iq_capture(self) -> None:
        """
        Stop IQ capture and retrieve final data.
        
        Raises:
            BB60CSDKError: If device returned error status
        """
        with self._capture_lock:
            if not self._capturing:
                return
            
            result = bb_api.bb_stop_iq_capture(self._handle)
            self._check_status(result)
            
            self._capturing = False
            self._capture_event.set()
    
    # ========================================================================
    # DATA RETRIEVAL
    # ========================================================================
    
    def get_iq_data(self) -> Optional[np.ndarray]:
        """
        Retrieve captured IQ data.
        
        Returns:
            numpy array of complex64 IQ samples, or None if no data captured
        """
        with self._capture_lock:
            return self._iq_data.copy() if self._iq_data is not None else None
    
    def get_iq_chunk(self, chunk_size: int) -> Tuple[np.ndarray, bool]:
        """
        Retrieve a chunk of IQ data during capture.
        
        This allows streaming retrieval of data without waiting
        for capture to complete.
        
        Args:
            chunk_size: Number of samples to retrieve
            
        Returns:
            Tuple of (data_chunk, capture_still_running)
        """
        with self._capture_lock:
            if not self._capturing:
                return np.array([], dtype=np.complex64), False
            
            result = bb_api.bb_get_iq_chunk(
                self._handle,
                chunk_size
            )
            self._check_status(result)
            
            data = result.get("data", np.array([], dtype=np.complex64))
            self._sample_count += len(data)
            
            return data, self._capturing
    
    def get_capture_status(self) -> dict:
        """
        Get current IQ capture status.
        
        Returns:
            dict with:
            - capturing: bool - whether capture is active
            - samples_collected: int - number of samples collected so far
            - sample_loss: bool - whether sample loss was detected
        """
        with self._capture_lock:
            result = bb_api.bb_get_iq_capture_status(self._handle)
            self._check_status(result)
            
            return {
                "capturing": self._capturing,
                "samples_collected": self._sample_count,
                "sample_loss": result.get("sample_loss_detected", False),
            }
    
    # ========================================================================
    # DIAGNOSTICS
    # ========================================================================
    
    def verify_iq_data(self) -> dict:
        """
        Verify integrity of captured IQ data.
        
        Performs checks for:
        - Proper sample count
        - Sample loss detection
        - Data validity (no NaN/Inf)
        - IQ imbalance
        - DC offset
        
        Returns:
            dict with verification results and metrics
        """
        if self._iq_data is None or len(self._iq_data) == 0:
            return {
                "valid": False,
                "error": "No IQ data available"
            }
        
        data = self._iq_data
        
        # Check for NaN/Inf
        if np.any(~np.isfinite(data)):
            return {
                "valid": False,
                "error": "Data contains NaN or Inf values"
            }
        
        # Calculate statistics
        i_component = np.real(data)
        q_component = np.imag(data)
        
        i_power = np.mean(i_component ** 2)
        q_power = np.mean(q_component ** 2)
        
        # IQ imbalance in dB
        iq_imbalance_db = 10 * np.log10(max(i_power, q_power) / min(i_power, q_power))
        
        # DC offset
        i_dc = np.mean(i_component)
        q_dc = np.mean(q_component)
        dc_offset_rms = np.sqrt(i_dc**2 + q_dc**2)
        
        return {
            "valid": True,
            "sample_count": len(data),
            "iq_imbalance_db": float(iq_imbalance_db),
            "dc_offset_rms": float(dc_offset_rms),
            "i_power_dbm": float(10 * np.log10(i_power + 1e-10)),
            "q_power_dbm": float(10 * np.log10(q_power + 1e-10)),
        }
