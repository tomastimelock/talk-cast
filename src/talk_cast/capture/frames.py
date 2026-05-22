# Filepath: talk-cast/src/talk_cast/capture/frames.py
# Condensed Description: Captures PNG frames from slide HTML via web_overlay with disk caching
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.capture.frames
# Dependencies: Internal: talk_cast.config, talk_cast.exceptions / External: web-overlay (lazy)
# Exposes: capture_slide_frames
# Configuration: NarrateConfig
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from talk_cast.exceptions import CaptureError

logger = logging.getLogger(__name__)


def _frame_cache_key(html_content: str, duration: float, fps: int) -> str:
    raw = f"{html_content}|{duration}|{fps}"
    return hashlib.sha256(raw.encode()).hexdigest()


def capture_slide_frames(
    slide_html_path: Path,
    duration: float,
    fps: int,
    output_dir: Path,
    cache_dir: Path,
    reuse: bool = True,
) -> list[Path]:
    html_content = slide_html_path.read_text(encoding="utf-8")
    key = _frame_cache_key(html_content, duration, fps)
    frames_cache_dir = cache_dir / "frames" / key

    if reuse and frames_cache_dir.exists():
        existing = sorted(frames_cache_dir.glob("frame_*.png"))
        if existing:
            logger.debug(f"Frame cache hit: {key[:12]}")
            return existing

    frames_cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        from web_overlay import capture_frames
    except ImportError as exc:
        raise CaptureError(
            "web-overlay package is not installed. Run: pip install web-overlay"
        ) from exc

    try:
        capture_frames(
            html_path=slide_html_path,
            duration=duration,
            fps=fps,
            output_dir=frames_cache_dir,
        )
    except CaptureError:
        raise
    except Exception as exc:
        raise CaptureError(f"Frame capture failed: {exc}") from exc

    return sorted(frames_cache_dir.glob("frame_*.png"))
