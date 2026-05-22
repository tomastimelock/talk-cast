# talk-cast

Deck-spec to narrated MP4: TTS via ElevenLabs, frame capture via web-overlay, audio mix via audio-arrange, video assembly via video-arrange.

Built at Trollfabriken AITrix AB to close the loop: AIMOS Insight audit reports, Granskning case briefs,
and civic-education explainers all begin as Deck objects authored by an LLM, and end as narrated videos
posted to the news site — without leaving Python or paying a video-API vendor. Uses ElevenLabs for
narration, your `audio-arrange` for the mix, your `web-overlay` for frame capture, and your
`video-arrange` for the final assembly. Re-rendering after editing one slide takes seconds, not minutes.

---

## What it solves

| Problem | How talk-cast fixes it |
|---|---|
| TTS calls cost money on every re-render | Per-slide audio cache; unchanged slides reuse the cached MP3 |
| Frame capture needs a real browser | `web-overlay` drives Playwright Chromium headlessly |
| Audio timing drifts from slide duration | `audio-arrange` trims/pads each clip to match slide duration exactly |
| Assembling MP4 from frames + audio requires ffmpeg knowledge | `video-arrange` wraps ffmpeg; one call produces the final file |
| Different voice per section is messy to wire up | `NarrateConfig` maps slide index ranges to ElevenLabs voice IDs |
| Subtitle track is optional but painful to add | `talk-cast[subtitles]` writes a WebVTT file alongside the MP4 |

---

## Installation

```bash
pip install talk-cast
```

With subtitle support:

```bash
pip install "talk-cast[subtitles]"
```

Development extras:

```bash
pip install "talk-cast[dev]"
```

### Runtime requirements

**ffmpeg** must be on `PATH`:

```bash
# Ubuntu / Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

**Playwright Chromium** for frame capture:

```bash
python -m playwright install chromium
```

**ElevenLabs API key** — set the environment variable:

```bash
export ELEVENLABS_API_KEY="your-key-here"
```

---

## Quick start

```python
from deck_spec import Deck
from talk_cast import NarrateConfig, cast

# Load a deck authored by an LLM or built by hand
deck = Deck.model_validate_json(open("my_deck.json").read())

config = NarrateConfig(
    voice_id="21m00Tcm4TlvDq8ikWAM",   # ElevenLabs voice ID
    slide_duration=8.0,                   # seconds per slide
    output_path="output/my_video.mp4",
    cache_dir=".talk-cast-cache",         # skip TTS if audio already cached
)

# Render the full narrated video
cast(deck, config)
```

Re-run after editing one slide — only that slide's TTS call is repeated. All other audio is served from cache.

---

## The pipeline

```
Deck object
    │
    ① Read slides + speaker notes
    │
    ② Check cache (.talk-cast-cache/)
    │        │
    │   hit ─┘   miss ─► ③ ElevenLabs TTS → MP3 → cache
    │
    ④ audio-arrange: trim / pad each MP3 to slide_duration
    │
    ⑤ slide-render: render each slide to HTML
    │
    ⑥ web-overlay: Playwright Chromium captures PNG frame per slide
    │
    ⑦ Assemble per-slide: frame PNG + padded MP3
    │
    ⑧ video-arrange: encode each slide segment to MP4 clip
    │
    ⑨ video-arrange: concatenate all clips → final MP4
    │
    ⑩ (optional) write WebVTT subtitle file alongside MP4
```

Each step is independently testable. Steps ③–④ are skipped when `TALK_CAST_SKIP_LIVE_TTS=1`.

---

## Configuration

`NarrateConfig` is a Pydantic model. All fields have defaults except `voice_id`.

| Field | Type | Default | Description |
|---|---|---|---|
| `voice_id` | `str` | required | ElevenLabs voice ID for narration |
| `voice_map` | `dict[int, str]` | `{}` | Override voice per slide index (0-based) |
| `slide_duration` | `float` | `8.0` | Seconds each slide is held on screen |
| `output_path` | `str \| Path` | `"output.mp4"` | Destination MP4 file |
| `cache_dir` | `str \| Path` | `".talk-cast-cache"` | Directory for cached TTS audio |
| `resolution` | `tuple[int, int]` | `(1920, 1080)` | Frame resolution in pixels |
| `fps` | `int` | `30` | Frames per second in the output video |
| `model_id` | `str` | `"eleven_multilingual_v2"` | ElevenLabs model |
| `stability` | `float` | `0.5` | ElevenLabs stability (0.0–1.0) |
| `similarity_boost` | `float` | `0.75` | ElevenLabs similarity boost (0.0–1.0) |
| `subtitles` | `bool` | `False` | Write a `.vtt` file alongside the MP4 |
| `theme` | `str` | `"default"` | slide-render theme name |

### Voice map example

Assign a different voice to slides 5–9:

```python
config = NarrateConfig(
    voice_id="21m00Tcm4TlvDq8ikWAM",
    voice_map={5: "AZnzlk1XvdvUeBnXmlld", 6: "AZnzlk1XvdvUeBnXmlld"},
    slide_duration=10.0,
    output_path="output/report.mp4",
)
```

---

## CLI

Render a deck file to MP4:

```bash
talk-cast render my_deck.json --voice 21m00Tcm4TlvDq8ikWAM --output output/video.mp4
```

Set slide duration to 12 seconds and enable subtitles:

```bash
talk-cast render my_deck.json \
    --voice 21m00Tcm4TlvDq8ikWAM \
    --duration 12 \
    --subtitles \
    --output output/video.mp4
```

Purge the TTS cache (forces re-synthesis on next render):

```bash
talk-cast cache clear
```

Inspect the cache — see which slides have audio:

```bash
talk-cast cache list
```

Validate a deck before rendering (runs deck-spec validation):

```bash
talk-cast validate my_deck.json
```

---

## Package structure

```
talk-cast/
├── src/
│   └── talk_cast/
│       ├── __init__.py          ← public API: cast(), NarrateConfig
│       ├── cli.py               ← talk-cast entry point
│       ├── narrate.py           ← TTS orchestration and cache logic
│       ├── capture.py           ← web-overlay frame capture per slide
│       ├── assemble.py          ← video-arrange + audio-arrange wiring
│       ├── config.py            ← NarrateConfig Pydantic model
│       ├── cache.py             ← cache read/write helpers
│       └── py.typed             ← PEP 561 marker
├── tests/
│   ├── fixtures/                ← small JSON decks + reference WAVs
│   ├── test_narrate.py
│   ├── test_capture.py
│   ├── test_assemble.py
│   └── test_cli.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

© Trollfabriken AITrix AB — MIT licensed
