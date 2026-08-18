"""
Integration tests for FASE 2A components.

Tests the complete workflow:
- AcquisitionService
- StorageService
- Database
- EventService
"""

import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Import test components
from app.api.schemas.acquisition import (
    AcquisitionMetadata,
    AcquisitionMode,
    IQRecording,
)
from app.services.acquisition_service import AcquisitionService, RecordingStatus
from app.services.storage_service import StorageService
from app.services.event_service import EventService
from app.storage.database import Database


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def storage_service(temp_storage_dir):
    """Create StorageService with temporary directory."""
    return StorageService(str(temp_storage_dir))


@pytest.fixture
def database(temp_storage_dir):
    """Create Database with temporary file."""
    db_path = temp_storage_dir / "test.db"
    return Database(str(db_path))


@pytest.fixture
def event_service(database):
    """Create EventService with test database."""
    return EventService(database)


@pytest.fixture
def mock_device():
    """Create mock BB60C device."""
    device = Mock()
    device.handle = 12345
    device.get_device_info.return_value = Mock(
        serial_number=123456,
        firmware_version="3.2.1"
    )
    device.get_diagnostics.return_value = {
        "temperature_c": 45.2,
        "voltage_5v": 5.0,
    }
    device.get_api_version.return_value = "3.0.0"
    return device


@pytest.fixture
def mock_iq_capture(monkeypatch):
    """Mock BB60CIQCapture."""
    mock_iq = Mock()
    mock_iq.start_iq_capture.return_value = (1000000, 40e6)
    mock_iq.stop_iq_capture.return_value = None
    mock_iq.get_iq_data.return_value = np.zeros(1000000, dtype=np.complex64)
    
    def mock_init(device_handle):
        return mock_iq
    
    monkeypatch.setattr(
        "app.services.acquisition_service.BB60CIQCapture",
        lambda x: mock_iq
    )
    
    return mock_iq


# ============================================================================
# STORAGE SERVICE TESTS
# ============================================================================

class TestStorageService:
    """Test HDF5 storage functionality."""
    
    def test_initialization(self, storage_service):
        """Test storage service initialization."""
        assert storage_service.storage_path.exists()
        assert (storage_service.storage_path / "iq").exists()
        assert (storage_service.storage_path / "sweep").exists()
    
    def test_save_iq_recording(self, storage_service):
        """Test saving IQ recording to HDF5."""
        # Create test recording
        metadata = AcquisitionMetadata(
            timestamp_utc=0,
            device_id="BB60C_SN123456",
            serial_number=123456,
            device_type="BB60C",
            firmware_version="3.2.1",
            api_version="3.0.0",
            center_frequency_hz=1e9,
            span_hz=40e6,
            start_frequency_hz=980e6,
            stop_frequency_hz=1020e6,
            rbw_hz=100e3,
            vbw_hz=100e3,
            reference_level_dbm=0,
            attenuation_db=0,
            detector_type="iq",
            acquisition_mode=AcquisitionMode.IQ,
            sample_rate_sps=40e6,
            sample_count=1000000,
            duration_seconds=25.0,
            sample_loss_detected=False,
        )
        
        iq_data = np.random.randn(1000000) + 1j * np.random.randn(1000000)
        iq_data = iq_data.astype(np.complex64)
        
        recording = IQRecording(
            metadata=metadata,
            iq_data=iq_data,
            sample_count=1000000,
            power_watts=1.0,
            peak_to_average_ratio_db=6.0,
            crest_factor=3.16,
        )
        
        # Save
        filepath = storage_service.save_iq_recording(recording)
        
        # Verify file exists
        assert filepath.exists()
        assert filepath.suffix == ".h5"
        
        # Verify file is readable
        loaded = storage_service.load_iq_recording(filepath)
        assert loaded is not None
        assert loaded.sample_count == 1000000
        assert np.array_equal(loaded.iq_data, iq_data)
    
    def test_list_recordings(self, storage_service):
        """Test listing recordings."""
        # Create and save test recording
        metadata = AcquisitionMetadata(
            timestamp_utc=0,
            device_id="BB60C_SN123456",
            serial_number=123456,
            device_type="BB60C",
            firmware_version="3.2.1",
            api_version="3.0.0",
            center_frequency_hz=1e9,
            span_hz=40e6,
            start_frequency_hz=980e6,
            stop_frequency_hz=1020e6,
            rbw_hz=100e3,
            vbw_hz=100e3,
            reference_level_dbm=0,
            attenuation_db=0,
            detector_type="iq",
            acquisition_mode=AcquisitionMode.IQ,
            sample_rate_sps=40e6,
            sample_count=1000,
            duration_seconds=0.025,
            sample_loss_detected=False,
        )
        
        iq_data = np.zeros(1000, dtype=np.complex64)
        recording = IQRecording(
            metadata=metadata,
            iq_data=iq_data,
            sample_count=1000,
            power_watts=1.0,
            peak_to_average_ratio_db=6.0,
            crest_factor=3.16,
        )
        
        storage_service.save_iq_recording(recording)
        
        # List recordings
        recordings = storage_service.list_recordings(type_filter="iq")
        assert len(recordings) >= 1


# ============================================================================
# DATABASE TESTS
# ============================================================================

class TestDatabase:
    """Test SQLite database functionality."""
    
    def test_initialization(self, database):
        """Test database table creation."""
        stats = database.get_statistics()
        assert stats["total_recordings"] == 0
        assert stats["total_events"] == 0
    
    def test_insert_recording(self, database):
        """Test inserting recording metadata."""
        database.insert_recording(
            recording_id="rec_001",
            filename="recording_001.h5",
            recording_type="iq",
            timestamp_utc=0,
            device_id="BB60C_SN123456",
            device_type="BB60C",
            center_frequency_hz=1e9,
            bandwidth_hz=40e6,
            sample_rate_sps=40e6,
            duration_seconds=25.0,
            sample_count=1000000,
            file_size_bytes=500000000,
        )
        
        # Verify stored
        recording = database.get_recording("rec_001")
        assert recording is not None
        assert recording["filename"] == "recording_001.h5"
        assert recording["device_id"] == "BB60C_SN123456"
    
    def test_insert_event(self, database):
        """Test inserting events."""
        event_id = database.insert_event(
            event_type="recording_started",
            timestamp_utc=0,
            recording_id="rec_001",
            data={
                "duration": 25.0,
                "frequency": 1e9,
            }
        )
        
        assert event_id > 0
        
        events = database.get_recent_events()
        assert len(events) > 0
        assert events[0]["event_type"] == "recording_started"
    
    def test_delete_recording(self, database):
        """Test deleting recording."""
        database.insert_recording(
            recording_id="rec_001",
            filename="recording_001.h5",
            recording_type="iq",
            timestamp_utc=0,
            device_id="BB60C_SN123456",
            device_type="BB60C",
        )
        
        # Delete
        database.delete_recording("rec_001")
        
        # Verify deleted
        recording = database.get_recording("rec_001")
        assert recording is None


# ============================================================================
# EVENT SERVICE TESTS
# ============================================================================

class TestEventService:
    """Test event logging functionality."""
    
    def test_log_recording_started(self, event_service):
        """Test logging recording start."""
        event_id = event_service.log_recording_started(
            recording_id="rec_001",
            center_frequency_hz=1e9,
            bandwidth_hz=40e6,
            sample_rate_sps=40e6,
            duration_seconds=25.0,
            operator_name="Test Operator",
        )
        
        assert event_id > 0
    
    def test_get_events_for_recording(self, event_service):
        """Test retrieving events for a recording."""
        recording_id = "rec_001"
        
        event_service.log_recording_started(
            recording_id=recording_id,
            center_frequency_hz=1e9,
            bandwidth_hz=40e6,
            sample_rate_sps=40e6,
            duration_seconds=25.0,
        )
        
        event_service.log_file_saved(
            recording_id=recording_id,
            filename="recording_001.h5",
            file_size_bytes=500000000,
            file_hash="abc123",
        )
        
        events = event_service.get_events_for_recording(recording_id)
        assert len(events) == 2


# ============================================================================
# ACQUISITION SERVICE TESTS
# ============================================================================

class TestAcquisitionService:
    """Test high-level acquisition service."""
    
    def test_start_iq_recording(self, mock_device, mock_iq_capture, storage_service):
        """Test starting IQ recording."""
        acq_service = AcquisitionService(mock_device, storage_service)
        
        recording_id = acq_service.start_iq_recording(
            center_frequency_hz=1e9,
            bandwidth_hz=40e6,
            sample_rate_sps=40e6,
            duration_seconds=25.0,
        )
        
        assert recording_id is not None
        assert len(recording_id) == 8
    
    def test_get_recording_status(self, mock_device, mock_iq_capture, storage_service):
        """Test getting recording status."""
        acq_service = AcquisitionService(mock_device, storage_service)
        
        recording_id = acq_service.start_iq_recording(
            center_frequency_hz=1e9,
            bandwidth_hz=40e6,
            sample_rate_sps=40e6,
            duration_seconds=25.0,
        )
        
        status = acq_service.get_iq_recording_status(recording_id)
        
        assert status["recording_id"] == recording_id
        assert status["status"] == "recording"
        assert "elapsed_seconds" in status
