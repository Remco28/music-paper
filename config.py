"""Static configuration for the Band Transcription Tool MVP."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
APP_VERSION = "0.4.0"
TEMP_DIR = PROJECT_ROOT / "temp"
RUNS_DIR = TEMP_DIR / "runs"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DOWNLOADS_DIR = PROJECT_ROOT / "downloads"

SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".aac", ".m4a", ".flac"}

YOUTUBE_DOMAINS = ("youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com")

DEMUCS_MODEL = "htdemucs"
MUSESCORE_CMD = "mscore"

REQUIRED_TOOLS = [
    {"name": "demucs", "cmd": "demucs", "args": ["--help"], "required": True},
    {"name": "basic-pitch", "cmd": "basic-pitch", "args": ["--help"], "required": True},
    {"name": "MuseScore", "cmd": MUSESCORE_CMD, "args": ["--version"], "required": True},
    {"name": "ffmpeg (via pydub)", "check": "pydub", "required": True},
]

# written pitch = concert pitch + transpose_semitones
INSTRUMENT_SPECS: dict[str, int] = {
    "Flute": 0,
    "Oboe": 0,
    "Bassoon": 0,
    "Bb Clarinet 1": 2,
    "Bb Clarinet 2": 2,
    "Bb Clarinet 3": 2,
    "Bass Clarinet": 14,
    "Alto Sax 1": 9,
    "Alto Sax 2": 9,
    "Tenor Sax": 14,
    "Baritone Sax": 21,
    "Bb Trumpet 1": 2,
    "Bb Trumpet 2": 2,
    "Bb Trumpet 3": 2,
    "French Horn 1": 7,
    "French Horn 2": 7,
    "Trombone 1": 0,
    "Trombone 2": 0,
    "Euphonium": 0,
    "Tuba": 0,
    "Snare Drum": 0,
    "Bass Drum": 0,
    "Mallets (Xylophone)": 0,
    "Timpani": 0,
    "Auxiliary Percussion": 0,
}

STANDARD_INSTRUMENTS = list(INSTRUMENT_SPECS.keys())

SIMPLIFY_PROFILES: dict[str, dict] = {
    "Conservative": {
        "quantize_grid": "1/16",
        "min_note_duration_beats": 0.125,
        "density_threshold": 10,
    },
    "Balanced": {
        "quantize_grid": "1/8",
        "min_note_duration_beats": 0.25,
        "density_threshold": 6,
    },
    "Aggressive": {
        "quantize_grid": "1/4",
        "min_note_duration_beats": 0.5,
        "density_threshold": 3,
    },
}

DEFAULT_PROFILE = "Balanced"

SIMPLIFY_PRESET = SIMPLIFY_PROFILES[DEFAULT_PROFILE] | {"enabled": True}

SIMPLIFY_ADVANCED_RANGES = {
    "quantize_grid": ("1/4", "1/8", "1/16"),
    "min_note_duration_beats": (0.125, 0.5),
    "density_threshold": (3, 10),
}
