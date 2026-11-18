from __future__ import annotations

import numpy as np


def _lowpass(signal: np.ndarray, cutoff: float, sample_rate: float, taps: int = 65) -> np.ndarray:
    """Simple FIR low-pass filter using a Hann window."""
    if cutoff <= 0 or cutoff >= sample_rate / 2:
        return signal

    n = np.arange(taps)
    h = np.sinc(2 * cutoff / sample_rate * (n - (taps - 1) / 2))
    w = np.hanning(taps)
    h = h * w
    h = h / np.sum(h)

    padded = np.convolve(signal, h, mode="same")
    return padded


def _deemphasis(signal: np.ndarray, sample_rate: float, tau: float) -> np.ndarray:
    """First-order IIR de-emphasis."""
    if tau <= 0:
        return signal

    alpha = 1.0 / (1.0 + sample_rate * tau)
    output = np.zeros_like(signal)
    output[0] = signal[0]
    for i in range(1, len(signal)):
        output[i] = output[i - 1] + alpha * (signal[i] - output[i - 1])
    return output


def _agc(signal: np.ndarray, target: float = 0.5) -> np.ndarray:
    rms = np.sqrt(np.mean(signal ** 2) + 1e-12)
    gain = target / rms
    gain = min(gain, 10.0)
    return signal * gain


def _normalize(signal: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(signal)) + 1e-12
    return signal / peak * 0.9


def demodulate_am(iq: np.ndarray, sample_rate: float, audio_rate: float = 48000.0, if_bandwidth: float = 8000.0) -> np.ndarray:
    """AM envelope detector."""
    envelope = np.abs(iq)
    envelope = envelope - np.mean(envelope)
    audio = _lowpass(envelope, if_bandwidth, sample_rate)
    # decimate
    if sample_rate != audio_rate:
        factor = int(round(sample_rate / audio_rate))
        factor = max(1, factor)
        audio = audio[::factor]
    audio = _agc(audio)
    return _normalize(audio).astype(np.float32)


def demodulate_fm(
    iq: np.ndarray,
    sample_rate: float,
    audio_rate: float = 48000.0,
    deviation: float = 5000.0,
    deemp_tau: float = 0.0,
    if_bandwidth: float = 12500.0,
) -> np.ndarray:
    """FM discriminator."""
    # Phase difference
    phase = np.unwrap(np.angle(iq))
    freq = np.diff(phase) * sample_rate / (2 * np.pi)
    freq = np.concatenate(([freq[0] if len(freq) else 0.0], freq))
    freq = freq - np.mean(freq)
    freq = np.clip(freq, -deviation, deviation)
    audio = _lowpass(freq, if_bandwidth, sample_rate)
    if deemp_tau > 0:
        audio = _deemphasis(audio, sample_rate, deemp_tau)
    if sample_rate != audio_rate:
        factor = int(round(sample_rate / audio_rate))
        factor = max(1, factor)
        audio = audio[::factor]
    audio = _agc(audio)
    return _normalize(audio).astype(np.float32)


def demodulate_wfm(iq, sample_rate, audio_rate=48000.0):
    return demodulate_fm(iq, sample_rate, audio_rate, deviation=75000.0, deemp_tau=75e-6, if_bandwidth=150000.0)


def demodulate_nfm(iq, sample_rate, audio_rate=48000.0):
    return demodulate_fm(iq, sample_rate, audio_rate, deviation=2500.0, deemp_tau=0.0, if_bandwidth=3000.0)


def demodulate_ssb(iq, sample_rate, audio_rate=48000.0, usb=True, if_bandwidth=3000.0):
    # Mix to baseband already assumed; apply lowpass and take real part with sideband selection
    if usb:
        audio = np.real(iq)
    else:
        audio = np.imag(iq)
    audio = audio - np.mean(audio)
    audio = _lowpass(audio, if_bandwidth, sample_rate)
    if sample_rate != audio_rate:
        factor = int(round(sample_rate / audio_rate))
        factor = max(1, factor)
        audio = audio[::factor]
    audio = _agc(audio)
    return _normalize(audio).astype(np.float32)


def demodulate_cw(iq, sample_rate, audio_rate=48000.0, tone=600.0, if_bandwidth=500.0):
    envelope = np.abs(iq)
    envelope = envelope - np.mean(envelope)
    audio = _lowpass(envelope, if_bandwidth, sample_rate)
    # Generate audible tone gated by envelope
    t = np.arange(len(audio)) / sample_rate
    carrier = np.sin(2 * np.pi * tone * t)
    audio = audio * carrier
    audio = _lowpass(audio, if_bandwidth, sample_rate)
    if sample_rate != audio_rate:
        factor = int(round(sample_rate / audio_rate))
        factor = max(1, factor)
        audio = audio[::factor]
    audio = _agc(audio)
    return _normalize(audio).astype(np.float32)


MODES = {
    "AM": demodulate_am,
    "FM": demodulate_nfm,
    "WFM": demodulate_wfm,
    "NFM": demodulate_nfm,
    "USB": lambda iq, sr, ar=48000.0: demodulate_ssb(iq, sr, ar, usb=True),
    "LSB": lambda iq, sr, ar=48000.0: demodulate_ssb(iq, sr, ar, usb=False),
    "CW": demodulate_cw,
}


def demodulate(mode: str, iq: np.ndarray, sample_rate: float, audio_rate: float = 48000.0, **kwargs) -> np.ndarray:
    mode = mode.upper()
    if mode not in MODES:
        raise ValueError(f"Unsupported demodulation mode: {mode}")
    func = MODES[mode]
    if mode in ("AM",):
        return func(iq, sample_rate, audio_rate, **{k: v for k, v in kwargs.items() if k in ("if_bandwidth",)})
    if mode in ("FM", "NFM"):
        return func(iq, sample_rate, audio_rate, **{k: v for k, v in kwargs.items() if k in ("deviation", "deemp_tau", "if_bandwidth")})
    if mode == "WFM":
        return func(iq, sample_rate, audio_rate)
    if mode in ("USB", "LSB"):
        return func(iq, sample_rate, audio_rate)
    if mode == "CW":
        return func(iq, sample_rate, audio_rate, **{k: v for k, v in kwargs.items() if k in ("tone", "if_bandwidth")})
    return func(iq, sample_rate, audio_rate)