# Filepath: talk-cast/src/talk_cast/__init__.py
# Condensed Description: Package root; re-exports primary public API
# Architecture Layer: interface
# Environment: Local
# Script Hierarchy: talk_cast
# Dependencies: Internal: talk_cast.config, talk_cast.narrate / External: none
# Exposes: narrate, NarrateConfig, __version__
# Configuration: NarrateConfig
from __future__ import annotations

from talk_cast.config import NarrateConfig
from talk_cast.narrate import narrate

__version__ = "0.1.0"
__all__ = ["NarrateConfig", "__version__", "narrate"]
