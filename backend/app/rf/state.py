from threading import Lock


class SpectrumState:

    def __init__(self):

        self.lock = Lock()

        self.trace = None

        self.trace_length = 0

        self.bin_size_hz = 0.0

        self.start_frequency_hz = 0.0


spectrum_state = SpectrumState()