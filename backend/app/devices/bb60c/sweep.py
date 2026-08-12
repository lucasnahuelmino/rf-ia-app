from __future__ import annotations

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

        print()
        print("RF Monitor - Sweep Test")
        print("-" * 40)

        print(
            f"Trace Length: "
            f"{trace.info.trace_length}"
        )

        print(
            f"Bin Size: "
            f"{trace.info.bin_size_hz:.2f} Hz"
        )

        print(
            f"Start Frequency: "
            f"{trace.info.start_frequency_hz:.2f} Hz"
        )

        print()
        print("First 10 Trace Samples")
        print("-" * 40)

        samples_to_show = min(
            10,
            len(trace.trace_max),
        )

        for i in range(samples_to_show):
            print(
                f"{i:03d}: "
                f"{trace.trace_max:.2f} dBm"
            )

    finally:
        adapter.disconnect()

        print()
        print("Device closed successfully.")


if __name__ == "__main__":
    main()