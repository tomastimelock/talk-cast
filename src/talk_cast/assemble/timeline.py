# Filepath: talk-cast/src/talk_cast/assemble/timeline.py
# Condensed Description: Builds and renders video-arrange Timeline from frame dirs, audio, and transitions
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.assemble.timeline
# Dependencies: Internal: talk_cast.config, talk_cast.exceptions / External: video-arrange (lazy)
# Exposes: assemble_timeline
# Configuration: NarrateConfig
from __future__ import annotations

import logging
from pathlib import Path

from talk_cast.config import NarrateConfig
from talk_cast.exceptions import AssembleError

logger = logging.getLogger(__name__)


def assemble_timeline(
    slide_frame_dirs: list[Path],
    mixed_audio: Path,
    config: NarrateConfig,
    output: Path,
) -> Path:
    try:
        from video_arrange import Timeline, VideoSegment
    except ImportError as exc:
        raise AssembleError(
            "video-arrange package is not installed. Run: pip install video-arrange"
        ) from exc

    try:
        timeline = Timeline(
            fps=config.fps,
            width=config.width,
            height=config.height,
            audio_path=mixed_audio,
            video_codec=config.video_codec,
            audio_codec=config.audio_codec,
            audio_bitrate=config.audio_bitrate,
        )

        for frame_dir in slide_frame_dirs:
            frames = sorted(frame_dir.glob("frame_*.png"))
            if not frames:
                raise AssembleError(f"No frames found in {frame_dir}")
            seg = VideoSegment(frames=frames, transition_duration=config.transition_duration)
            timeline.add(seg)

        timeline.render(output)
        return output
    except AssembleError:
        raise
    except Exception as exc:
        raise AssembleError(f"Video assembly failed: {exc}") from exc
