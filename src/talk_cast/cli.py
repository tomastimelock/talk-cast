# Filepath: talk-cast/src/talk_cast/cli.py
# Condensed Description: argparse CLI entry point for the talk-cast narration pipeline
# Architecture Layer: interface
# Environment: Local
# Script Hierarchy: talk_cast.cli
# Dependencies: Internal: talk_cast.config, talk_cast.narrate, talk_cast.narration_source, talk_cast.tts.batch / External: deck-spec
# Exposes: main
# Configuration: NarrateConfig
from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="talk-cast",
        description="Render a deck-spec Deck to a narrated MP4 video.",
    )
    parser.add_argument("deck", help="Path to deck JSON file")
    parser.add_argument("--output", "-o", metavar="PATH", help="Output MP4 path")
    parser.add_argument("--voice", metavar="VOICE_ID", help="ElevenLabs voice ID override")
    parser.add_argument("--music", metavar="PATH", help="Background music file")
    parser.add_argument("--music-db", type=float, metavar="DB", help="Music bed gain (dB)")
    parser.add_argument(
        "--subtitles",
        choices=["off", "soft", "hard"],
        default="off",
        help="Subtitle mode (default: off)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Prepare assets but skip video encode"
    )
    parser.add_argument("--tts-only", action="store_true", help="Only synthesize TTS audio")
    parser.add_argument("--output-dir", metavar="DIR", help="Output directory for --tts-only mode")
    parser.add_argument("--no-cache", action="store_true", help="Force regeneration of all assets")
    parser.add_argument("--verbose", "-v", action="store_true", help="Emit debug-level log output")
    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_parser()
    ns = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if ns.verbose else logging.WARNING,
        stream=sys.stderr,
    )

    deck_path = Path(ns.deck)
    if not deck_path.exists():
        print(f"Error: deck file not found: {deck_path}", file=sys.stderr)
        return 1

    try:
        from deck_spec.validate import validate_json
    except ImportError as exc:
        print(
            f"Error: deck-spec not installed ({exc}). Run: pip install deck-spec", file=sys.stderr
        )
        return 1

    try:
        deck = validate_json(deck_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error loading deck {deck_path}: {exc}", file=sys.stderr)
        return 1

    from talk_cast.config import NarrateConfig

    config_kwargs: dict = {
        "subtitles": ns.subtitles,
        "verbose": ns.verbose,
        "reuse_audio_cache": not ns.no_cache,
        "reuse_frame_cache": not ns.no_cache,
    }
    if ns.voice:
        config_kwargs["voice_id"] = ns.voice
    if ns.music:
        config_kwargs["music_bed"] = Path(ns.music)
    if ns.music_db is not None:
        config_kwargs["music_bed_db"] = ns.music_db

    config = NarrateConfig(**config_kwargs)

    if ns.tts_only:
        output_dir = Path(ns.output_dir) if ns.output_dir else Path("narration")
        output_dir.mkdir(parents=True, exist_ok=True)
        from talk_cast.narration_source import get_narration_text
        from talk_cast.tts.batch import BatchTTS

        cache_dir = config.cache_dir or Path(".talk-cast-cache")
        batch = BatchTTS(config, cache_dir)
        items = [(f"slide_{i:02d}", get_narration_text(s)) for i, s in enumerate(deck.slides)]
        wavs = batch.synthesize_all(items)
        for i, wav in enumerate(wavs):
            dest = output_dir / f"slide_{i:02d}.wav"
            shutil.copy(wav, dest)
        print(f"TTS audio written to {output_dir}/")
        return 0

    if not ns.output:
        print("Error: --output is required.", file=sys.stderr)
        return 1

    try:
        from talk_cast.narrate import narrate

        narrate(deck, Path(ns.output), config=config, dry_run=ns.dry_run)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
