# Filepath: talk-cast/src/talk_cast/tts/__init__.py
# Condensed Description: Public re-exports for the tts sub-package
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.tts
# Dependencies: Internal: talk_cast.tts.batch, talk_cast.tts.elevenlabs / External: none
# Exposes: BatchTTS, synthesize_narration
# Configuration: NarrateConfig
from __future__ import annotations

from talk_cast.tts.batch import BatchTTS
from talk_cast.tts.elevenlabs import synthesize as synthesize_narration

__all__ = ["BatchTTS", "synthesize_narration"]
