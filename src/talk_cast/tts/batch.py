# Filepath: talk-cast/src/talk_cast/tts/batch.py
# Condensed Description: Parallel TTS synthesis with MP3-to-WAV conversion and disk caching
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.tts.batch
# Dependencies: Internal: talk_cast.config, talk_cast.tts.cache, talk_cast.tts.elevenlabs / External: none
# Exposes: BatchTTS
# Configuration: NarrateConfig
from __future__ import annotations

import asyncio
import logging
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

from talk_cast.config import NarrateConfig
from talk_cast.tts.cache import TTSCache

logger = logging.getLogger(__name__)

_SynthFn = Callable[[str, str, str, dict, str], bytes]


def _mp3_to_wav(mp3_path: Path, wav_path: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp3_path), str(wav_path)],
        check=True,
        capture_output=True,
    )


class BatchTTS:
    def __init__(
        self,
        config: NarrateConfig,
        cache_dir: Path,
        tts_fn: _SynthFn | None = None,
    ) -> None:
        self._config = config
        self._cache = TTSCache(cache_dir)
        self._wav_dir = cache_dir / "wav"
        self._wav_dir.mkdir(parents=True, exist_ok=True)
        if tts_fn is None:
            from talk_cast.tts.elevenlabs import synthesize

            self._tts_fn: _SynthFn = synthesize
        else:
            self._tts_fn = tts_fn

    def _api_key(self) -> str:
        key = self._config.elevenlabs_api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        if not key:
            raise ValueError(
                "No ElevenLabs API key. Set ELEVENLABS_API_KEY or NarrateConfig.elevenlabs_api_key."
            )
        return key

    def _synth_one(self, slide_id: str, text: str) -> Path:
        vs = self._config.voice_settings
        key = TTSCache.make_key(text, self._config.voice_id, self._config.model_id, vs)
        mp3_path = self._cache.get(key)
        if mp3_path is None:
            logger.debug(f"TTS cache miss: {slide_id}")
            mp3_bytes = self._tts_fn(
                text,
                self._config.voice_id,
                self._config.model_id,
                vs.model_dump(),
                self._api_key(),
            )
            mp3_path = self._cache.put(key, mp3_bytes)
        else:
            logger.debug(f"TTS cache hit: {slide_id}")

        wav_path = self._wav_dir / f"{key}.wav"
        if not wav_path.exists():
            _mp3_to_wav(mp3_path, wav_path)
        return wav_path

    async def _synth_all_async(self, items: list[tuple[str, str]]) -> list[Path]:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, self._synth_one, slide_id, text) for slide_id, text in items
        ]
        return list(await asyncio.gather(*tasks))

    def synthesize_all(self, items: list[tuple[str, str]]) -> list[Path]:
        return asyncio.run(self._synth_all_async(items))
