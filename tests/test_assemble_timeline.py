# Filepath: talk-cast/tests/test_assemble_timeline.py
# Condensed Description: Tests for assemble_timeline video-arrange integration (mocked)
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_assemble_timeline
# Dependencies: Internal: talk_cast.assemble.timeline, talk_cast.exceptions / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from talk_cast.assemble.timeline import assemble_timeline
from talk_cast.config import NarrateConfig
from talk_cast.exceptions import AssembleError


def _make_frame_dir(tmp_path: Path, name: str, count: int = 2) -> Path:
    d = tmp_path / name
    d.mkdir()
    for i in range(count):
        (d / f"frame_{i:04d}.png").write_bytes(b"\x89PNG")
    return d


def _build_mock_video_arrange() -> tuple[MagicMock, MagicMock, MagicMock]:
    timeline_instance = MagicMock()
    timeline_class = MagicMock(return_value=timeline_instance)
    video_segment_class = MagicMock()
    module_mock = MagicMock()
    module_mock.Timeline = timeline_class
    module_mock.VideoSegment = video_segment_class
    return module_mock, timeline_instance, video_segment_class


def test_assemble_timeline_calls_timeline_render(tmp_path: Path) -> None:
    frame_dir = _make_frame_dir(tmp_path, "frames_0")
    audio = tmp_path / "mixed.wav"
    audio.write_bytes(b"RIFF")
    output = tmp_path / "out.mp4"
    config = NarrateConfig()

    module_mock, timeline_instance, _ = _build_mock_video_arrange()

    with patch.dict("sys.modules", {"video_arrange": module_mock}):
        result = assemble_timeline([frame_dir], audio, config, output)

    timeline_instance.render.assert_called_once_with(output)
    assert result == output


def test_assemble_timeline_adds_segment_per_dir(tmp_path: Path) -> None:
    dirs = [_make_frame_dir(tmp_path, f"frames_{i}") for i in range(3)]
    audio = tmp_path / "mixed.wav"
    audio.write_bytes(b"RIFF")
    output = tmp_path / "out.mp4"
    config = NarrateConfig()

    module_mock, timeline_instance, _ = _build_mock_video_arrange()

    with patch.dict("sys.modules", {"video_arrange": module_mock}):
        assemble_timeline(dirs, audio, config, output)

    assert timeline_instance.add.call_count == 3


def test_assemble_timeline_uses_config_fps(tmp_path: Path) -> None:
    frame_dir = _make_frame_dir(tmp_path, "frames_0")
    audio = tmp_path / "mixed.wav"
    audio.write_bytes(b"RIFF")
    output = tmp_path / "out.mp4"
    config = NarrateConfig(fps=24, width=1280, height=720)

    module_mock, _, _ = _build_mock_video_arrange()

    with patch.dict("sys.modules", {"video_arrange": module_mock}):
        assemble_timeline([frame_dir], audio, config, output)

    module_mock.Timeline.assert_called_once()
    kwargs = module_mock.Timeline.call_args[1]
    assert kwargs["fps"] == 24
    assert kwargs["width"] == 1280
    assert kwargs["height"] == 720


def test_empty_frame_dir_raises_assemble_error(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    audio = tmp_path / "mixed.wav"
    audio.write_bytes(b"RIFF")
    output = tmp_path / "out.mp4"
    config = NarrateConfig()

    module_mock, _, _ = _build_mock_video_arrange()

    with (
        patch.dict("sys.modules", {"video_arrange": module_mock}),
        pytest.raises(AssembleError, match="No frames found"),
    ):
        assemble_timeline([empty_dir], audio, config, output)


def test_video_arrange_import_error_raises_assemble_error(tmp_path: Path) -> None:
    frame_dir = _make_frame_dir(tmp_path, "frames_0")
    audio = tmp_path / "mixed.wav"
    audio.write_bytes(b"RIFF")
    output = tmp_path / "out.mp4"
    config = NarrateConfig()

    with (
        patch.dict("sys.modules", {"video_arrange": None}),
        pytest.raises(AssembleError, match="video-arrange"),
    ):
        assemble_timeline([frame_dir], audio, config, output)


def test_video_arrange_render_exception_wrapped(tmp_path: Path) -> None:
    frame_dir = _make_frame_dir(tmp_path, "frames_0")
    audio = tmp_path / "mixed.wav"
    audio.write_bytes(b"RIFF")
    output = tmp_path / "out.mp4"
    config = NarrateConfig()

    module_mock, timeline_instance, _ = _build_mock_video_arrange()
    timeline_instance.render.side_effect = RuntimeError("ffmpeg died")

    with (
        patch.dict("sys.modules", {"video_arrange": module_mock}),
        pytest.raises(AssembleError, match="Video assembly failed"),
    ):
        assemble_timeline([frame_dir], audio, config, output)
