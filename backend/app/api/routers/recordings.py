"""
API Router for IQ recordings and acquisition.

Endpoints for starting, stopping, and managing IQ recordings.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
import time

from app.api.schemas.acquisition import (
    IQRecordingStartRequest,
    IQRecordingStartResponse,
    IQRecordingStatusResponse,
    RecordingListResponse,
)
from app.services.acquisition_service import AcquisitionService
from app.services.event_service import EventService
from app.devices.bb60c.adapter import BB60CAdapter
from app.storage.database import Database


# Global instances (will be injected properly in main.py)
acquisition_service: Optional[AcquisitionService] = None
event_service: Optional[EventService] = None

router = APIRouter(prefix="/recordings", tags=["recordings"])


# ============================================================================
# DEPENDENCY INJECTION (will be set by main.py)
# ============================================================================

def set_services(acq_svc: AcquisitionService, evt_svc: EventService):
    """Set service instances (called from main.py)."""
    global acquisition_service, event_service
    acquisition_service = acq_svc
    event_service = evt_svc


# ============================================================================
# IQ RECORDING ENDPOINTS
# ============================================================================

@router.post("/iq/start", response_model=IQRecordingStartResponse)
async def start_iq_recording(request: IQRecordingStartRequest):
    """
    Start a new IQ recording session.
    
    Parameters:
    - center_frequency_hz: Center frequency in Hz
    - bandwidth_hz: Capture bandwidth in Hz
    - sample_rate_sps: Sample rate in samples/second
    - duration_seconds: How long to record (seconds)
    - location_name: Optional location description
    - operator_name: Optional operator name
    - notes: Optional notes
    
    Returns: Recording ID and estimated file size
    """
    if acquisition_service is None:
        raise HTTPException(status_code=500, detail="Acquisition service not initialized")
    
    try:
        recording_id = acquisition_service.start_iq_recording(
            center_frequency_hz=request.center_frequency_hz,
            bandwidth_hz=request.bandwidth_hz,
            sample_rate_sps=request.sample_rate_sps,
            duration_seconds=request.duration_seconds,
            location_name=request.location_name,
            operator_name=request.operator_name,
            notes=request.notes,
        )
        
        # Log event
        if event_service:
            event_service.log_recording_started(
                recording_id=recording_id,
                center_frequency_hz=request.center_frequency_hz,
                bandwidth_hz=request.bandwidth_hz,
                sample_rate_sps=request.sample_rate_sps,
                duration_seconds=request.duration_seconds,
                operator_name=request.operator_name,
            )
        
        # Estimate file size
        sample_count = int(request.duration_seconds * request.sample_rate_sps)
        iq_bytes_per_sample = 8  # 4 bytes I + 4 bytes Q
        uncompressed_size = sample_count * iq_bytes_per_sample
        estimated_compressed = uncompressed_size * 0.5 / (1024**3)  # ~50% compression with gzip
        
        return IQRecordingStartResponse(
            recording_id=recording_id,
            status="recording",
            timestamp_utc=time.time(),
            estimated_file_size_gb=estimated_compressed,
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to start recording: {str(e)}")


@router.post("/iq/stop")
async def stop_iq_recording(recording_id: str, background_tasks: BackgroundTasks):
    """
    Stop an IQ recording and save to disk.
    
    Parameters:
    - recording_id: Recording ID from start_iq_recording
    
    Returns: File path where recording was saved
    """
    if acquisition_service is None:
        raise HTTPException(status_code=500, detail="Acquisition service not initialized")
    
    try:
        filepath = acquisition_service.stop_iq_recording(recording_id)
        
        # Log event
        if event_service:
            status = acquisition_service.get_iq_recording_status(recording_id)
            event_service.log_recording_stopped(
                recording_id=recording_id,
                actual_duration_seconds=status["elapsed_seconds"],
                sample_count=status.get("sample_count", 0),
            )
        
        return {
            "status": "success",
            "recording_id": recording_id,
            "file_path": filepath,
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to stop recording: {str(e)}")


@router.get("/iq/{recording_id}/status", response_model=IQRecordingStatusResponse)
async def get_iq_recording_status(recording_id: str):
    """
    Get status of an ongoing or completed IQ recording.
    
    Returns: Current status, elapsed time, progress, etc.
    """
    if acquisition_service is None:
        raise HTTPException(status_code=500, detail="Acquisition service not initialized")
    
    try:
        status = acquisition_service.get_iq_recording_status(recording_id)
        
        return IQRecordingStatusResponse(
            recording_id=recording_id,
            status=status["status"],
            elapsed_seconds=status["elapsed_seconds"],
            estimated_remaining_seconds=status.get("remaining_seconds"),
            file_size_mb=None,  # Will be filled after save
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=RecordingListResponse)
async def list_recordings(recording_type: Optional[str] = None, limit: int = 100):
    """
    List all recordings.
    
    Parameters:
    - recording_type: Filter by type ("iq", "sweep", or None for all)
    - limit: Maximum number to return
    
    Returns: List of recordings with metadata
    """
    if acquisition_service is None:
        raise HTTPException(status_code=500, detail="Acquisition service not initialized")
    
    try:
        recordings = acquisition_service.list_iq_recordings()
        
        storage_stats = acquisition_service.get_storage_status()
        
        return RecordingListResponse(
            recordings=recordings[:limit],
            total_count=len(recordings),
            storage_used_gb=storage_stats["total_size_gb"],
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{filename}")
async def get_recording_metadata(filename: str):
    """
    Get metadata for a specific recording file.
    
    Returns: Recording metadata and file information
    """
    if acquisition_service is None:
        raise HTTPException(status_code=500, detail="Acquisition service not initialized")
    
    try:
        recording = acquisition_service.get_iq_recording_file(filename)
        
        if recording is None:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        return {
            "filename": filename,
            "metadata": recording.metadata.to_dict(),
            "sample_count": recording.sample_count,
            "power_watts": recording.power_watts,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{filename}")
async def delete_recording(filename: str):
    """
    Delete a recording file.
    
    Parameters:
    - filename: Filename to delete
    
    Returns: Confirmation message
    """
    if acquisition_service is None:
        raise HTTPException(status_code=500, detail="Acquisition service not initialized")
    
    try:
        acquisition_service.delete_iq_recording(filename)
        
        return {
            "status": "deleted",
            "filename": filename,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_acquisition_status():
    """
    Get overall acquisition system status.
    
    Returns: Storage statistics, system health, etc.
    """
    if acquisition_service is None:
        raise HTTPException(status_code=500, detail="Acquisition service not initialized")
    
    try:
        storage_stats = acquisition_service.get_storage_status()
        
        return {
            "status": "ok",
            "storage": storage_stats,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
