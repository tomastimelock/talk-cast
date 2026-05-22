# Filepath: talk-cast/tests/test_narration_source.py
# Condensed Description: Tests for get_narration_text priority and auto-gen per layout
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_narration_source
# Dependencies: Internal: talk_cast.narration_source / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

import pytest
from deck_spec.models import Slide

from talk_cast.narration_source import get_narration_text

# ---------------------------------------------------------------------------
# Priority: narration > notes > auto-gen
# ---------------------------------------------------------------------------


def test_narration_field_takes_priority_over_notes():
    slide = Slide(
        layout="title",
        title="Ignored title",
        narration="Explicit narration text",
        notes="Notes text",
    )
    assert get_narration_text(slide) == "Explicit narration text"


def test_notes_used_when_narration_is_none():
    slide = Slide(layout="content", title="Some title", notes="Notes narration")
    assert get_narration_text(slide) == "Notes narration"


def test_auto_gen_used_when_no_narration_and_no_notes():
    slide = Slide(layout="title", title="My Title", subtitle="My Subtitle")
    result = get_narration_text(slide)
    assert result  # non-empty
    assert "My Title" in result


# ---------------------------------------------------------------------------
# Auto-gen: title layout
# ---------------------------------------------------------------------------


def test_auto_gen_title_includes_title_and_subtitle():
    slide = Slide(layout="title", title="Hello", subtitle="World")
    result = get_narration_text(slide)
    assert "Hello" in result
    assert "World" in result


def test_auto_gen_title_only_title_when_no_subtitle():
    slide = Slide(layout="title", title="Only Title")
    result = get_narration_text(slide)
    assert result == "Only Title"


# ---------------------------------------------------------------------------
# Auto-gen: section layout
# ---------------------------------------------------------------------------


def test_auto_gen_section_includes_title_and_subtitle():
    slide = Slide(layout="section", title="Section Title", subtitle="Section Sub")
    result = get_narration_text(slide)
    assert "Section Title" in result
    assert "Section Sub" in result


# ---------------------------------------------------------------------------
# Auto-gen: content layout
# ---------------------------------------------------------------------------


def test_auto_gen_content_includes_title_and_body():
    slide = Slide(layout="content", title="Content Title", body="Body text here.")
    result = get_narration_text(slide)
    assert "Content Title" in result
    assert "Body text here." in result


def test_auto_gen_content_is_nonempty():
    slide = Slide(layout="content", title="T", body="B")
    assert get_narration_text(slide)


# ---------------------------------------------------------------------------
# Auto-gen: bullet layout
# ---------------------------------------------------------------------------


def test_auto_gen_bullet_includes_title():
    slide = Slide(layout="bullet", title="Bullet Title", bullets=["Alpha", "Beta"])
    result = get_narration_text(slide)
    assert "Bullet Title" in result


def test_auto_gen_bullet_includes_at_least_one_bullet():
    slide = Slide(layout="bullet", title="Points", bullets=["First point", "Second point"])
    result = get_narration_text(slide)
    assert "First point" in result


def test_auto_gen_bullet_is_nonempty():
    slide = Slide(layout="bullet", title="T", bullets=["A"])
    assert get_narration_text(slide)


# ---------------------------------------------------------------------------
# Auto-gen: quote layout
# ---------------------------------------------------------------------------


def test_auto_gen_quote_includes_quote_text():
    slide = Slide(layout="quote", quote="To be or not to be.", attribution="Shakespeare")
    result = get_narration_text(slide)
    assert "To be or not to be." in result


def test_auto_gen_quote_includes_attribution():
    slide = Slide(layout="quote", quote="Quote text", attribution="Famous Person")
    result = get_narration_text(slide)
    assert "Famous Person" in result


# ---------------------------------------------------------------------------
# Auto-gen: stat layout
# ---------------------------------------------------------------------------


def test_auto_gen_stat_includes_stat_value():
    slide = Slide(layout="stat", stat_value="99%", stat_label="Uptime")
    result = get_narration_text(slide)
    assert "99%" in result


def test_auto_gen_stat_includes_stat_label():
    slide = Slide(layout="stat", stat_value="42", stat_label="Answers")
    result = get_narration_text(slide)
    assert "Answers" in result


def test_auto_gen_stat_is_nonempty():
    slide = Slide(layout="stat", stat_value="7", stat_label="Items")
    assert get_narration_text(slide)


# ---------------------------------------------------------------------------
# Auto-gen: blank layout
# ---------------------------------------------------------------------------


def test_auto_gen_blank_with_title_returns_title():
    slide = Slide(layout="blank", title="Blank with title")
    assert get_narration_text(slide) == "Blank with title"


def test_auto_gen_blank_with_no_fields_returns_empty_string():
    slide = Slide(layout="blank")
    result = get_narration_text(slide)
    assert result == ""


# ---------------------------------------------------------------------------
# All auto-gen results are strings (no TypeError)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "slide",
    [
        Slide(layout="title", title="T", subtitle="S"),
        Slide(layout="section", title="S"),
        Slide(layout="content", title="C", body="B"),
        Slide(layout="bullet", title="BT", bullets=["X"]),
        Slide(layout="quote", quote="Q", attribution="A"),
        Slide(layout="stat", stat_value="1", stat_label="L"),
        Slide(layout="blank", title="BL"),
        Slide(layout="blank"),
    ],
)
def test_auto_gen_returns_string_for_every_layout(slide: Slide):
    result = get_narration_text(slide)
    assert isinstance(result, str)
