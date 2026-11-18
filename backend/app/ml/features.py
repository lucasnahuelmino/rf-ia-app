from __future__ import annotations

import numpy as np


def extract_spectrum_features(trace: list[float]) -> dict[str, float]:
    arr = np.asarray(trace, dtype=float)
    if arr.size == 0:
        return {}
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "max": float(np.max(arr)),
        "min": float(np.min(arr)),
        "median": float(np.median(arr)),
        "peak_to_mean": float(np.max(arr) - np.mean(arr)),
        "rms": float(np.sqrt(np.mean(arr ** 2))),
    }


def extract_iq_features(iq: np.ndarray) -> dict[str, float]:
    iq = np.asarray(iq)
    if iq.size == 0:
        return {}
    mag = np.abs(iq)
    phase = np.angle(iq)
    return {
        "mean_magnitude": float(np.mean(mag)),
        "std_magnitude": float(np.std(mag)),
        "mean_phase": float(np.mean(phase)),
        "std_phase": float(np.std(phase)),
        "power": float(np.mean(mag ** 2)),
    }