from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from .adapter import BB60CAdapter
from .models import SweepConfiguration


def main() -> None:

    adapter = BB60CAdapter()

    try:
        adapter.connect()

        config = SweepConfiguration(
            center_frequency_hz=124.650e6,
            span_hz=5e6,
            rbw_hz=10e3,
            vbw_hz=10e3,
            reference_level_dbm=0,
        )

        adapter.configure_sweep(config)

        print("Starting sweep...")

        adapter.start_sweep()

        trace = adapter.get_trace()

        frequencies = (
            trace.info.start_frequency_hz
            + np.arange(trace.info.trace_length)
            * trace.info.bin_size_hz
        )

        frequencies_mhz = frequencies / 1e6

        plt.figure(figsize=(14, 6))

        plt.plot(
            frequencies_mhz,
            trace.trace_max,
            linewidth=1,
        )

        plt.title(
            "RF Monitor - BB60C Spectrum"
        )

        plt.xlabel("Frequency (MHz)")
        plt.ylabel("Power (dBm)")

        plt.grid(True)

        plt.tight_layout()

        output_file = "spectrum.png"

        plt.savefig(
            output_file,
            dpi=150,
        )

        print()
        print(
            f"Spectrum saved to: {output_file}"
        )

    finally:
        adapter.disconnect()

        print("Device closed successfully.")


if __name__ == "__main__":
    main()