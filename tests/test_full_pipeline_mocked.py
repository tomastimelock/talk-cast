# Filepath: talk-cast/tests/test_full_pipeline_mocked.py
# Condensed Description: End-to-end narrate() smoke test with all external calls mocked
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_full_pipeline_mocked
# Dependencies: Internal: talk_cast.narrate, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

import io
import shutil
import wave
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from deck_spec.models import Deck, Slide

from talk_cast.config import NarrateConfig

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None,
    reason="ffmpeg not found — skipping full pipeline test",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WHITE_PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)

_DUMMY_MP4 = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"


def _make_silence_wav_bytes(duration_sec: float = 1.0) -> bytes:
    buf = io.BytesIO()
    n_frames = int(44100 * duration_sec)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b"\x00\x00" * n_frames)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def small_deck() -> Deck:
    return Deck(
        title="Mocked Pipeline",
        slides=[
            Slide(layout="title", title="Title Slide", notes="Opening."),
            Slide(layout="content", title="Content", body="Body text.", notes="Main content."),
        ],
    )


@pytest.fixture
def mock_tts_fn() -> Callable:
    wav_bytes = _make_silence_wav_bytes(1.0)

    def _synth(text, voice_id, model_id, voice_settings, api_key):
        return wav_bytes

    return _synth


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_narrate_returns_a_path(
    tmp_path: Path,
    small_deck: Deck,
    mock_tts_fn: Callable,
    patch_mp3_to_wav: None,
) -> None:
    output = tmp_path / "output.mp4"
    config = NarrateConfig(
        elevenlabs_api_key="fake-key",
        cache_dir=tmp_path / "cache",
    )

    def fake_capture_frames(slide_html_path, duration, fps, output_dir, cache_dir, reuse=True):
        frame_dir = cache_dir / "frames" / "fake_key"
        frame_dir.mkdir(parents=True, exist_ok=True)
        png = frame_dir / "frame_0000.png"
        png.write_bytes(_WHITE_PNG_1X1)
        return [png]

    def fake_mix_audio(narration_paths, durations, config, output):
        shutil.copy(narration_paths[0], output)
        return output

    def fake_assemble_timeline(slide_frame_dirs, mixed_audio, config, output):
        output.write_bytes(_DUMMY_MP4)
        return output

    with (
        patch("talk_cast.tts.batch._mp3_to_wav", side_effect=shutil.copy),
        patch("talk_cast.capture.frames.capture_slide_frames", side_effect=fake_capture_frames),
        patch("talk_cast.assemble.audio_mix.mix_audio", side_effect=fake_mix_audio),
        patch("talk_cast.assemble.timeline.assemble_timeline", side_effect=fake_assemble_timeline),
    ):
        from talk_cast.tts.batch import BatchTTS

        original_init = BatchTTS.__init__

        def patched_init(self, config, cache_dir, tts_fn=None):
            original_init(self, config, cache_dir, tts_fn=mock_tts_fn)

        with patch.object(BatchTTS, "__init__", patched_init):
            from talk_cast.narrate import narrate

            result = narrate(small_deck, output, config=config)

    assert isinstance(result, Path)


def test_narrate_output_file_exists(
    tmp_path: Path,
    small_deck: Deck,
    mock_tts_fn: Callable,
    patch_mp3_to_wav: None,
) -> None:
    output = tmp_path / "output.mp4"
    config = NarrateConfig(
        elevenlabs_api_key="fake-key",
        cache_dir=tmp_path / "cache",
    )

    def fake_capture_frames(slide_html_path, duration, fps, output_dir, cache_dir, reuse=True):
        frame_dir = cache_dir / "frames" / "fake_key2"
        frame_dir.mkdir(parents=True, exist_ok=True)
        png = frame_dir / "frame_0000.png"
        png.write_bytes(_WHITE_PNG_1X1)
        return [png]

    def fake_mix_audio(narration_paths, durations, config, output):
        shutil.copy(narration_paths[0], output)
        return output

    def fake_assemble_timeline(slide_frame_dirs, mixed_audio, config, output):
        output.write_bytes(_DUMMY_MP4)
        return output

    with (
        patch("talk_cast.capture.frames.capture_slide_frames", side_effect=fake_capture_frames),
        patch("talk_cast.assemble.audio_mix.mix_audio", side_effect=fake_mix_audio),
        patch("talk_cast.assemble.timeline.assemble_timeline", side_effect=fake_assemble_timeline),
    ):
        from talk_cast.tts.batch import BatchTTS

        original_init = BatchTTS.__init__

        def patched_init(self, config, cache_dir, tts_fn=None):
            original_init(self, config, cache_dir, tts_fn=mock_tts_fn)

        with patch.object(BatchTTS, "__init__", patched_init):
            from talk_cast.narrate import narrate

            narrate(small_deck, output, config=config)

    assert output.exists()


def test_elevenlabs_sdk_not_called_during_mocked_pipeline(
    tmp_path: Path,
    small_deck: Deck,
    mock_tts_fn: Callable,
    patch_mp3_to_wav: None,
) -> None:
    """Verify ElevenLabs is never imported or invoked when using a mock tts_fn."""
    output = tmp_path / "output.mp4"
    config = NarrateConfig(
        elevenlabs_api_key="fake-key",
        cache_dir=tmp_path / "cache",
    )

    elevenlabs_synth_mock = MagicMock()

    def fake_capture_frames(slide_html_path, duration, fps, output_dir, cache_dir, reuse=True):
        frame_dir = cache_dir / "frames" / "fake_key3"
        frame_dir.mkdir(parents=True, exist_ok=True)
        png = frame_dir / "frame_0000.png"
        png.write_bytes(_WHITE_PNG_1X1)
        return [png]

    def fake_mix_audio(narration_paths, durations, config, output):
        shutil.copy(narration_paths[0], output)
        return output

    def fake_assemble_timeline(slide_frame_dirs, mixed_audio, config, output):
        output.write_bytes(_DUMMY_MP4)
        return output

    with (
        patch("talk_cast.capture.frames.capture_slide_frames", side_effect=fake_capture_frames),
        patch("talk_cast.assemble.audio_mix.mix_audio", side_effect=fake_mix_audio),
        patch("talk_cast.assemble.timeline.assemble_timeline", side_effect=fake_assemble_timeline),
        patch("talk_cast.tts.elevenlabs.synthesize", elevenlabs_synth_mock),
    ):
        from talk_cast.tts.batch import BatchTTS

        original_init = BatchTTS.__init__

        def patched_init(self, config, cache_dir, tts_fn=None):
            original_init(self, config, cache_dir, tts_fn=mock_tts_fn)

        with patch.object(BatchTTS, "__init__", patched_init):
            from talk_cast.narrate import narrate

            narrate(small_deck, output, config=config)

    elevenlabs_synth_mock.assert_not_called()
