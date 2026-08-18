"""
Event logging service.

Tracks and logs all important events in the system:
- Recording started/stopped
- File saved
- Data quality issues
- Predictions
- etc.
"""

import time
from typing import Dict, Optional
from app.storage.database import Database


class EventService:
    """
    Centralized event logging service.
    
    All significant system events are logged here for:
    - Audit trail
    - Debugging
    - Analysis
    - User visibility
    """
    
    def __init__(self, database: Database):
        """
        Initialize event service.
        
        Args:
            database: Database instance for persistence
        """
        self.database = database
    
    # ========================================================================
    # RECORDING EVENTS
    # ========================================================================
    
    def log_recording_started(
        self,
        recording_id: str,
        center_frequency_hz: float,
        bandwidth_hz: float,
        sample_rate_sps: float,
        duration_seconds: float,
        operator_name: Optional[str] = None,
    ) -> int:
        """Log recording start event."""
        event_id = self.database.insert_event(
            event_type="recording_started",
            timestamp_utc=time.time(),
            recording_id=recording_id,
            data={
                "center_frequency_hz": center_frequency_hz,
                "bandwidth_hz": bandwidth_hz,
                "sample_rate_sps": sample_rate_sps,
                "duration_seconds": duration_seconds,
                "operator_name": operator_name,
            }
        )
        print(f"[EventService] Recording started: {recording_id}")
        return event_id
    
    def log_recording_stopped(
        self,
        recording_id: str,
        actual_duration_seconds: float,
        sample_count: int,
        file_size_bytes: Optional[int] = None,
    ) -> int:
        """Log recording stop event."""
        event_id = self.database.insert_event(
            event_type="recording_stopped",
            timestamp_utc=time.time(),
            recording_id=recording_id,
            data={
                "actual_duration_seconds": actual_duration_seconds,
                "sample_count": sample_count,
                "file_size_bytes": file_size_bytes,
            }
        )
        print(f"[EventService] Recording stopped: {recording_id}")
        return event_id
    
    def log_file_saved(
        self,
        recording_id: str,
        filename: str,
        file_size_bytes: int,
        file_hash: str,
    ) -> int:
        """Log file save event."""
        event_id = self.database.insert_event(
            event_type="file_saved",
            timestamp_utc=time.time(),
            recording_id=recording_id,
            data={
                "filename": filename,
                "file_size_bytes": file_size_bytes,
                "file_hash": file_hash,
            }
        )
        print(f"[EventService] File saved: {filename}")
        return event_id
    
    def log_data_quality_issue(
        self,
        recording_id: str,
        issue_type: str,  # "sample_loss", "iq_imbalance", "dc_offset", etc.
        severity: str,    # "warning", "error"
        details: Dict,
    ) -> int:
        """Log data quality issues."""
        event_id = self.database.insert_event(
            event_type="data_quality_issue",
            timestamp_utc=time.time(),
            recording_id=recording_id,
            data={
                "issue_type": issue_type,
                "severity": severity,
                **details,
            }
        )
        print(f"[EventService] Data quality {severity}: {issue_type}")
        return event_id
    
    # ========================================================================
    # RETRIEVAL
    # ========================================================================
    
    def get_recent_events(self, limit: int = 100) -> list:
        """Get recent events."""
        return self.database.get_recent_events(limit=limit)
    
    def get_events_for_recording(self, recording_id: str) -> list:
        """Get all events related to a recording."""
        conn = self.database._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM events WHERE recording_id = ? ORDER BY timestamp_utc DESC",
            (recording_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_events_by_type(self, event_type: str, limit: int = 50) -> list:
        """Get events of specific type."""
        return self.database.get_recent_events(event_type=event_type, limit=limit)
