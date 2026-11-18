from __future__ import annotations

import threading
import time
from typing import Optional

import numpy as np

from app.devices.bb60c.models import SweepConfiguration
from app.rf.config import spectrum_config
from app.rf.models import SpectrumSnapshot
from app.rf.state import spectrum_state
from app.rf.synthetic import generate_spectrum
from app.services.device_manager import device_manager


class SpectrumWorker:
    """Continuous sweep acquisition worker with simulated fallback."""

    def __init__(self, manager=None) -> None:
        self._manager = manager or device_manager
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(
                target=self._run,
                daemon=True,
                name="SpectrumWorker",
            )
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._running = False

        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=5.0)
        self._thread = None

    def is_running(self) -> bool:
        return self._running

    def single_sweep(self) -> None:
        self._acquire_once()

    def _build_config(self) -> SweepConfiguration:
        with spectrum_config.lock:
            return SweepConfiguration(
                center_frequency_hz=spectrum_config.center_frequency_hz,
                span_hz=spectrum_config.span_hz,
                start_frequency_hz=spectrum_config.start_frequency_hz,
                stop_frequency_hz=spectrum_config.stop_frequency_hz,
                rbw_hz=spectrum_config.rbw_hz,
                vbw_hz=spectrum_config.vbw_hz,
                reference_level_dbm=spectrum_config.reference_level_dbm,
                attenuation=spectrum_config.attenuation,
                gain=spectrum_config.gain,
                auto_attenuation=spectrum_config.auto_attenuation,
                auto_gain=spectrum_config.auto_gain,
                detector=spectrum_config.detector,
                rbw_shape=spectrum_config.rbw_shape,
                spur_reject=spectrum_config.spur_reject,
                sweep_time_s=spectrum_config.sweep_time_s,
            )

    def _config_version(self) -> int:
        with spectrum_config.lock:
            return spectrum_config.version

    def _acquire_once(self) -> None:
        self._manager.connect()
        try:
            self._manager.set_acquiring(True)

            cfg = self._build_config()
            self._manager.configure_sweep(cfg)
            self._manager.start_sweep()

            trace = self._manager.get_trace()

            center, span, start, stop = cfg.normalized_center_span()

            with spectrum_state.lock:
                spectrum_state.snapshot.timestamp = time.time()
                spectrum_state.snapshot.center_frequency_hz = center
                spectrum_state.snapshot.span_hz = span
                spectrum_state.snapshot.start_frequency_hz = trace.info.start_frequency_hz
                spectrum_state.snapshot.stop_frequency_hz = (
                    trace.info.start_frequency_hz
                    + trace.info.trace_length * trace.info.bin_size_hz
                )
                spectrum_state.snapshot.bin_size_hz = trace.info.bin_size_hz
                spectrum_state.snapshot.trace_length = trace.info.trace_length
                spectrum_state.snapshot.trace = trace.trace_max.tolist()
                spectrum_state.snapshot.trace_min = trace.trace_min.tolist()
                spectrum_state.snapshot.trace_max = trace.trace_max.tolist()
                spectrum_state.snapshot.config_version = self._config_version()
                spectrum_state.snapshot.source = "HARDWARE"

            self._manager.set_acquiring(False)
        except Exception:
            self._manager.set_acquiring(False)
            raise
        finally:
            self._manager.disconnect()

    def _run(self) -> None:
        last_config_version = -1
        simulated = False

        try:
            while self._running:
                try:
                    if not simulated:
                        if not self._manager.is_connected:
                            self._manager.connect()

                        current_version = self._config_version()

                        if current_version != last_config_version:
                            self._manager.set_acquiring(True)
                            cfg = self._build_config()
                            self._manager.configure_sweep(cfg)
                            self._manager.start_sweep()
                            last_config_version = current_version
                            self._manager.set_acquiring(False)

                        trace = self._manager.get_trace()

                        center, span, _start, _stop = self._build_config().normalized_center_span()

                        with spectrum_state.lock:
                            spectrum_state.snapshot.timestamp = time.time()
                            spectrum_state.snapshot.center_frequency_hz = center
                            spectrum_state.snapshot.span_hz = span
                            spectrum_state.snapshot.start_frequency_hz = trace.info.start_frequency_hz
                            spectrum_state.snapshot.stop_frequency_hz = (
                                trace.info.start_frequency_hz
                                + trace.info.trace_length * trace.info.bin_size_hz
                            )
                            spectrum_state.snapshot.bin_size_hz = trace.info.bin_size_hz
                            spectrum_state.snapshot.trace_length = trace.info.trace_length
                            spectrum_state.snapshot.trace = trace.trace_max.tolist()
                            spectrum_state.snapshot.trace_min = trace.trace_min.tolist()
                            spectrum_state.snapshot.trace_max = trace.trace_max.tolist()
                            spectrum_state.snapshot.config_version = current_version
                            spectrum_state.snapshot.source = "HARDWARE"

                        time.sleep(0.05)
                    else:
                        cfg = self._build_config()
                        center, span, start, stop = cfg.normalized_center_span()
                        bin_size = cfg.rbw_hz
                        trace = generate_spectrum(center, span, bin_size)
                        with spectrum_state.lock:
                            spectrum_state.snapshot.timestamp = time.time()
                            spectrum_state.snapshot.center_frequency_hz = center
                            spectrum_state.snapshot.span_hz = span
                            spectrum_state.snapshot.start_frequency_hz = start
                            spectrum_state.snapshot.stop_frequency_hz = stop
                            spectrum_state.snapshot.bin_size_hz = bin_size
                            spectrum_state.snapshot.trace_length = len(trace)
                            spectrum_state.snapshot.trace = trace.tolist()
                            spectrum_state.snapshot.trace_min = (trace - 2).tolist()
                            spectrum_state.snapshot.trace_max = trace.tolist()
                            spectrum_state.snapshot.config_version = self._config_version()
                            spectrum_state.snapshot.source = "SIMULATED"
                        time.sleep(0.1)

                except Exception as exc:
                    print("[SpectrumWorker] ERROR:", exc)
                    if not simulated:
                        print("[SpectrumWorker] Falling back to SIMULATED source.")
                        simulated = True
                    self._manager.set_acquiring(False)
                    try:
                        self._manager.force_disconnect()
                    except Exception:
                        pass
                    time.sleep(1.0)

        finally:
            try:
                self._manager.force_disconnect()
            except Exception:
                pass
            print("[SpectrumWorker] Device disconnected.")