# Filepath: talk-cast/src/talk_cast/tts/elevenlabs.py
# Condensed Description: ElevenLabs TTS synthesis; sole importer of the elevenlabs SDK
# Architecture Layer: integration
# Environment: Local
# Script Hierarchy: talk_cast.tts.elevenlabs
# Dependencies: Internal: talk_cast.tts.errors / External: elevenlabs (lazy)
# Exposes: synthesize
# Configuration: NarrateConfig
from __future__ import annotations

import logging

from talk_cast.tts.errors import AuthError, RateLimitError

logger = logging.getLogger(__name__)


def synthesize(
    text: str,
    voice_id: str,
    model_id: str,
    voice_settings: dict,
    api_key: str,
) -> bytes:
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError as exc:
        raise ImportError(
            "elevenlabs package is not installed. Run: pip install elevenlabs"
        ) from exc

    client = ElevenLabs(api_key=api_key)
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            voice_settings=voice_settings,
            output_format="mp3_44100_128",
        )
        return b"".join(audio)
    except (AuthError, RateLimitError):
        raise
    except Exception as exc:
        msg = str(exc).lower()
        if "401" in msg or "unauthorized" in msg or "invalid api key" in msg:
            raise AuthError(f"ElevenLabs authentication failed: {exc}") from exc
        if "429" in msg or "rate limit" in msg:
            raise RateLimitError(f"ElevenLabs rate limit exceeded: {exc}") from exc
        raise
