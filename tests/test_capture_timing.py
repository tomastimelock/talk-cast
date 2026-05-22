# Filepath: talk-cast/tests/test_capture_timing.py
# Condensed Description: Tests for compute_slide_duration pacing logic
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_capture_timing
# Dependencies: Internal: talk_cast.capture.timing, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from talk_cast.capture.timing import compute_slide_duration
from talk_cast.config import NarrateConfig


def test_duration_includes_leading_and_trailing_silence(
    silence_wav: Callable[[float], Path],
) -> None:
    wav = silence_wav(2.0)
    config = NarrateConfig(leading_silence=0.4, trailing_silence=0.4, per_slide_seconds_min=0.0)
    result = compute_slide_duration(wav, config)
    assert result == pytest.approx(2.0 + 0.4 + 0.4, abs=0.01)


def test_duration_meets_minimum_even_for_very_short_audio(
    silence_wav: Callable[[float], Path],
) -> None:
    wav = silence_wav(0.01)
    config = NarrateConfig(
        leading_silence=0.1,
        trailing_silence=0.1,
        per_slide_seconds_min=5.0,
        per_slide_seconds_max=None,
    )
    result = compute_slide_duration(wav, config)
    assert result >= 5.0


def test_duration_respects_max_when_set(
    silence_wav: Callable[[float], Path],
) -> None:
    wav = silence_wav(10.0)
    config = NarrateConfig(
        leading_silence=0.4,
        trailing_silence=0.4,
        per_slide_seconds_min=0.0,
        per_slide_seconds_max=8.0,
    )
    result = compute_slide_duration(wav, config)
    assert result <= 8.0 + 0.01


def test_duration_no_upper_bound_when_max_is_none(
    silence_wav: Callable[[float], Path],
) -> None:
    wav = silence_wav(30.0)
    config = NarrateConfig(
        leading_silence=0.4,
        trailing_silence=0.4,
        per_slide_seconds_min=0.0,
        per_slide_seconds_max=None,
    )
    result = compute_slide_duration(wav, config)
    assert result > 30.0


def test_duration_with_normal_audio_exceeds_audio_length(
    silence_wav: Callable[[float], Path],
) -> None:
    wav = silence_wav(3.0)
    config = NarrateConfig(leading_silence=0.4, trailing_silence=0.4, per_slide_seconds_min=0.0)
    result = compute_slide_duration(wav, config)
    assert result > 3.0


def test_min_applied_when_audio_plus_padding_is_below_min(
    silence_wav: Callable[[float], Path],
) -> None:
    # audio(0.5) + leading(0.2) + trailing(0.2) = 0.9 < min(3.0)
    wav = silence_wav(0.5)
    config = NarrateConfig(
        leading_silence=0.2,
        trailing_silence=0.2,
        per_slide_seconds_min=3.0,
        per_slide_seconds_max=None,
    )
    result = compute_slide_duration(wav, config)
    assert result == pytest.approx(3.0, abs=0.01)
