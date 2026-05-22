# Filepath: talk-cast/tests/test_capture_frames.py
# Condensed Description: Tests for capture_slide_frames frame cache hit/miss and error handling
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_capture_frames
# Dependencies: Internal: talk_cast.capture.frames, talk_cast.exceptions / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from talk_cast.capture.frames import _frame_cache_key, capture_slide_frames
from talk_cast.exceptions import CaptureError


def _make_html_file(tmp_path: Path, content: str = "<html>slide</html>") -> Path:
    p = tmp_path / "slide.html"
    p.write_text(content, encoding="utf-8")
    return p


def _plant_cache_frames(cache_dir: Path, key: str, count: int = 2) -> list[Path]:
    frame_dir = cache_dir / "frames" / key
    frame_dir.mkdir(parents=True)
    frames = []
    for i in range(count):
        p = frame_dir / f"frame_{i:04d}.png"
        p.write_bytes(b"\x89PNG")
        frames.append(p)
    return frames


def test_cache_key_is_deterministic(tmp_path: Path) -> None:
    k1 = _frame_cache_key("<html>a</html>", 3.0, 30)
    k2 = _frame_cache_key("<html>a</html>", 3.0, 30)
    assert k1 == k2


def test_cache_key_changes_with_content(tmp_path: Path) -> None:
    k1 = _frame_cache_key("<html>a</html>", 3.0, 30)
    k2 = _frame_cache_key("<html>b</html>", 3.0, 30)
    assert k1 != k2


def test_cache_key_changes_with_duration() -> None:
    k1 = _frame_cache_key("<html>x</html>", 3.0, 30)
    k2 = _frame_cache_key("<html>x</html>", 5.0, 30)
    assert k1 != k2


def test_cache_key_changes_with_fps() -> None:
    k1 = _frame_cache_key("<html>x</html>", 3.0, 24)
    k2 = _frame_cache_key("<html>x</html>", 3.0, 30)
    assert k1 != k2


def test_cache_hit_returns_existing_frames(tmp_path: Path) -> None:
    html_file = _make_html_file(tmp_path)
    cache_dir = tmp_path / "cache"
    key = _frame_cache_key(html_file.read_text(), 3.0, 30)
    planted = _plant_cache_frames(cache_dir, key, count=3)

    result = capture_slide_frames(
        slide_html_path=html_file,
        duration=3.0,
        fps=30,
        output_dir=tmp_path / "out",
        cache_dir=cache_dir,
        reuse=True,
    )

    assert result == planted


def test_cache_hit_skips_web_overlay(tmp_path: Path) -> None:
    html_file = _make_html_file(tmp_path)
    cache_dir = tmp_path / "cache"
    key = _frame_cache_key(html_file.read_text(), 3.0, 30)
    _plant_cache_frames(cache_dir, key, count=1)

    with patch.dict("sys.modules", {"web_overlay": MagicMock()}) as patched:
        capture_slide_frames(
            slide_html_path=html_file,
            duration=3.0,
            fps=30,
            output_dir=tmp_path / "out",
            cache_dir=cache_dir,
            reuse=True,
        )
        # If cache hit, web_overlay.capture_frames should NOT be called
        web_mod = patched["web_overlay"]
        web_mod.capture_frames.assert_not_called()


def test_cache_miss_calls_web_overlay(tmp_path: Path) -> None:
    html_file = _make_html_file(tmp_path, "<html>new slide</html>")
    cache_dir = tmp_path / "cache"

    mock_web = MagicMock()

    def fake_capture_frames(html_path: Path, duration: float, fps: int, output_dir: Path) -> None:
        (output_dir / "frame_0000.png").write_bytes(b"\x89PNG")

    mock_web.capture_frames = fake_capture_frames

    with patch.dict("sys.modules", {"web_overlay": mock_web}):
        result = capture_slide_frames(
            slide_html_path=html_file,
            duration=4.0,
            fps=30,
            output_dir=tmp_path / "out",
            cache_dir=cache_dir,
            reuse=True,
        )

    assert len(result) == 1
    assert result[0].name == "frame_0000.png"


def test_reuse_false_bypasses_cache(tmp_path: Path) -> None:
    html_file = _make_html_file(tmp_path)
    cache_dir = tmp_path / "cache"
    key = _frame_cache_key(html_file.read_text(), 3.0, 30)
    _plant_cache_frames(cache_dir, key, count=1)

    call_count = 0

    def fake_capture(html_path: Path, duration: float, fps: int, output_dir: Path) -> None:
        nonlocal call_count
        call_count += 1
        (output_dir / "frame_0000.png").write_bytes(b"\x89PNG")

    mock_web = MagicMock()
    mock_web.capture_frames = fake_capture

    with patch.dict("sys.modules", {"web_overlay": mock_web}):
        capture_slide_frames(
            slide_html_path=html_file,
            duration=3.0,
            fps=30,
            output_dir=tmp_path / "out",
            cache_dir=cache_dir,
            reuse=False,
        )

    assert call_count == 1


def test_web_overlay_import_error_raises_capture_error(tmp_path: Path) -> None:
    html_file = _make_html_file(tmp_path, "<html>fresh</html>")
    cache_dir = tmp_path / "cache"

    with (
        patch.dict("sys.modules", {"web_overlay": None}),
        pytest.raises(CaptureError, match="web-overlay"),
    ):
        capture_slide_frames(
            slide_html_path=html_file,
            duration=3.0,
            fps=30,
            output_dir=tmp_path / "out",
            cache_dir=cache_dir,
            reuse=True,
        )


def test_web_overlay_exception_wrapped_as_capture_error(tmp_path: Path) -> None:
    html_file = _make_html_file(tmp_path, "<html>fail slide</html>")
    cache_dir = tmp_path / "cache"

    mock_web = MagicMock()
    mock_web.capture_frames.side_effect = RuntimeError("playwright crashed")

    with (
        patch.dict("sys.modules", {"web_overlay": mock_web}),
        pytest.raises(CaptureError, match="Frame capture failed"),
    ):
        capture_slide_frames(
            slide_html_path=html_file,
            duration=3.0,
            fps=30,
            output_dir=tmp_path / "out",
            cache_dir=cache_dir,
            reuse=True,
        )
