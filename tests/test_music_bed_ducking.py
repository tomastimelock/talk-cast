# Filepath: talk-cast/tests/test_music_bed_ducking.py
# Condensed Description: Tests that mix_audio invokes set_music_bed only when config.music_bed is set
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_music_bed_ducking
# Dependencies: Internal: talk_cast.assemble.audio_mix, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

import wave
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, patch

from talk_cast.config import NarrateConfig


def _make_silence_wav(path: Path, duration_sec: float = 1.0) -> Path:
    n_frames = int(44100 * duration_sec)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(b"\x00\x00" * n_frames)
    return path


def _build_mock_audio_arrange() -> tuple[MagicMock, MagicMock, MagicMock]:
    """Return (module_mock, timeline_instance, music_bed_class)."""
    timeline_instance = MagicMock()
    timeline_class = MagicMock(return_value=timeline_instance)
    segment_class = MagicMock(return_value=MagicMock())
    music_bed_instance = MagicMock()
    music_bed_class = MagicMock(return_value=music_bed_instance)

    module_mock = MagicMock()
    module_mock.AudioTimeline = timeline_class
    module_mock.Segment = segment_class
    module_mock.MusicBed = music_bed_class

    return module_mock, timeline_instance, music_bed_class


def test_set_music_bed_called_when_music_bed_configured(
    tmp_path: Path, silence_wav: Callable[[float], Path]
) -> None:
    wav = silence_wav(1.0)
    music_file = tmp_path / "music.mp3"
    music_file.write_bytes(b"fake audio data")
    output = tmp_path / "mixed.wav"

    config = NarrateConfig(music_bed=music_file, music_bed_db=-20.0)

    module_mock, timeline_instance, _music_bed_class = _build_mock_audio_arrange()

    with patch.dict("sys.modules", {"audio_arrange": module_mock}):
        from talk_cast.assemble.audio_mix import mix_audio

        mix_audio([wav], [3.0], config, output)

    timeline_instance.set_music_bed.assert_called_once()


def test_set_music_bed_not_called_when_music_bed_is_none(
    tmp_path: Path, silence_wav: Callable[[float], Path]
) -> None:
    wav = silence_wav(1.0)
    output = tmp_path / "mixed.wav"

    config = NarrateConfig(music_bed=None)

    module_mock, timeline_instance, _music_bed_class = _build_mock_audio_arrange()

    with patch.dict("sys.modules", {"audio_arrange": module_mock}):
        from talk_cast.assemble.audio_mix import mix_audio

        mix_audio([wav], [3.0], config, output)

    timeline_instance.set_music_bed.assert_not_called()


def test_music_bed_class_receives_correct_path(
    tmp_path: Path, silence_wav: Callable[[float], Path]
) -> None:
    wav = silence_wav(1.0)
    music_file = tmp_path / "music.wav"
    music_file.write_bytes(b"fake")
    output = tmp_path / "mixed.wav"

    config = NarrateConfig(music_bed=music_file, music_bed_db=-18.0)

    module_mock, _timeline_instance, music_bed_class = _build_mock_audio_arrange()

    with patch.dict("sys.modules", {"audio_arrange": module_mock}):
        from talk_cast.assemble.audio_mix import mix_audio

        mix_audio([wav], [3.0], config, output)

    call_kwargs = music_bed_class.call_args
    assert call_kwargs is not None
    # path should be the music_file
    assert call_kwargs.kwargs.get("path") == music_file or call_kwargs.args[0] == music_file


def test_timeline_render_always_called(
    tmp_path: Path, silence_wav: Callable[[float], Path]
) -> None:
    wav = silence_wav(1.0)
    output = tmp_path / "mixed.wav"

    config = NarrateConfig(music_bed=None)

    module_mock, timeline_instance, _ = _build_mock_audio_arrange()

    with patch.dict("sys.modules", {"audio_arrange": module_mock}):
        from talk_cast.assemble.audio_mix import mix_audio

        mix_audio([wav], [3.0], config, output)

    timeline_instance.render.assert_called_once_with(output)
