# Filepath: talk-cast/tests/test_subtitle_srt.py
# Condensed Description: Tests for generate_srt timestamp alignment and write_srt disk output
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_subtitle_srt
# Dependencies: Internal: talk_cast.assemble.subtitles / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from pathlib import Path

from talk_cast.assemble.subtitles import generate_srt, write_srt


def _parse_srt_blocks(srt: str) -> list[dict[str, str]]:
    """Parse SRT into list of {index, timecode, text} dicts."""
    blocks = []
    raw_blocks = srt.strip().split("\n\n")
    for block in raw_blocks:
        if not block.strip():
            continue
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            blocks.append({"index": lines[0], "timecode": lines[1], "text": "\n".join(lines[2:])})
    return blocks


def test_generate_srt_returns_nonempty_string():
    result = generate_srt(["Hello world"], [5.0], leading_silence=0.4)
    assert isinstance(result, str)
    assert result.strip()


def test_first_subtitle_block_starts_with_1():
    result = generate_srt(["First slide"], [4.0], leading_silence=0.4)
    blocks = _parse_srt_blocks(result)
    assert blocks[0]["index"] == "1"


def test_slide_0_starts_at_leading_silence():
    leading = 0.4
    result = generate_srt(["Slide zero text"], [5.0], leading_silence=leading)
    blocks = _parse_srt_blocks(result)
    timecode = blocks[0]["timecode"]
    start_part = timecode.split(" --> ")[0]
    # 0.4 seconds -> 00:00:00,400
    assert start_part == "00:00:00,400"


def test_slide_1_starts_at_duration_0_plus_leading_silence():
    durations = [4.0, 6.0]
    leading = 0.5
    result = generate_srt(["First", "Second"], durations, leading_silence=leading)
    blocks = _parse_srt_blocks(result)
    timecode = blocks[1]["timecode"]
    start_part = timecode.split(" --> ")[0]
    # slide 1 starts at duration[0] + leading_silence = 4.0 + 0.5 = 4.5
    # -> 00:00:04,500
    assert start_part == "00:00:04,500"


def test_each_block_contains_corresponding_text():
    texts = ["Alpha text", "Beta text", "Gamma text"]
    durations = [3.0, 4.0, 5.0]
    result = generate_srt(texts, durations, leading_silence=0.4)
    blocks = _parse_srt_blocks(result)
    for block, expected_text in zip(blocks, texts, strict=True):
        assert expected_text in block["text"]


def test_number_of_blocks_matches_number_of_slides():
    texts = ["A", "B", "C", "D"]
    durations = [3.0] * 4
    result = generate_srt(texts, durations, leading_silence=0.4)
    blocks = _parse_srt_blocks(result)
    assert len(blocks) == 4


def test_write_srt_creates_readable_file(tmp_path: Path) -> None:
    srt_content = generate_srt(["Hello subtitle"], [4.0], leading_silence=0.4)
    srt_path = tmp_path / "output.srt"
    write_srt(srt_content, srt_path)
    assert srt_path.exists()
    read_back = srt_path.read_text(encoding="utf-8")
    assert "Hello subtitle" in read_back


def test_write_srt_preserves_content_exactly(tmp_path: Path) -> None:
    srt_content = "1\n00:00:00,400 --> 00:00:03,900\nTest line\n"
    srt_path = tmp_path / "test.srt"
    write_srt(srt_content, srt_path)
    assert srt_path.read_text(encoding="utf-8") == srt_content
