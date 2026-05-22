# Filepath: talk-cast/tests/test_tts_elevenlabs.py
# Condensed Description: Tests for the ElevenLabs TTS synthesize() wrapper (SDK mocked)
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_tts_elevenlabs
# Dependencies: Internal: talk_cast.tts.elevenlabs, talk_cast.tts.errors / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from talk_cast.tts.elevenlabs import synthesize
from talk_cast.tts.errors import AuthError, RateLimitError


def _make_mock_client(chunks: list[bytes]) -> MagicMock:
    """Return a mock ElevenLabs client whose convert() yields the given chunks."""
    client_instance = MagicMock()
    client_instance.text_to_speech.convert.return_value = iter(chunks)
    client_class = MagicMock(return_value=client_instance)
    return client_class, client_instance


def test_synthesize_returns_joined_bytes() -> None:
    client_class, _client_instance = _make_mock_client([b"chunk1", b"chunk2"])
    mock_module = MagicMock()
    mock_module.ElevenLabs = client_class

    with patch.dict("sys.modules", {"elevenlabs.client": mock_module}):
        result = synthesize(
            text="Hello",
            voice_id="v1",
            model_id="m1",
            voice_settings={"stability": 0.5},
            api_key="key123",
        )

    assert result == b"chunk1chunk2"


def test_synthesize_passes_correct_args_to_sdk() -> None:
    client_class, client_instance = _make_mock_client([b"audio"])
    mock_module = MagicMock()
    mock_module.ElevenLabs = client_class

    with patch.dict("sys.modules", {"elevenlabs.client": mock_module}):
        synthesize(
            text="Test sentence",
            voice_id="voice_abc",
            model_id="eleven_multilingual_v2",
            voice_settings={"stability": 0.7, "speed": 1.0},
            api_key="sk-test",
        )

    client_instance.text_to_speech.convert.assert_called_once_with(
        text="Test sentence",
        voice_id="voice_abc",
        model_id="eleven_multilingual_v2",
        voice_settings={"stability": 0.7, "speed": 1.0},
        output_format="mp3_44100_128",
    )


def test_synthesize_creates_client_with_api_key() -> None:
    client_class, _ = _make_mock_client([b"x"])
    mock_module = MagicMock()
    mock_module.ElevenLabs = client_class

    with patch.dict("sys.modules", {"elevenlabs.client": mock_module}):
        synthesize(
            text="Hi",
            voice_id="v",
            model_id="m",
            voice_settings={},
            api_key="my-key",
        )

    client_class.assert_called_once_with(api_key="my-key")


def test_401_response_raises_auth_error() -> None:
    client_class, client_instance = _make_mock_client([])
    client_instance.text_to_speech.convert.side_effect = Exception("401 Unauthorized")
    mock_module = MagicMock()
    mock_module.ElevenLabs = client_class

    with patch.dict("sys.modules", {"elevenlabs.client": mock_module}), pytest.raises(AuthError):
        synthesize("text", "v", "m", {}, "key")


def test_rate_limit_response_raises_rate_limit_error() -> None:
    client_class, client_instance = _make_mock_client([])
    client_instance.text_to_speech.convert.side_effect = Exception("429 rate limit exceeded")
    mock_module = MagicMock()
    mock_module.ElevenLabs = client_class

    with (
        patch.dict("sys.modules", {"elevenlabs.client": mock_module}),
        pytest.raises(RateLimitError),
    ):
        synthesize("text", "v", "m", {}, "key")


def test_invalid_api_key_raises_auth_error() -> None:
    client_class, client_instance = _make_mock_client([])
    client_instance.text_to_speech.convert.side_effect = Exception("invalid api key")
    mock_module = MagicMock()
    mock_module.ElevenLabs = client_class

    with patch.dict("sys.modules", {"elevenlabs.client": mock_module}), pytest.raises(AuthError):
        synthesize("text", "v", "m", {}, "key")


def test_other_exception_is_reraised() -> None:
    client_class, client_instance = _make_mock_client([])
    client_instance.text_to_speech.convert.side_effect = RuntimeError("network error")
    mock_module = MagicMock()
    mock_module.ElevenLabs = client_class

    with (
        patch.dict("sys.modules", {"elevenlabs.client": mock_module}),
        pytest.raises(RuntimeError, match="network error"),
    ):
        synthesize("text", "v", "m", {}, "key")


def test_elevenlabs_not_installed_raises_import_error() -> None:
    with (
        patch.dict("sys.modules", {"elevenlabs.client": None}),
        pytest.raises(ImportError, match="elevenlabs"),
    ):
        synthesize("text", "v", "m", {}, "key")
