# Filepath: talk-cast/tests/test_tts_cache_hit.py
# Condensed Description: Tests for BatchTTS cache hit/miss behaviour and WAV output
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_tts_cache_hit
# Dependencies: Internal: talk_cast.tts.batch, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from talk_cast.config import NarrateConfig
from talk_cast.tts.batch import BatchTTS


def _make_batch(tmp_path: Path, tts_fn: object, api_key: str = "test-key") -> BatchTTS:
    config = NarrateConfig(elevenlabs_api_key=api_key)
    return BatchTTS(config=config, cache_dir=tmp_path, tts_fn=tts_fn)  # type: ignore[arg-type]


@pytest.fixture
def wav_bytes() -> bytes:
    """Minimal 1-second silent WAV bytes."""
    import io
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b"\x00\x00" * 44100)
    return buf.getvalue()


def test_tts_fn_called_once_per_item_on_first_run(
    tmp_path: Path, patch_mp3_to_wav: None, wav_bytes: bytes
) -> None:
    tts_fn = MagicMock(return_value=wav_bytes)
    batch = _make_batch(tmp_path, tts_fn)

    items = [("slide_00", "Hello world"), ("slide_01", "Second slide")]
    batch.synthesize_all(items)

    assert tts_fn.call_count == 2


def test_tts_fn_not_called_on_cache_hit(
    tmp_path: Path, patch_mp3_to_wav: None, wav_bytes: bytes
) -> None:
    tts_fn = MagicMock(return_value=wav_bytes)
    batch = _make_batch(tmp_path, tts_fn)

    items = [("slide_00", "Hello world"), ("slide_01", "Second slide")]
    batch.synthesize_all(items)
    first_call_count = tts_fn.call_count

    # Second run — same batch instance, same items: full cache hit
    batch.synthesize_all(items)
    assert tts_fn.call_count == first_call_count


def test_returned_paths_are_existing_wav_files(
    tmp_path: Path, patch_mp3_to_wav: None, wav_bytes: bytes
) -> None:
    tts_fn = MagicMock(return_value=wav_bytes)
    batch = _make_batch(tmp_path, tts_fn)

    paths = batch.synthesize_all([("slide_00", "Test text")])

    assert len(paths) == 1
    p = paths[0]
    assert p.exists()
    assert p.suffix == ".wav"


def test_cache_dir_contains_mp3_after_synthesis(
    tmp_path: Path, patch_mp3_to_wav: None, wav_bytes: bytes
) -> None:
    tts_fn = MagicMock(return_value=wav_bytes)
    batch = _make_batch(tmp_path, tts_fn)

    batch.synthesize_all([("slide_00", "Cache test")])

    mp3_files = list((tmp_path / "tts").glob("*.mp3"))
    assert len(mp3_files) >= 1


def test_new_batch_instance_hits_disk_cache(
    tmp_path: Path, patch_mp3_to_wav: None, wav_bytes: bytes
) -> None:
    """A fresh BatchTTS pointing at the same cache_dir should not re-call tts_fn."""
    tts_fn = MagicMock(return_value=wav_bytes)

    batch1 = _make_batch(tmp_path, tts_fn)
    batch1.synthesize_all([("slide_00", "Persistent cache")])
    assert tts_fn.call_count == 1

    tts_fn2 = MagicMock(return_value=wav_bytes)
    batch2 = _make_batch(tmp_path, tts_fn2)
    batch2.synthesize_all([("slide_00", "Persistent cache")])
    assert tts_fn2.call_count == 0
