# Filepath: talk-cast/src/talk_cast/capture/timing.py
# Condensed Description: Computes per-slide video duration from WAV audio length and config pacing
# Architecture Layer: domain
# Environment: Local
# Script Hierarchy: talk_cast.capture.timing
# Dependencies: Internal: talk_cast.config / External: none
# Exposes: compute_slide_duration
# Configuration: NarrateConfig
from __future__ import annotations

import wave
from pathlib import Path

from talk_cast.config import NarrateConfig


def compute_slide_duration(audio_path: Path, config: NarrateConfig) -> float:
    with wave.open(str(audio_path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
    audio_len = frames / rate
    duration = audio_len + config.leading_silence + config.trailing_silence
    duration = max(duration, config.per_slide_seconds_min)
    if config.per_slide_seconds_max is not None:
        duration = min(duration, config.per_slide_seconds_max)
    return duration
