# Filepath: talk-cast/tests/test_config_defaults.py
# Condensed Description: Tests for NarrateConfig and VoiceSettings default values and validation
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_config_defaults
# Dependencies: Internal: talk_cast.config / External: pytest, pydantic
# Exposes: test functions
# Configuration: None
from __future__ import annotations

import pytest
from pydantic import ValidationError

from talk_cast.config import NarrateConfig, VoiceSettings


def test_narrate_config_default_voice_id():
    config = NarrateConfig()
    assert config.voice_id == "JBFqnCBsd6RMkjVDRZzb"


def test_narrate_config_default_model_id():
    config = NarrateConfig()
    assert config.model_id == "eleven_multilingual_v2"


def test_narrate_config_default_leading_silence():
    config = NarrateConfig()
    assert config.leading_silence == pytest.approx(0.4)


def test_narrate_config_default_trailing_silence():
    config = NarrateConfig()
    assert config.trailing_silence == pytest.approx(0.4)


def test_narrate_config_default_per_slide_seconds_min():
    config = NarrateConfig()
    assert config.per_slide_seconds_min == pytest.approx(3.0)


def test_narrate_config_default_fps():
    config = NarrateConfig()
    assert config.fps == 30


def test_narrate_config_default_width():
    config = NarrateConfig()
    assert config.width == 1920


def test_narrate_config_default_height():
    config = NarrateConfig()
    assert config.height == 1080


def test_narrate_config_default_subtitles_off():
    config = NarrateConfig()
    assert config.subtitles == "off"


def test_voice_settings_default_stability():
    vs = VoiceSettings()
    assert vs.stability == pytest.approx(0.5)


def test_voice_settings_default_similarity_boost():
    vs = VoiceSettings()
    assert vs.similarity_boost == pytest.approx(0.75)


def test_narrate_config_invalid_subtitles_raises_validation_error():
    with pytest.raises(ValidationError):
        NarrateConfig(subtitles="invalid")  # type: ignore[call-arg]


def test_narrate_config_subtitles_soft_accepted():
    config = NarrateConfig(subtitles="soft")
    assert config.subtitles == "soft"


def test_narrate_config_subtitles_hard_accepted():
    config = NarrateConfig(subtitles="hard")
    assert config.subtitles == "hard"


def test_narrate_config_per_slide_seconds_max_default_is_none():
    config = NarrateConfig()
    assert config.per_slide_seconds_max is None


def test_narrate_config_music_bed_default_is_none():
    config = NarrateConfig()
    assert config.music_bed is None
