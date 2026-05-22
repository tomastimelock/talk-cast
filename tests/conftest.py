# Filepath: talk-cast/tests/conftest.py
# Condensed Description: Shared fixtures for talk-cast test suite
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.conftest
# Dependencies: Internal: talk_cast.config / External: pytest
# Exposes: minimal_deck, silence_wav, mock_tts, patch_mp3_to_wav, minimal_cache_dir
# Configuration: None
from __future__ import annotations

import shutil
import wave
from collections.abc import Callable
from pathlib import Path

import pytest
from deck_spec.models import Deck, Slide


def _write_silence_wav(path: Path, duration_sec: float, sample_rate: int = 44100) -> Path:
    """Write a silent 16-bit mono WAV file to *path*."""
    n_frames = int(sample_rate * duration_sec)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_frames)
    return path


def _minimal_silence_wav_bytes(duration_sec: float = 1.0, sample_rate: int = 44100) -> bytes:
    """Return in-memory bytes of a minimal silent WAV (no disk I/O)."""
    import io

    buf = io.BytesIO()
    n_frames = int(sample_rate * duration_sec)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_frames)
    return buf.getvalue()


@pytest.fixture
def minimal_deck() -> Deck:
    """2-slide Deck: one title slide with notes, one content slide with notes."""
    return Deck(
        title="Test Deck",
        slides=[
            Slide(
                layout="title",
                title="Opening",
                subtitle="A test deck",
                notes="Opening narration.",
            ),
            Slide(
                layout="content",
                title="Main",
                body="Some content here.",
                notes="Main content narration.",
            ),
        ],
    )


@pytest.fixture
def silence_wav(tmp_path: Path) -> Callable[[float], Path]:
    """Factory fixture: make_silence(duration_sec) -> Path to a WAV file."""
    _counter = [0]

    def make_silence(duration_sec: float) -> Path:
        _counter[0] += 1
        out = tmp_path / f"silence_{_counter[0]}.wav"
        return _write_silence_wav(out, duration_sec)

    return make_silence


@pytest.fixture
def mock_tts() -> Callable[[str, str, str, dict, str], bytes]:
    """
    Callable matching BatchTTS's tts_fn signature.

    Returns bytes of a valid 1-second silent WAV.  BatchTTS will pass these
    bytes to TTSCache.put() (stored as .mp3 on disk), then call _mp3_to_wav.
    Pair with patch_mp3_to_wav so that ffmpeg is never invoked.
    """
    wav_bytes = _minimal_silence_wav_bytes(duration_sec=1.0)

    def _synth(
        text: str, voice_id: str, model_id: str, voice_settings: dict, api_key: str
    ) -> bytes:
        return wav_bytes

    return _synth


@pytest.fixture
def patch_mp3_to_wav(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    Patch talk_cast.tts.batch._mp3_to_wav to copy the source file as-is
    (treating the WAV bytes stored in the .mp3 slot as already usable WAV).
    """

    def _fake_mp3_to_wav(mp3_path: Path, wav_path: Path) -> None:
        shutil.copy(mp3_path, wav_path)

    monkeypatch.setattr("talk_cast.tts.batch._mp3_to_wav", _fake_mp3_to_wav)


@pytest.fixture
def minimal_cache_dir(tmp_path: Path) -> Path:
    """Return a fresh empty cache directory."""
    cache = tmp_path / "cache"
    cache.mkdir()
    return cache
