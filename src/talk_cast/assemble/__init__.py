# Filepath: talk-cast/src/talk_cast/assemble/__init__.py
# Condensed Description: Public re-exports for the assemble sub-package
# Architecture Layer: infrastructure
# Environment: Local
# Script Hierarchy: talk_cast.assemble
# Dependencies: Internal: talk_cast.assemble.timeline / External: none
# Exposes: assemble_timeline
# Configuration: None
from __future__ import annotations

from talk_cast.assemble.timeline import assemble_timeline

__all__ = ["assemble_timeline"]
