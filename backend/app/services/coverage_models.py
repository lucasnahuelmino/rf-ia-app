from __future__ import annotations

import math
from typing import Any, Dict


class CoverageModelService:
    def free_space(self, params: Dict[str, Any]) -> Dict[str, Any]:
        f_mhz = params["frequency_hz"] / 1e6
        d_km = params["distance_km"]
        tx_power_dbm = params.get("tx_power_dbm", 0.0)
        tx_gain_dbi = params.get("tx_gain_dbi", 0.0)
        rx_gain_dbi = params.get("rx_gain_dbi", 0.0)
        losses_db = params.get("losses_db", 0.0)
        fspl = 20 * math.log10(d_km) + 20 * math.log10(f_mhz) + 32.44
        rssi = tx_power_dbm + tx_gain_dbi + rx_gain_dbi - fspl - losses_db
        return {
            "model": "free_space",
            "predicted_rssi_dbm": rssi,
            "path_loss_db": fspl,
            "assumptions": "Line-of-sight, no terrain, no clutter.",
            "limitations": "Not valid in urban/indoor environments.",
        }

    def okumura_hata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        f_mhz = params["frequency_hz"] / 1e6
        d_km = max(params["distance_km"], 0.001)
        hb = params["tx_height_m"]
        hm = params["rx_height_m"]
        tx_power_dbm = params.get("tx_power_dbm", 0.0)
        tx_gain_dbi = params.get("tx_gain_dbi", 0.0)
        rx_gain_dbi = params.get("rx_gain_dbi", 0.0)
        losses_db = params.get("losses_db", 0.0)

        # Urban medium city
        a_hm = (1.1 * math.log10(f_mhz) - 0.7) * hm - (1.56 * math.log10(f_mhz) - 0.8)
        L = 69.55 + 26.16 * math.log10(f_mhz) - 13.82 * math.log10(hb) - a_hm + (44.9 - 6.55 * math.log10(hb)) * math.log10(d_km)
        rssi = tx_power_dbm + tx_gain_dbi + rx_gain_dbi - L - losses_db
        return {
            "model": "okumura_hata_urban",
            "predicted_rssi_dbm": rssi,
            "path_loss_db": L,
            "assumptions": "Urban medium city, hb 30-200m, d 1-20km, f 150-1500MHz.",
            "limitations": "Not for rural/suburban without correction factors.",
        }

    def cost231_hata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        f_mhz = params["frequency_hz"] / 1e6
        d_km = max(params["distance_km"], 0.001)
        hb = params["tx_height_m"]
        hm = params["rx_height_m"]
        tx_power_dbm = params.get("tx_power_dbm", 0.0)
        tx_gain_dbi = params.get("tx_gain_dbi", 0.0)
        rx_gain_dbi = params.get("rx_gain_dbi", 0.0)
        losses_db = params.get("losses_db", 0.0)
        C = 3.0  # metropolitan
        a_hm = (1.1 * math.log10(f_mhz) - 0.7) * hm - (1.56 * math.log10(f_mhz) - 0.8)
        L = 46.3 + 33.9 * math.log10(f_mhz) - 13.82 * math.log10(hb) - a_hm + (44.9 - 6.55 * math.log10(hb)) * math.log10(d_km) + C
        rssi = tx_power_dbm + tx_gain_dbi + rx_gain_dbi - L - losses_db
        return {
            "model": "cost231_hata",
            "predicted_rssi_dbm": rssi,
            "path_loss_db": L,
            "assumptions": "Urban, f 1500-2000MHz.",
            "limitations": "Metropolitan correction C=3 dB.",
        }

    def predict(self, model: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if model == "free_space":
            return self.free_space(params)
        if model == "okumura_hata":
            return self.okumura_hata(params)
        if model == "cost231_hata":
            return self.cost231_hata(params)
        raise ValueError("Unknown model")