# Filepath: talk-cast/src/talk_cast/tts/errors.py
# Condensed Description: TTS-specific exception subtypes
# Architecture Layer: domain
# Environment: Local
# Script Hierarchy: talk_cast.tts.errors
# Dependencies: Internal: talk_cast.exceptions / External: none
# Exposes: RateLimitError, AuthError
# Configuration: None
from __future__ import annotations

from talk_cast.exceptions import TTSError


class RateLimitError(TTSError): ...


class AuthError(TTSError): ...
