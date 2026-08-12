# app/devices/bb60c/exceptions.py

class BB60CError(Exception):
    """Base exception for BB60C errors."""


class BB60CSDKError(BB60CError):
    """SDK returned an error status."""


class BB60CDeviceNotFoundError(BB60CError):
    """No BB60C device detected."""


class BB60CConnectionError(BB60CError):
    """Could not connect to device."""


class BB60CDiagnosticError(BB60CError):
    """Could not retrieve diagnostics."""