# Filepath: talk-cast/tests/test_tts_cache_key.py
# Condensed Description: Tests for TTSCache.make_key determinism and uniqueness
# Architecture Layer: test
# Environment: Local
# Script Hierarchy: tests.test_tts_cache_key
# Dependencies: Internal: talk_cast.tts.cache, talk_cast.config / External: pytest
# Exposes: test functions
# Configuration: None
from __future__ import annotations

from talk_cast.config import VoiceSettings
from talk_cast.tts.cache import TTSCache

_VS_DEFAULT = VoiceSettings()


def test_same_inputs_produce_same_key():
    key1 = TTSCache.make_key("Hello world", "voice-abc", "model-xyz", _VS_DEFAULT)
    key2 = TTSCache.make_key("Hello world", "voice-abc", "model-xyz", _VS_DEFAULT)
    assert key1 == key2


def test_different_text_produces_different_key():
    key1 = TTSCache.make_key("Text one", "voice-abc", "model-xyz", _VS_DEFAULT)
    key2 = TTSCache.make_key("Text two", "voice-abc", "model-xyz", _VS_DEFAULT)
    assert key1 != key2


def test_different_voice_id_produces_different_key():
    key1 = TTSCache.make_key("Same text", "voice-aaa", "model-xyz", _VS_DEFAULT)
    key2 = TTSCache.make_key("Same text", "voice-bbb", "model-xyz", _VS_DEFAULT)
    assert key1 != key2


def test_different_model_id_produces_different_key():
    key1 = TTSCache.make_key("Same text", "voice-abc", "model-v1", _VS_DEFAULT)
    key2 = TTSCache.make_key("Same text", "voice-abc", "model-v2", _VS_DEFAULT)
    assert key1 != key2


def test_different_stability_produces_different_key():
    vs_a = VoiceSettings(stability=0.3)
    vs_b = VoiceSettings(stability=0.9)
    key1 = TTSCache.make_key("Same text", "voice-abc", "model-xyz", vs_a)
    key2 = TTSCache.make_key("Same text", "voice-abc", "model-xyz", vs_b)
    assert key1 != key2


def test_key_is_64_char_hex_string():
    key = TTSCache.make_key("Any text", "v-id", "m-id", _VS_DEFAULT)
    assert len(key) == 64
    assert all(c in "0123456789abcdef" for c in key)


def test_key_is_deterministic_across_calls():
    key_a = TTSCache.make_key("Stable", "v", "m", _VS_DEFAULT)
    key_b = TTSCache.make_key("Stable", "v", "m", _VS_DEFAULT)
    assert key_a == key_b


def test_different_similarity_boost_produces_different_key():
    vs_a = VoiceSettings(similarity_boost=0.5)
    vs_b = VoiceSettings(similarity_boost=0.99)
    key1 = TTSCache.make_key("Text", "v", "m", vs_a)
    key2 = TTSCache.make_key("Text", "v", "m", vs_b)
    assert key1 != key2
