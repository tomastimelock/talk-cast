# Filepath: talk-cast/src/talk_cast/narration_source.py
# Condensed Description: Extracts narration text from a Slide by priority: narration > notes > auto-gen
# Architecture Layer: domain
# Environment: Local
# Script Hierarchy: talk_cast.narration_source
# Dependencies: Internal: none / External: deck-spec
# Exposes: get_narration_text
# Configuration: None
from __future__ import annotations

from deck_spec.models import Slide


def _auto_gen(slide: Slide) -> str:
    layout = slide.layout

    def _join(*parts: str | None) -> str:
        return " ".join(p for p in parts if p)

    if layout in ("title", "section"):
        return _join(slide.title, slide.subtitle)

    if layout == "content":
        return _join(slide.title, slide.body)

    if layout == "bullet":
        title = slide.title or ""
        bullets_text = ""
        if isinstance(slide.bullets, list):
            bullets_text = ". ".join(str(b) for b in slide.bullets if b)
        elif slide.bullets:
            bullets_text = str(slide.bullets)
        return _join(title, bullets_text)

    if layout in ("two_column", "comparison"):
        title = slide.title or ""
        cols = slide.columns or []
        parts: list[str] = [title]
        for col in cols[:2]:
            if col.heading:
                parts.append(col.heading)
            if col.bullets:
                parts.append(str(col.bullets[0]))
        return " ".join(p for p in parts if p)

    if layout in ("image", "image_caption"):
        return _join(slide.title, slide.caption)

    if layout == "quote":
        return _join(slide.attribution, slide.quote)

    if layout == "stat":
        return _join(slide.stat_value, slide.stat_label, slide.stat_supporting)

    # blank and any unknown layout
    return slide.title or ""


def get_narration_text(slide: Slide) -> str:
    """Return narration text for slide. Priority: narration > notes > auto-gen."""
    if slide.narration:
        return slide.narration
    if slide.notes:
        return slide.notes
    return _auto_gen(slide)
