from __future__ import annotations

import numpy as np
from typing import Any, Dict, List


class OccupationAuditService:
    def audit_channel(self, nominal_freq: float, trace: List[float], bin_size_hz: float, start_freq: float) -> Dict[str, Any]:
        arr = np.asarray(trace, dtype=float)
        if arr.size == 0:
            return {"nominal_frequency_hz": nominal_freq, "error": "empty trace"}

        freqs = start_freq + np.arange(arr.size) * bin_size_hz
        idx_peak = int(np.argmax(arr))
        peak_freq = float(freqs[idx_peak])
        peak_power = float(arr[idx_peak])
        mean_power = float(np.mean(arr))
        noise_floor = float(np.percentile(arr, 10))
        snr = peak_power - noise_floor

        # centroid
        linear = 10 ** (arr / 10.0)
        centroid = float(np.sum(freqs * linear) / (np.sum(linear) + 1e-12))

        # occupied bandwidth (99% power)
        order = np.argsort(linear)[::-1]
        cum = np.cumsum(linear[order])
        total = cum[-1]
        k = np.searchsorted(cum, total * 0.99)
        occupied_bins = order[: k + 1]
        occ_bw = float((freqs[occupied_bins].max() - freqs[occupied_bins].min()) if occupied_bins.size else 0.0)

        activity = float(np.mean(arr > (noise_floor + 6.0)))

        return {
            "nominal_frequency_hz": nominal_freq,
            "peak_frequency_hz": peak_freq,
            "centroid_hz": centroid,
            "frequency_offset_hz": peak_freq - nominal_freq,
            "max_power_dbm": peak_power,
            "mean_power_dbm": mean_power,
            "noise_floor_dbm": noise_floor,
            "snr_db": snr,
            "occupied_bandwidth_hz": occ_bw,
            "activity_ratio": activity,
            "persistence": activity,
        }

    def audit_band(self, channels: List[Dict[str, Any]], trace: List[float], bin_size_hz: float, start_freq: float) -> List[Dict[str, Any]]:
        return [self.audit_channel(ch["frequency"], trace, bin_size_hz, start_freq) for ch in channels]