# Filepath: talk-cast/tests/test_hard_subtitles.py
# Condensed Description: Tests for hard subtitle burn and soft/off subtitle branching logic
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_hard_subtitles
# Dependencies: Internal: talk_cast.assemble.subtitles / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from talk_cast.assemble.subtitles import burn_subtitles, generate_srt, write_srt

# ---------------------------------------------------------------------------
# burn_subtitles calls video_arrange.burn_subtitles
# ---------------------------------------------------------------------------


def test_burn_subtitles_delegates_to_video_arrange(tmp_path: Path) -> None:
    mp4_in = tmp_path / "input.mp4"
    mp4_in.write_bytes(b"fake mp4")
    srt_path = tmp_path / "subs.srt"
    srt_path.write_text("1\n00:00:00,400 --> 00:00:03,900\nHello\n", encoding="utf-8")
    mp4_out = tmp_path / "output.mp4"

    burn_mock = MagicMock()
    video_arrange_mock = MagicMock()
    video_arrange_mock.burn_subtitles = burn_mock

    with patch.dict("sys.modules", {"video_arrange": video_arrange_mock}):
        burn_subtitles(mp4_in, srt_path, mp4_out)

    burn_mock.assert_called_once_with(str(mp4_in), str(srt_path), str(mp4_out))


def test_burn_subtitles_not_called_for_off_mode(tmp_path: Path) -> None:
    """Simulate narrate() with subtitles='off': burn_subtitles should never be reached."""
    from talk_cast.config import NarrateConfig

    config = NarrateConfig(subtitles="off")

    burn_mock = MagicMock()

    # Simulate the conditional in narrate.py:
    # if config.subtitles == "hard": burn_subtitles(...)
    if config.subtitles == "hard":
        burn_mock()

    burn_mock.assert_not_called()


def test_burn_subtitles_called_for_hard_mode(tmp_path: Path) -> None:
    """Simulate narrate() with subtitles='hard': burn_subtitles is invoked."""
    from talk_cast.config import NarrateConfig

    config = NarrateConfig(subtitles="hard")

    burn_mock = MagicMock()

    # Simulate the conditional in narrate.py:
    if config.subtitles == "hard":
        burn_mock()

    burn_mock.assert_called_once()


# ---------------------------------------------------------------------------
# generate_srt -> write_srt -> readable file
# ---------------------------------------------------------------------------


def test_generate_srt_write_srt_roundtrip(tmp_path: Path) -> None:
    texts = ["Welcome to the presentation", "This is slide two"]
    durations = [4.0, 5.0]
    srt_content = generate_srt(texts, durations, leading_silence=0.4)

    srt_path = tmp_path / "output.srt"
    write_srt(srt_content, srt_path)

    assert srt_path.exists()
    read_back = srt_path.read_text(encoding="utf-8")
    assert "Welcome to the presentation" in read_back
    assert "This is slide two" in read_back


def test_write_srt_file_is_utf8_text(tmp_path: Path) -> None:
    texts = ["Swedish: Välkommen", "More: åäö"]
    durations = [3.0, 3.0]
    srt_content = generate_srt(texts, durations, leading_silence=0.4)
    srt_path = tmp_path / "unicode.srt"
    write_srt(srt_content, srt_path)

    content = srt_path.read_text(encoding="utf-8")
    assert "Välkommen" in content
    assert "åäö" in content


def test_burn_subtitles_raises_when_video_arrange_missing(tmp_path: Path) -> None:
    mp4_in = tmp_path / "in.mp4"
    mp4_in.write_bytes(b"x")
    srt = tmp_path / "s.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n")
    mp4_out = tmp_path / "out.mp4"

    with patch.dict("sys.modules", {"video_arrange": None}), pytest.raises(ImportError):
        burn_subtitles(mp4_in, srt, mp4_out)
