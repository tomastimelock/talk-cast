# Filepath: talk-cast/tests/test_cli.py
# Condensed Description: Tests for the talk-cast CLI main() entry point
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_cli
# Dependencies: Internal: talk_cast.cli / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from talk_cast.cli import main


def _write_deck(path: Path) -> None:
    deck = {
        "title": "Test Deck",
        "slides": [{"layout": "title", "title": "Hello", "notes": "Hello narration."}],
    }
    path.write_text(json.dumps(deck), encoding="utf-8")


def test_missing_deck_file_returns_1(tmp_path: Path) -> None:
    rc = main([str(tmp_path / "nonexistent.json"), "--output", "out.mp4"])
    assert rc == 1


def test_no_output_flag_returns_1(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    rc = main([str(deck_file)])
    assert rc == 1


def test_help_exits(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_invalid_deck_json_returns_1(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"title": "missing slides"}', encoding="utf-8")
    rc = main([str(bad), "--output", "out.mp4"])
    assert rc == 1


def test_valid_deck_calls_narrate(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate") as mock_narrate:
        mock_narrate.return_value = output
        rc = main([str(deck_file), "--output", str(output)])

    assert rc == 0
    mock_narrate.assert_called_once()


def test_voice_flag_sets_voice_id(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate") as mock_narrate:
        mock_narrate.return_value = output
        rc = main([str(deck_file), "--output", str(output), "--voice", "test_voice_123"])

    assert rc == 0
    _, kwargs = mock_narrate.call_args
    assert kwargs["config"].voice_id == "test_voice_123"


def test_music_flag_sets_music_bed(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    music_file = tmp_path / "music.mp3"
    music_file.write_bytes(b"fake")
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate") as mock_narrate:
        mock_narrate.return_value = output
        rc = main([str(deck_file), "--output", str(output), "--music", str(music_file)])

    assert rc == 0
    _, kwargs = mock_narrate.call_args
    assert kwargs["config"].music_bed == music_file


def test_music_db_flag_sets_music_bed_db(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate") as mock_narrate:
        mock_narrate.return_value = output
        rc = main([str(deck_file), "--output", str(output), "--music-db", "-18.0"])

    assert rc == 0
    _, kwargs = mock_narrate.call_args
    assert pytest.approx(-18.0) == kwargs["config"].music_bed_db


def test_subtitles_flag_sets_subtitles(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate") as mock_narrate:
        mock_narrate.return_value = output
        rc = main([str(deck_file), "--output", str(output), "--subtitles", "soft"])

    assert rc == 0
    _, kwargs = mock_narrate.call_args
    assert kwargs["config"].subtitles == "soft"


def test_dry_run_flag_passed_to_narrate(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate") as mock_narrate:
        mock_narrate.return_value = output
        rc = main([str(deck_file), "--output", str(output), "--dry-run"])

    assert rc == 0
    _, kwargs = mock_narrate.call_args
    assert kwargs["dry_run"] is True


def test_no_cache_disables_cache(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate") as mock_narrate:
        mock_narrate.return_value = output
        rc = main([str(deck_file), "--output", str(output), "--no-cache"])

    assert rc == 0
    _, kwargs = mock_narrate.call_args
    assert kwargs["config"].reuse_audio_cache is False
    assert kwargs["config"].reuse_frame_cache is False


def test_narrate_exception_returns_1(tmp_path: Path) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    output = tmp_path / "out.mp4"

    with patch("talk_cast.narrate.narrate", side_effect=RuntimeError("boom")):
        rc = main([str(deck_file), "--output", str(output)])

    assert rc == 1


def test_tts_only_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    deck_file = tmp_path / "deck.json"
    _write_deck(deck_file)
    out_dir = tmp_path / "narration"

    fake_wav = tmp_path / "fake.wav"
    fake_wav.write_bytes(b"RIFF")

    with patch("talk_cast.tts.batch.BatchTTS") as mock_batch_cls:
        instance = mock_batch_cls.return_value
        instance.synthesize_all.return_value = [fake_wav]
        rc = main([str(deck_file), "--tts-only", "--output-dir", str(out_dir)])

    assert rc == 0
    assert out_dir.exists()
