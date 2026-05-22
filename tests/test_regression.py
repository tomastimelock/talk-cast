# Filepath: talk-cast/tests/test_regression.py
# Condensed Description: Regression tests for specific bugs identified during development
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_regression
# Dependencies: Internal: talk_cast.narration_source, talk_cast.tts.cache, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from pathlib import Path

from deck_spec.models import Slide

from talk_cast.narration_source import get_narration_text

# ---------------------------------------------------------------------------
# Regression 1: blank slide with title=None must return "" without raising
# ---------------------------------------------------------------------------


def test_blank_slide_with_no_title_returns_empty_string() -> None:
    """get_narration_text(Slide(layout='blank', title=None)) must not raise."""
    slide = Slide(layout="blank", title=None)
    result = get_narration_text(slide)
    assert result == ""


# ---------------------------------------------------------------------------
# Regression 2: slide with no title, no notes, no narration must not raise
# ---------------------------------------------------------------------------


def test_slide_with_no_content_fields_does_not_raise() -> None:
    """A completely empty slide must return a string (possibly empty), never raise."""
    slide = Slide(layout="content")
    result = get_narration_text(slide)
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Regression 3: TTSCache.get() returns None for stale / deleted .mp3 entries
# ---------------------------------------------------------------------------


def test_tts_cache_get_returns_none_for_deleted_mp3(tmp_path: Path) -> None:
    """
    If the .mp3 file has been deleted after put(), TTSCache.get() should return
    None so that the caller regenerates the audio cleanly.
    """
    from talk_cast.config import VoiceSettings
    from talk_cast.tts.cache import TTSCache

    cache = TTSCache(tmp_path)
    vs = VoiceSettings()
    key = TTSCache.make_key("Stale entry text", "v-id", "m-id", vs)

    # Write and then delete the cached file to simulate a stale entry
    mp3_path = cache.put(key, b"fake mp3 bytes")
    assert mp3_path.exists()

    mp3_path.unlink()

    result = cache.get(key)
    assert result is None


# ---------------------------------------------------------------------------
# Regression 4: NarrateConfig preserves multilingual model_id
# ---------------------------------------------------------------------------


def test_narrate_config_preserves_multilingual_model_id() -> None:
    """NarrateConfig(model_id='eleven_multilingual_v2') must store the value unchanged."""
    from talk_cast.config import NarrateConfig

    config = NarrateConfig(model_id="eleven_multilingual_v2")
    assert config.model_id == "eleven_multilingual_v2"
