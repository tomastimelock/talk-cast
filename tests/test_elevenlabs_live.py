# Filepath: talk-cast/tests/test_elevenlabs_live.py
# Condensed Description: Live ElevenLabs TTS integration test (skipped unless env vars set)
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_elevenlabs_live
# Dependencies: Internal: talk_cast.tts.elevenlabs, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    not (os.environ.get("ELEVENLABS_API_KEY") and os.environ.get("TALK_CAST_RUN_LIVE_TTS")),
    reason="Live TTS test requires ELEVENLABS_API_KEY and TALK_CAST_RUN_LIVE_TTS=1",
)


def test_live_tts_returns_mp3_bytes() -> None:
    """One short TTS call to verify ElevenLabs integration. ~50 chars of quota."""
    from talk_cast.config import VoiceSettings
    from talk_cast.tts.elevenlabs import synthesize

    api_key = os.environ["ELEVENLABS_API_KEY"]
    result = synthesize(
        text="Hello.",
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings().model_dump(),
        api_key=api_key,
    )
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_live_tts_result_is_nontrivial() -> None:
    """Verify the returned bytes are substantial enough to be real audio."""
    from talk_cast.config import VoiceSettings
    from talk_cast.tts.elevenlabs import synthesize

    api_key = os.environ["ELEVENLABS_API_KEY"]
    result = synthesize(
        text="Testing integration call.",
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings().model_dump(),
        api_key=api_key,
    )
    assert len(result) > 1000
