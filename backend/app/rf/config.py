from threading import Lock


class SpectrumConfig:

    def __init__(self):

        self.lock = Lock()

        self.version = 1

        self.center_frequency_hz = 124.650e6

        self.span_hz = 5e6

        self.rbw_hz = 10e3

        self.vbw_hz = 10e3

        self.reference_level_dbm = 0.0


spectrum_config = SpectrumConfig()