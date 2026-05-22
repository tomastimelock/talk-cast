# Filepath: talk-cast/tests/test_cache_invalidation.py
# Condensed Description: Tests that only changed-text slides trigger fresh TTS synthesis
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_cache_invalidation
# Dependencies: Internal: talk_cast.tts.batch, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

import io
import wave
from pathlib import Path
from unittest.mock import MagicMock

from talk_cast.config import NarrateConfig
from talk_cast.tts.batch import BatchTTS


def _make_silence_wav_bytes() -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b"\x00\x00" * 44100)
    return buf.getvalue()


def _make_batch(tmp_path: Path, tts_fn: object) -> BatchTTS:
    config = NarrateConfig(elevenlabs_api_key="test-key")
    return BatchTTS(config=config, cache_dir=tmp_path, tts_fn=tts_fn)  # type: ignore[arg-type]


def test_only_changed_slide_triggers_tts_on_second_run(
    tmp_path: Path, patch_mp3_to_wav: None
) -> None:
    """
    Run 1: 2 slides -> tts_fn called twice.
    Change second slide's text.
    Run 2: first slide hits cache, second is a miss -> tts_fn called once more.
    Total calls: 3.
    """
    wav_bytes = _make_silence_wav_bytes()
    tts_fn = MagicMock(return_value=wav_bytes)
    batch = _make_batch(tmp_path, tts_fn)

    original_items = [
        ("slide_00", "First slide text"),
        ("slide_01", "Second slide text"),
    ]
    batch.synthesize_all(original_items)
    assert tts_fn.call_count == 2

    changed_items = [
        ("slide_00", "First slide text"),  # unchanged -> cache hit
        ("slide_01", "Modified second text"),  # changed -> cache miss
    ]
    batch.synthesize_all(changed_items)
    assert tts_fn.call_count == 3


def test_unchanged_slides_do_not_trigger_tts_on_second_run(
    tmp_path: Path, patch_mp3_to_wav: None
) -> None:
    wav_bytes = _make_silence_wav_bytes()
    tts_fn = MagicMock(return_value=wav_bytes)
    batch = _make_batch(tmp_path, tts_fn)

    items = [("slide_00", "Stable text"), ("slide_01", "Also stable")]
    batch.synthesize_all(items)
    first_count = tts_fn.call_count

    batch.synthesize_all(items)
    assert tts_fn.call_count == first_count


def test_all_new_slides_trigger_full_synthesis(tmp_path: Path, patch_mp3_to_wav: None) -> None:
    wav_bytes = _make_silence_wav_bytes()
    tts_fn = MagicMock(return_value=wav_bytes)
    batch = _make_batch(tmp_path, tts_fn)

    items_a = [("slide_00", "Run A slide 0"), ("slide_01", "Run A slide 1")]
    batch.synthesize_all(items_a)
    assert tts_fn.call_count == 2

    items_b = [("slide_00", "Run B slide 0"), ("slide_01", "Run B slide 1")]
    batch.synthesize_all(items_b)
    assert tts_fn.call_count == 4
