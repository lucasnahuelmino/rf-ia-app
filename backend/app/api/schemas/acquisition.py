"""
Schemas for RF acquisition data (Spectrum, IQ recordings).

This module defines Pydantic models for:
- Acquisition metadata (common to all acquisition modes)
- Spectrum snapshots (sweep data)
- IQ recordings (complex data)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum
import numpy as np


# ============================================================================
# ENUMS
# ============================================================================

class AcquisitionMode(str, Enum):
    """Type of acquisition being performed."""
    SWEEP = "sweep"
    IQ = "iq"


class DetectorType(str, Enum):
    """Detector type used for measurement."""
    AVERAGE = "average"
    PEAK = "peak"
    MIN = "min"
    MAX = "max"


class Environment(str, Enum):
    """Physical environment of measurement."""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    MOBILE = "mobile"
    LABORATORY = "laboratory"


# ============================================================================
# ACQUISITION METADATA
# ============================================================================

@dataclass
class AcquisitionMetadata:
    """
    Common metadata for any RF acquisition.
    
    Contains all configuration parameters captured at moment of acquisition
    plus device information, location data, and quality metrics.
    """
    
    # ---- TEMPORAL ----
    timestamp_utc: float                    # Unix timestamp (UTC) when acquisition started
    
    # ---- DEVICE INFO ----
    device_id: str                          # e.g., "BB60C_SN123456"
    serial_number: int                      # Device serial number
    device_type: str                        # "BB60C", "BB60D", etc.
    firmware_version: str                   # e.g., "v3.2.1"
    api_version: str                        # e.g., "3.0.0"
    
    # ---- RF CONFIGURATION ----
    center_frequency_hz: float              # Center frequency in Hz
    span_hz: float                          # Span in Hz (for sweep or IQ bandwidth)
    start_frequency_hz: float               # Start frequency in Hz
    stop_frequency_hz: float                # Stop frequency in Hz
    rbw_hz: float                           # Resolution bandwidth in Hz
    vbw_hz: float                           # Video bandwidth in Hz
    reference_level_dbm: float              # Reference level in dBm
    attenuation_db: float                   # Attenuation in dB (if applicable)
    detector_type: str                      # Detector type (AVERAGE, PEAK, MIN, MAX)
    
    # ---- ACQUISITION TYPE & MODE ----
    acquisition_mode: AcquisitionMode       # SWEEP or IQ
    sample_rate_sps: Optional[float]        # Sample rate in samples/sec (for IQ)
    sample_count: Optional[int]             # Total samples (for IQ)
    duration_seconds: Optional[float]       # Duration in seconds
    
    # ---- LOCATION (Future GPS) ----
    gps_latitude: Optional[float]           # Latitude (-90 to +90)
    gps_longitude: Optional[float]          # Longitude (-180 to +180)
    gps_altitude_m: Optional[float]         # Altitude in meters
    gps_timestamp: Optional[float]          # GPS timestamp (Unix)
    location_name: Optional[str]            # Human-readable location name
    
    # ---- ADDITIONAL METADATA ----
    operator_name: Optional[str]            # Person who performed measurement
    notes: Optional[str]                    # Free-form notes
    environment: Optional[Environment]      # Physical environment
    
    # ---- DATA QUALITY METRICS ----
    sample_loss_detected: bool              # Whether sample loss was detected
    iq_imbalance_db: Optional[float]        # IQ imbalance in dB (for IQ mode)
    dc_offset: Optional[float]              # DC offset (for IQ mode)
    frequency_error_hz: Optional[float]     # Frequency error estimate in Hz
    
    # ---- FILE INFORMATION ----
    file_hash: Optional[str]                # SHA256 of file data
    file_format: Optional[str]              # "HDF5", "NPZ", "WAV", etc.
    file_size_bytes: Optional[int]          # File size in bytes
    compression: Optional[str]              # Compression type ("gzip", "lz4", None)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp_utc": self.timestamp_utc,
            "device_id": self.device_id,
            "serial_number": self.serial_number,
            "device_type": self.device_type,
            "firmware_version": self.firmware_version,
            "api_version": self.api_version,
            "center_frequency_hz": self.center_frequency_hz,
            "span_hz": self.span_hz,
            "start_frequency_hz": self.start_frequency_hz,
            "stop_frequency_hz": self.stop_frequency_hz,
            "rbw_hz": self.rbw_hz,
            "vbw_hz": self.vbw_hz,
            "reference_level_dbm": self.reference_level_dbm,
            "attenuation_db": self.attenuation_db,
            "detector_type": self.detector_type,
            "acquisition_mode": self.acquisition_mode.value,
            "sample_rate_sps": self.sample_rate_sps,
            "sample_count": self.sample_count,
            "duration_seconds": self.duration_seconds,
            "gps_latitude": self.gps_latitude,
            "gps_longitude": self.gps_longitude,
            "gps_altitude_m": self.gps_altitude_m,
            "gps_timestamp": self.gps_timestamp,
            "location_name": self.location_name,
            "operator_name": self.operator_name,
            "notes": self.notes,
            "environment": self.environment.value if self.environment else None,
            "sample_loss_detected": self.sample_loss_detected,
            "iq_imbalance_db": self.iq_imbalance_db,
            "dc_offset": self.dc_offset,
            "frequency_error_hz": self.frequency_error_hz,
            "file_hash": self.file_hash,
            "file_format": self.file_format,
            "file_size_bytes": self.file_size_bytes,
            "compression": self.compression,
        }


# ============================================================================
# SPECTRUM SNAPSHOT (SWEEP MODE)
# ============================================================================

@dataclass
class SpectrumSnapshot:
    """
    Instantaneous spectrum data (sweep acquisition).
    
    Contains power vs frequency data plus derived metrics.
    Inherits metadata from AcquisitionMetadata.
    """
    
    # Metadata from acquisition
    metadata: AcquisitionMetadata
    
    # ---- TRACE DATA ----
    trace: List[float]                      # Power values in dBm (one per bin)
    trace_length: int                       # Number of points in trace
    bin_size_hz: float                      # Frequency width of each bin
    
    # ---- DERIVED METRICS ----
    peak_frequency_hz: float                # Frequency of maximum power
    peak_power_dbm: float                   # Maximum power value
    noise_floor_dbm: float                  # Estimated noise floor
    occupied_bandwidth_hz: float            # Occupied bandwidth
    
    # ---- OPTIONAL ADDITIONAL TRACES ----
    max_hold: Optional[List[float]]         # Max-hold trace
    min_hold: Optional[List[float]]         # Min-hold trace
    average_trace: Optional[List[float]]    # Averaged trace
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": self.metadata.to_dict(),
            "trace": self.trace,
            "trace_length": self.trace_length,
            "bin_size_hz": self.bin_size_hz,
            "peak_frequency_hz": self.peak_frequency_hz,
            "peak_power_dbm": self.peak_power_dbm,
            "noise_floor_dbm": self.noise_floor_dbm,
            "occupied_bandwidth_hz": self.occupied_bandwidth_hz,
            "max_hold": self.max_hold,
            "min_hold": self.min_hold,
            "average_trace": self.average_trace,
        }


# ============================================================================
# IQ RECORDING (IQ MODE)
# ============================================================================

@dataclass
class IQRecording:
    """
    Complex IQ data capture.
    
    Contains I/Q sample pairs plus quality metrics and derived statistics.
    Data is stored as serialized numpy array (typically complex64).
    """
    
    # Metadata from acquisition
    metadata: AcquisitionMetadata
    
    # ---- IQ DATA ----
    iq_data: np.ndarray                     # Shape (N,) array of complex64
    sample_count: int                       # Number of IQ samples
    
    # ---- POWER STATISTICS ----
    power_watts: float                      # Average power in watts
    peak_to_average_ratio_db: float         # PAR in dB
    crest_factor: float                     # Crest factor
    
    # ---- OPTIONAL DETECTOR TRACES ----
    detector_min: Optional[np.ndarray]      # Min detector values
    detector_max: Optional[np.ndarray]      # Max detector values
    detector_avg: Optional[np.ndarray]      # Average detector values
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization (without iq_data)."""
        return {
            "metadata": self.metadata.to_dict(),
            "sample_count": self.sample_count,
            "power_watts": self.power_watts,
            "peak_to_average_ratio_db": self.peak_to_average_ratio_db,
            "crest_factor": self.crest_factor,
        }


# ============================================================================
# API REQUEST/RESPONSE SCHEMAS
# ============================================================================

@dataclass
class IQRecordingStartRequest:
    """Request to start IQ recording."""
    center_frequency_hz: float
    bandwidth_hz: float
    sample_rate_sps: float
    duration_seconds: float
    location_name: Optional[str] = None
    operator_name: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class IQRecordingStartResponse:
    """Response when starting IQ recording."""
    recording_id: str
    status: str                             # "recording"
    timestamp_utc: float
    estimated_file_size_gb: float


@dataclass
class IQRecordingStatusResponse:
    """Status of ongoing IQ recording."""
    recording_id: str
    status: str                             # "recording", "stopped", "saved"
    elapsed_seconds: float
    estimated_remaining_seconds: Optional[float]
    file_size_mb: Optional[float]


@dataclass
class RecordingListResponse:
    """List of available recordings."""
    recordings: List[Dict]
    total_count: int
    storage_used_gb: float
