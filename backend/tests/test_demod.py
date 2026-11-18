import numpy as np

from app.dsp.demod import demodulate


def test_am_demodulation_produces_audio():
    sr = 1e6
    t = np.arange(int(0.1 * sr)) / sr
    tone = 0.5 * np.sin(2 * np.pi * 1000 * t)
    iq = (1 + tone) * np.exp(1j * 2 * np.pi * 100e3 * t)

    audio = demodulate("AM", iq.astype(np.complex64), sr, 48000.0)

    assert audio.size > 0
    assert np.max(np.abs(audio)) <= 1.01
    assert np.isfinite(audio).all()


def test_fm_modes_differ():
    sr = 1e6
    t = np.arange(int(0.1 * sr)) / sr
    mod = np.sin(2 * np.pi * 1000 * t)
    phase = 2 * np.pi * 5000 * np.cumsum(mod) / sr
    iq = np.exp(1j * phase).astype(np.complex64)

    wfm = demodulate("WFM", iq, sr, 48000.0)
    nfm = demodulate("NFM", iq, sr, 48000.0)

    assert wfm.size > 0
    assert nfm.size > 0
    # Different filtering/deviation should not be identical
    assert not np.allclose(wfm, nfm, atol=1e-3)


def test_ssb_and_cw():
    sr = 1e6
    t = np.arange(int(0.05 * sr)) / sr
    iq = (np.cos(2 * np.pi * 1000 * t) + 1j * np.sin(2 * np.pi * 1000 * t)).astype(np.complex64)

    usb = demodulate("USB", iq, sr, 48000.0)
    lsb = demodulate("LSB", iq, sr, 48000.0)
    cw = demodulate("CW", iq, sr, 48000.0)

    assert usb.size > 0
    assert lsb.size > 0
    assert cw.size > 0


def test_unsupported_mode_raises():
    import pytest

    iq = np.ones(10, dtype=np.complex64)
    with pytest.raises(ValueError):
        demodulate("NOPE", iq, 1e6)