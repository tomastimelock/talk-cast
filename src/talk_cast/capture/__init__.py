# Filepath: talk-cast/src/talk_cast/capture/__init__.py
# Condensed Description: Public re-exports for the capture sub-package
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.capture
# Dependencies: Internal: talk_cast.capture.frames / External: none
# Exposes: capture_slide_frames
# Configuration: None
from __future__ import annotations

from talk_cast.capture.frames import capture_slide_frames

__all__ = ["capture_slide_frames"]
