# Filepath: talk-cast/src/talk_cast/config.py
# Condensed Description: Pydantic v2 configuration model for the narrate pipeline
# Architecture Layer: domain
# Environment: Local
# Script Hierarchy: talk_cast.config
# Dependencies: Internal: none / External: pydantic
# Exposes: VoiceSettings, NarrateConfig
# Configuration: NarrateConfig
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class VoiceSettings(BaseModel):
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    speed: float = 1.0


class NarrateConfig(BaseModel):
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_api_key: str | None = None
    model_id: str = "eleven_multilingual_v2"
    voice_settings: VoiceSettings = Field(default_factory=VoiceSettings)

    per_slide_seconds_min: float = 3.0
    per_slide_seconds_max: float | None = None
    transition_duration: float = 0.5
    leading_silence: float = 0.4
    trailing_silence: float = 0.4

    music_bed: Path | None = None
    music_bed_db: float = -20.0
    music_duck_db: float = -8.0
    music_fade_in: float = 1.5
    music_fade_out: float = 2.0

    fps: int = 30
    width: int = 1920
    height: int = 1080
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"

    cache_dir: Path | None = None
    reuse_audio_cache: bool = True
    reuse_frame_cache: bool = True

    subtitles: Literal["off", "soft", "hard"] = "off"

    verbose: bool = False
