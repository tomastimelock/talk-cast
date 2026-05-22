# Filepath: talk-cast/src/talk_cast/assemble/subtitles.py
# Condensed Description: SRT subtitle generation and optional hard-burn via video-arrange
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.assemble.subtitles
# Dependencies: Internal: none / External: video-arrange (lazy, hard-burn only)
# Exposes: generate_srt, write_srt, burn_subtitles
# Configuration: None
from __future__ import annotations

from pathlib import Path


def _fmt_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(
    texts: list[str],
    durations: list[float],
    leading_silence: float = 0.4,
) -> str:
    lines: list[str] = []
    offset = 0.0
    for i, (text, duration) in enumerate(zip(texts, durations, strict=True), start=1):
        start = offset + leading_silence
        end = offset + duration - 0.1
        lines.append(str(i))
        lines.append(f"{_fmt_timestamp(start)} --> {_fmt_timestamp(end)}")
        lines.append(text)
        lines.append("")
        offset += duration
    return "\n".join(lines)


def write_srt(srt_content: str, path: Path) -> None:
    path.write_text(srt_content, encoding="utf-8")


def burn_subtitles(mp4_in: Path, srt_path: Path, mp4_out: Path) -> None:
    try:
        from video_arrange import burn_subtitles as _burn
    except ImportError as exc:
        raise ImportError(
            "video-arrange package is not installed. Run: pip install video-arrange"
        ) from exc
    _burn(str(mp4_in), str(srt_path), str(mp4_out))
