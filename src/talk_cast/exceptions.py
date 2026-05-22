# Filepath: talk-cast/src/talk_cast/exceptions.py
# Condensed Description: Package-level exception hierarchy for talk-cast
# Architecture Layer: domain
# Environment: Local
# Script Hierarchy: talk_cast.exceptions
# Dependencies: Internal: none / External: none
# Exposes: TalkCastError, TTSError, CaptureError, AssembleError
# Configuration: None
from __future__ import annotations


class TalkCastError(Exception): ...


class TTSError(TalkCastError): ...


class CaptureError(TalkCastError): ...


class AssembleError(TalkCastError): ...
