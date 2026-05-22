# Filepath: talk-cast/src/talk_cast/assemble/audio_mix.py
# Condensed Description: Mixes per-slide narration WAVs with optional music bed via audio-arrange
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.assemble.audio_mix
# Dependencies: Internal: talk_cast.config, talk_cast.exceptions / External: audio-arrange (lazy)
# Exposes: mix_audio
# Configuration: NarrateConfig
from __future__ import annotations

import logging
from pathlib import Path

from talk_cast.config import NarrateConfig
from talk_cast.exceptions import AssembleError

logger = logging.getLogger(__name__)


def mix_audio(
    narration_paths: list[Path],
    durations: list[float],
    config: NarrateConfig,
    output: Path,
) -> Path:
    try:
        from audio_arrange import AudioTimeline, Segment
    except ImportError as exc:
        raise AssembleError(
            "audio-arrange package is not installed. Run: pip install audio-arrange"
        ) from exc

    try:
        timeline = AudioTimeline()
        offset = 0.0
        for wav_path, duration in zip(narration_paths, durations, strict=True):
            seg = Segment(
                path=wav_path,
                start=offset + config.leading_silence,
                volume_db=0.0,
            )
            timeline.add(seg)
            offset += duration

        if config.music_bed is not None:
            from audio_arrange import MusicBed

            bed = MusicBed(
                path=config.music_bed,
                volume_db=config.music_bed_db,
                duck_db=config.music_duck_db,
                fade_in=config.music_fade_in,
                fade_out=config.music_fade_out,
            )
            timeline.set_music_bed(bed)

        timeline.render(output)
        return output
    except AssembleError:
        raise
    except Exception as exc:
        raise AssembleError(f"Audio mix failed: {exc}") from exc
