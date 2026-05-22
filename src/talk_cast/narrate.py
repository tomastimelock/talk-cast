# Filepath: talk-cast/src/talk_cast/narrate.py
# Condensed Description: Top-level orchestrator sequencing all narration pipeline phases
# Architecture Layer: domain
# Environment: Local
# Script Hierarchy: talk_cast.narrate
# Dependencies: Internal: talk_cast.config, talk_cast.narration_source, talk_cast.tts.batch, talk_cast.capture, talk_cast.assemble / External: deck-spec, slide-render
# Exposes: narrate
# Configuration: NarrateConfig
from __future__ import annotations

import logging
from pathlib import Path

from talk_cast.config import NarrateConfig
from talk_cast.narration_source import get_narration_text

logger = logging.getLogger(__name__)


def narrate(
    deck: object,
    output: Path | str,
    config: NarrateConfig | None = None,
    dry_run: bool = False,
) -> Path:
    from deck_spec.models import Deck
    from slide_render.config import RenderConfig
    from slide_render.html.renderer import render_html_string

    from talk_cast.assemble.audio_mix import mix_audio
    from talk_cast.assemble.subtitles import burn_subtitles, generate_srt, write_srt
    from talk_cast.assemble.timeline import assemble_timeline
    from talk_cast.capture.frames import capture_slide_frames
    from talk_cast.capture.timing import compute_slide_duration
    from talk_cast.tts.batch import BatchTTS

    if config is None:
        config = NarrateConfig()

    output = Path(output)
    cache_dir = config.cache_dir or Path(".talk-cast-cache")
    cache_dir.mkdir(parents=True, exist_ok=True)

    assert isinstance(deck, Deck)
    slides = deck.slides

    texts = [get_narration_text(s) for s in slides]
    logger.debug(f"Extracted narration for {len(texts)} slides")

    batch = BatchTTS(config, cache_dir)
    items = [(f"slide_{i:02d}", text) for i, text in enumerate(texts)]
    wav_paths = batch.synthesize_all(items)
    logger.debug("TTS synthesis complete")

    durations = [compute_slide_duration(wav, config) for wav in wav_paths]

    render_config = RenderConfig(verbose=config.verbose)
    html_dir = cache_dir / "html"
    html_dir.mkdir(exist_ok=True)
    html_paths: list[Path] = []
    for i, slide in enumerate(slides):
        single_deck = Deck(title=deck.title, slides=[slide], theme=deck.theme)
        html_str = render_html_string(single_deck, render_config)
        html_path = html_dir / f"slide_{i:02d}.html"
        html_path.write_text(html_str, encoding="utf-8")
        html_paths.append(html_path)

    frame_dirs: list[Path] = []
    for i, html_path in enumerate(html_paths):
        frames = capture_slide_frames(
            slide_html_path=html_path,
            duration=durations[i],
            fps=config.fps,
            output_dir=cache_dir / "frames",
            cache_dir=cache_dir,
            reuse=config.reuse_frame_cache,
        )
        frame_dirs.append(frames[0].parent)

    if dry_run:
        logger.info("Dry run complete -- skipping audio mix and video encode")
        return output

    mixed_audio = cache_dir / "mixed.wav"
    mix_audio(wav_paths, durations, config, mixed_audio)

    srt_path: Path | None = None
    if config.subtitles != "off":
        srt_content = generate_srt(texts, durations, config.leading_silence)
        srt_path = output.with_suffix(".srt")
        write_srt(srt_content, srt_path)

    if config.subtitles == "hard":
        assert srt_path is not None
        raw_output = cache_dir / "raw.mp4"
        assemble_timeline(frame_dirs, mixed_audio, config, raw_output)
        burn_subtitles(raw_output, srt_path, output)
    else:
        assemble_timeline(frame_dirs, mixed_audio, config, output)

    logger.info(f"Rendered: {output}")
    return output
