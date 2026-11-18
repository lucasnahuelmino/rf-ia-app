from __future__ import annotations

import numpy as np
from typing import Any, Dict

from app.rf.config import spectrum_config


def generate_spectrum(
    center_frequency_hz: float,
    span_hz: float,
    bin_size_hz: float = 10000.0,
    noise_floor: float = -90.0,
    peaks: list[dict[str, Any]] | None = None,
    seed: int = 42,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    num_bins = max(1, int(span_hz / bin_size_hz))
    trace = rng.normal(noise_floor, 2.0, num_bins)

    start = center_frequency_hz - span_hz / 2.0
    freqs = start + np.arange(num_bins) * bin_size_hz

    peaks = peaks or [
        {"offset_hz": 0.0, "amplitude": -40.0, "width_bins": 3},
        {"offset_hz": span_hz * 0.25, "amplitude": -55.0, "width_bins": 5},
    ]

    for peak in peaks:
        offset = peak.get("offset_hz", 0.0)
        amplitude = peak.get("amplitude", -40.0)
        width = peak.get("width_bins", 3)
        idx = int((offset + span_hz / 2.0) / bin_size_hz)
        for w in range(-width, width + 1):
            i = idx + w
            if 0 <= i < num_bins:
                trace[i] = max(trace[i], amplitude - abs(w) * 3.0)

    return trace.astype(float)


def generate_iq(
    mode: str = "WFM",
    sample_rate: float = 1e6,
    duration: float = 0.5,
    center_offset_hz: float = 1000.0,
    snr_db: float = 20.0,
    seed: int = 42,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(sample_rate * duration)
    t = np.arange(n) / sample_rate

    if mode.upper() in ("WFM", "NFM", "FM"):
        mod = np.sin(2 * np.pi * 1000 * t)
        dev = 75000.0 if mode.upper() == "WFM" else 2500.0
        phase = 2 * np.pi * dev * np.cumsum(mod) / sample_rate
        iq = np.exp(1j * phase)
    elif mode.upper() == "AM":
        mod = 0.5 * (1 + 0.5 * np.sin(2 * np.pi * 1000 * t))
        iq = mod * np.exp(1j * 2 * np.pi * center_offset_hz * t)
    else:
        iq = np.exp(1j * 2 * np.pi * center_offset_hz * t)

    # Add noise
    noise_power = 10 ** (-snr_db / 10.0)
    noise = (rng.normal(0, np.sqrt(noise_power / 2), n)
             + 1j * rng.normal(0, np.sqrt(noise_power / 2), n))
    iq = (iq + noise).astype(np.complex64)
    return iq