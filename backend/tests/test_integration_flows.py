import json
import os
import tempfile

import numpy as np

from app.audio.wav_recorder import WAVMetadata, WAVRecorder
from app.dsp.demod import demodulate
from app.rf.iq_recorder import IQMetadata, IQRecorder
from app.rf.iq_player import IQPlayer
from app.services.export_service import ExportService
from app.services.session_service import SessionService


def test_iq_record_play_demod_export_session_flow():
    tmp = tempfile.mkdtemp()
    iq_dir = os.path.join(tmp, "iq")
    wav_dir = os.path.join(tmp, "wav")
    exp_dir = os.path.join(tmp, "exp")
    db = os.path.join(tmp, "test.db")
    os.makedirs(iq_dir, exist_ok=True)
    os.makedirs(wav_dir, exist_ok=True)
    os.makedirs(exp_dir, exist_ok=True)

    # Record IQ
    recorder = IQRecorder(iq_dir)
    meta = IQMetadata(filename="flow.iq", center_frequency_hz=100e6, sample_rate_hz=1e6, bandwidth_hz=200e3, gain=-1, attenuation=-1)
    recorder.start(meta)
    iq = np.exp(1j * 2 * np.pi * 1000 * np.arange(1000) / 1e6).astype(np.complex64)
    recorder.write(iq)
    recorder.stop()

    # Play IQ
    player = IQPlayer(iq_dir)
    player.open("flow.iq")
    player.play()
    chunk = player.read_chunk(500)
    assert chunk is not None and chunk.size == 500

    # Demodulate
    audio = demodulate("WFM", iq, 1e6, 48000.0)
    assert audio.size > 0

    # Record WAV
    wav_rec = WAVRecorder(wav_dir)
    wav_meta = WAVMetadata(filename="flow.wav", sample_rate=48000)
    wav_rec.start(wav_meta)
    wav_rec.write(audio)
    wav_rec.stop()
    assert os.path.exists(os.path.join(wav_dir, "flow.wav"))

    # Export
    exp = ExportService(exp_dir)
    path = exp.to_csv("flow.csv", [{"freq": 100.0, "level": -50.0}], ["freq", "level"])
    assert os.path.exists(path)

    # Session
    sessions = SessionService(db)
    sid = sessions.create_session("flow", {"center_frequency_hz": 100e6}, "test")
    sessions.add_capture(sid, "iq", "flow.iq", {"samples": 1000})
    sessions.add_event(sid, "info", "flow completed")
    assert sessions.get_session(sid) is not None
    assert len(sessions.list_captures(sid)) == 1
    assert len(sessions.list_events(sid)) == 1