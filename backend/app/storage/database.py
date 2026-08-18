"""
SQLite database initialization and operations.

Manages persistent storage of recording metadata and events
in SQLite database.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class Database:
    """SQLite database for RF Monitor metadata."""
    
    def __init__(self, db_path: str = "./data/rf_monitor.db"):
        """
        Initialize database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_tables()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        return conn
    
    # ========================================================================
    # SCHEMA INITIALIZATION
    # ========================================================================
    
    def _init_tables(self):
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Recordings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recordings (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                recording_type TEXT NOT NULL,
                timestamp_utc REAL NOT NULL,
                device_id TEXT,
                device_type TEXT,
                center_frequency_hz REAL,
                bandwidth_hz REAL,
                sample_rate_sps REAL,
                duration_seconds REAL,
                sample_count INTEGER,
                file_size_bytes INTEGER,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_timestamp (timestamp_utc),
                INDEX idx_device_id (device_id),
                INDEX idx_type (recording_type),
                INDEX idx_center_freq (center_frequency_hz)
            )
        """)
        
        # Events table (detection events, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp_utc REAL NOT NULL,
                recording_id TEXT,
                data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recording_id) REFERENCES recordings(id),
                INDEX idx_event_type (event_type),
                INDEX idx_timestamp (timestamp_utc),
                INDEX idx_recording_id (recording_id)
            )
        """)
        
        # Models table (for ML phase)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY,
                model_type TEXT NOT NULL,
                dataset_id TEXT,
                training_date TIMESTAMP,
                hyperparameters_json TEXT,
                metrics_json TEXT,
                feature_names_json TEXT,
                file_path TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_model_type (model_type),
                INDEX idx_status (status)
            )
        """)
        
        # Predictions table (for inference phase)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recording_id TEXT,
                model_id TEXT,
                predicted_class TEXT,
                confidence REAL,
                probabilities_json TEXT,
                timestamp_utc REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recording_id) REFERENCES recordings(id),
                FOREIGN KEY (model_id) REFERENCES models(id),
                INDEX idx_recording_id (recording_id),
                INDEX idx_model_id (model_id),
                INDEX idx_class (predicted_class)
            )
        """)
        
        conn.commit()
        conn.close()
        print("[Database] Initialized SQLite tables")
    
    # ========================================================================
    # RECORDINGS TABLE
    # ========================================================================
    
    def insert_recording(
        self,
        recording_id: str,
        filename: str,
        recording_type: str,  # "iq" or "sweep"
        timestamp_utc: float,
        device_id: Optional[str] = None,
        device_type: Optional[str] = None,
        center_frequency_hz: Optional[float] = None,
        bandwidth_hz: Optional[float] = None,
        sample_rate_sps: Optional[float] = None,
        duration_seconds: Optional[float] = None,
        sample_count: Optional[int] = None,
        file_size_bytes: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Insert recording metadata into database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO recordings (
                id, filename, recording_type, timestamp_utc,
                device_id, device_type, center_frequency_hz,
                bandwidth_hz, sample_rate_sps, duration_seconds,
                sample_count, file_size_bytes, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recording_id, filename, recording_type, timestamp_utc,
            device_id, device_type, center_frequency_hz,
            bandwidth_hz, sample_rate_sps, duration_seconds,
            sample_count, file_size_bytes, metadata_json
        ))
        
        conn.commit()
        conn.close()
    
    def get_recording(self, recording_id: str) -> Optional[Dict]:
        """Get recording by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM recordings WHERE id = ?", (recording_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def list_recordings(
        self,
        recording_type: Optional[str] = None,
        device_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """List recordings with optional filters."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM recordings"
        params = []
        
        if recording_type:
            query += " WHERE recording_type = ?"
            params.append(recording_type)
        elif device_id:
            query += " WHERE device_id = ?"
            params.append(device_id)
        
        query += " ORDER BY timestamp_utc DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_recording(self, recording_id: str, **kwargs) -> None:
        """Update recording fields."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(recording_id)
        
        query = f"UPDATE recordings SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def delete_recording(self, recording_id: str) -> None:
        """Delete recording metadata."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM events WHERE recording_id = ?", (recording_id,))
        cursor.execute("DELETE FROM predictions WHERE recording_id = ?", (recording_id,))
        cursor.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # EVENTS TABLE
    # ========================================================================
    
    def insert_event(
        self,
        event_type: str,
        timestamp_utc: float,
        recording_id: Optional[str] = None,
        data: Optional[Dict] = None,
    ) -> int:
        """Insert event. Returns event ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data_json = json.dumps(data) if data else None
        
        cursor.execute("""
            INSERT INTO events (event_type, timestamp_utc, recording_id, data_json)
            VALUES (?, ?, ?, ?)
        """, (event_type, timestamp_utc, recording_id, data_json))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    def get_recent_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """Get recent events."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if event_type:
            query = """
                SELECT * FROM events
                WHERE event_type = ?
                ORDER BY timestamp_utc DESC
                LIMIT ?
            """
            cursor.execute(query, (event_type, limit))
        else:
            query = """
                SELECT * FROM events
                ORDER BY timestamp_utc DESC
                LIMIT ?
            """
            cursor.execute(query, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========================================================================
    # PREDICTIONS TABLE (for ML phase)
    # ========================================================================
    
    def insert_prediction(
        self,
        recording_id: str,
        model_id: str,
        predicted_class: str,
        confidence: float,
        probabilities: Optional[Dict] = None,
        timestamp_utc: Optional[float] = None,
    ) -> int:
        """Insert prediction. Returns prediction ID."""
        if timestamp_utc is None:
            import time
            timestamp_utc = time.time()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        probs_json = json.dumps(probabilities) if probabilities else None
        
        cursor.execute("""
            INSERT INTO predictions (
                recording_id, model_id, predicted_class,
                confidence, probabilities_json, timestamp_utc
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            recording_id, model_id, predicted_class,
            confidence, probs_json, timestamp_utc
        ))
        
        pred_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return pred_id
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM recordings")
        recording_count = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM recordings WHERE recording_type = ?", ("iq",))
        iq_count = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM events")
        event_count = cursor.fetchone()["count"]
        
        cursor.execute("SELECT SUM(file_size_bytes) as total FROM recordings")
        total_size = cursor.fetchone()["total"] or 0
        
        conn.close()
        
        return {
            "total_recordings": recording_count,
            "iq_recordings": iq_count,
            "total_events": event_count,
            "total_storage_gb": total_size / (1024 ** 3),
        }
