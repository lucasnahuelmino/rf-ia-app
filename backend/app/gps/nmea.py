from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class GPSPosition:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed_knots: Optional[float] = None
    course: Optional[float] = None
    satellites: Optional[int] = None
    fix_quality: Optional[int] = None
    timestamp: str = ""
    valid: bool = False


def _nmea_to_decimal(value: str, hemisphere: str) -> float:
    if not value:
        return 0.0
    # value format: ddmm.mmmm or dddmm.mmmm
    if "." in value:
        dot = value.index(".")
        degrees_len = dot - 2
    else:
        degrees_len = len(value) - 2
    degrees = float(value[:degrees_len])
    minutes = float(value[degrees_len:])
    decimal = degrees + minutes / 60.0
    if hemisphere in ("S", "W"):
        decimal = -decimal
    return decimal


def parse_nmea(sentence: str) -> Optional[GPSPosition]:
    sentence = sentence.strip()
    if not sentence.startswith("$"):
        return None
    # Remove checksum
    if "*" in sentence:
        sentence = sentence.split("*")[0]
    parts = sentence.split(",")
    if len(parts) < 2:
        return None

    talker = parts[0][1:]  # e.g. GPGGA
    msg_type = talker[-3:]

    if msg_type == "GGA":
        # $GPGGA,time,lat,N,lon,E,quality,sats,hdop,alt,M,...
        if len(parts) < 10:
            return None
        try:
            quality = int(parts[6]) if parts[6] else 0
        except ValueError:
            quality = 0
        lat = _nmea_to_decimal(parts[2], parts[3])
        lon = _nmea_to_decimal(parts[4], parts[5])
        sats = None
        try:
            sats = int(parts[7]) if parts[7] else None
        except ValueError:
            sats = None
        alt = None
        try:
            alt = float(parts[9]) if parts[9] else None
        except ValueError:
            alt = None
        valid = quality > 0 and lat != 0 and lon != 0
        return GPSPosition(
            latitude=lat,
            longitude=lon,
            altitude=alt,
            satellites=sats,
            fix_quality=quality,
            timestamp=datetime.now(timezone.utc).isoformat(),
            valid=valid,
        )

    if msg_type == "RMC":
        # $GPRMC,time,status,lat,N,lon,E,speed,course,date,...
        if len(parts) < 9:
            return None
        status = parts[2]
        lat = _nmea_to_decimal(parts[3], parts[4])
        lon = _nmea_to_decimal(parts[5], parts[6])
        speed = None
        course = None
        try:
            speed = float(parts[7]) if parts[7] else None
        except ValueError:
            speed = None
        try:
            course = float(parts[8]) if parts[8] else None
        except ValueError:
            course = None
        valid = status == "A" and lat != 0 and lon != 0
        return GPSPosition(
            latitude=lat,
            longitude=lon,
            speed_knots=speed,
            course=course,
            timestamp=datetime.now(timezone.utc).isoformat(),
            valid=valid,
        )

    return None