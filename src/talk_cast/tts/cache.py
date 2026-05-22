# Filepath: talk-cast/src/talk_cast/tts/cache.py
# Condensed Description: Disk-backed TTS cache keyed by sha256 of synthesis parameters
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.tts.cache
# Dependencies: Internal: talk_cast.config / External: none
# Exposes: TTSCache
# Configuration: NarrateConfig
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from talk_cast.config import VoiceSettings


class TTSCache:
    def __init__(self, cache_dir: Path) -> None:
        self._dir = cache_dir / "tts"
        self._dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def make_key(text: str, voice_id: str, model_id: str, voice_settings: VoiceSettings) -> str:
        settings_json = json.dumps(voice_settings.model_dump(), sort_keys=True)
        raw = f"{voice_id}|{model_id}|{settings_json}|{text}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, key: str) -> Path | None:
        p = self._dir / f"{key}.mp3"
        return p if p.exists() else None

    def put(self, key: str, data: bytes) -> Path:
        p = self._dir / f"{key}.mp3"
        p.write_bytes(data)
        return p
