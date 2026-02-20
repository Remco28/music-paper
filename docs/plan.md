**Formalized Implementation Plan: Band Transcription Tool (BTT)**  
**Project Name**: Middle School Concert Band Transcription Assistant (BTT)  
**Version**: 1.0 (MVP)  
**Target**: One middle-school concert band teacher  
**Platform**: Local Windows PC (Ryzen 5 5600X, 16 GB RAM, RX 6500 XT) – 100% offline after install  
**Development Environment**: Ubuntu WSL (your side) → deploy to native Windows  
**Priority**: Maximum transcription quality (stem separation + clean MIDI + perfect transposition)  
**No paid APIs**, no cloud, no batch/library features  

## 2026-02-20 Addendum: Calibration Track
- We are adding a separate local-only **Tuning Lab** workflow for simplification calibration.
- Strategy source of truth: `docs/tuning-lab-strategy-2026-02-20.md`.
- First implementation phase: `comms/tasks/2026-02-20-phase-39-tuning-lab-mvp-spec.md`.
- Production app remains the teacher-facing path; Tuning Lab is experiment-only.

### 1. Confirmed Requirements
- **Input**: Clean MP3/AAC/WAV files (primary) + YouTube links (always visible, using yt-dlp audio-only).
- **UI**: Browser-based (Streamlit running locally on http://localhost:8501), big buttons, wizard-style, no CLI.
- **Processing**: Demucs stem separation (htdemucs or htdemucs_6s for best quality) → Basic-Pitch per-stem MIDI → music21 multi-part score with correct transpositions.
- **Output** (must-have):
  - Full conductor score PDF (concert pitch)
  - Individual transposed part PDFs (e.g., “Trumpet 1 - Song Title.pdf”, “Alto Sax - Song Title.pdf”, etc.)
- **Options**:
  - Checkbox: “Student Simplification Mode” (quantize to 8th notes, remove 16ths/tuplets, simplify rhythms).
  - Text boxes: Song Title, Composer, School/Teacher Name (for title page + disclaimer footer).
- **Auth**: Simple password login (stored locally in JSON, teacher sets on first run).
- **Disclaimer**: “Educational Use Only – Generated for [School Name]” stamped on every PDF (via music21 metadata + MuseScore text frame).
- **Pre-filled instruments** (standard middle-school concert band – teacher can select/assign stems):
  - Flute, Oboe, Bassoon
  - Bb Clarinet 1/2/3, Bass Clarinet
  - Alto Sax 1/2, Tenor Sax, Baritone Sax
  - Bb Trumpet 1/2/3, French Horn 1/2, Trombone 1/2, Euphonium, Tuba
  - Percussion: Snare Drum, Bass Drum, Mallets (Xylophone), Timpani, Auxiliary
- **MuseScore integration**: None required for daily use; optional “Open in MuseScore” button (launches .mscz).

### 2. High-Level Architecture
```
User (Browser) → Streamlit (FastAPI-like) → 
  1. Input handler (pydub + yt-dlp)
  2. Stem separation (demucs)
  3. Transcription (basic-pitch per stem)
  4. Score builder (music21: parts, transpositions, simplification, metadata)
  5. Render (MuseScore 4 CLI → full score + individual part PDFs)
→ Download ZIP of all PDFs + .mscz file
```

All temp files in `./temp/` (auto-cleaned after session).

### 3. Tech Stack (2026-verified, all free & stable)
- **UI**: Streamlit 1.40+ (local web server)
- **Audio**: pydub + ffmpeg, yt-dlp
- **Stem separation**: demucs (v4 / htdemucs – highest open-source quality in 2026; CPU-only fine)
- **Transcription**: basic-pitch (Spotify, latest v0.4.0+ with 2025 commits)
- **Score & transposition**: music21 9.9.1+
- **Rendering**: MuseScore 4+ CLI (`mscore.exe -o score.pdf input.musicxml`)
- **Packaging**: PyInstaller or simple .bat launcher
- **Auth & storage**: Python stdlib (json, secrets)
- **Python version**: 3.11 or 3.12 (works on both WSL & Windows)

### 4. Project Folder Structure
```
band-transcription-tool/
├── app.py                  # Main Streamlit app
├── config.py               # Instruments list, paths, constants
├── pipeline.py             # Core functions: stems → midi → musicxml → pdfs
├── utils.py                # Helpers (auth, cleanup, disclaimer)
├── requirements.txt
├── start.bat               # One-click Windows launcher
├── MuseScore/              # (user installs separately)
├── temp/                   # .gitignore
├── outputs/                # Saved results (optional)
└── README_for_teacher.md
```

### 5. Detailed Module Breakdown (for implementation)
**config.py**
- `STANDARD_INSTRUMENTS = ["Flute", "Bb Clarinet 1", ...]` with music21 instrument objects + transposition (e.g., BbClarinet: -2 semitones)
- `DEMUCS_MODEL = "htdemucs"` (or "htdemucs_6s" for piano/guitar split)

**pipeline.py** (core functions)
1. `download_or_convert_audio(url_or_path) → wav_path`
2. `separate_stems(wav_path) → dict[stem_name: wav_path]` (demucs)
3. `transcribe_to_midi(stems) → dict[stem_name: midi_path]` (basic-pitch loop)
4. `build_score(midis, title, composer, school, simplify=False) → musicxml_path + mscz_path`
   - Create `music21.stream.Score()`
   - For each stem → `music21.converter.parse(midi)` → assign instrument from teacher mapping
   - Apply simplification (`.quantize()` + filter short notes)
   - Add title, composer, disclaimer text frame
   - Write MusicXML + save .mscz via music21
5. `render_pdfs(musicxml_path) → list of pdf_paths`
   - Use `subprocess` to call `mscore -o full_score.pdf score.musicxml`
   - For each part: music21 generates part MusicXML or use MuseScore `--export-score-parts` / loop CLI

**app.py** (Streamlit)
- Sidebar: Login (password)
- Main tabs/pages:
  1. Upload / YouTube (big buttons)
  2. Stem preview + instrument assignment dropdowns (pre-filled list, multi-select allowed)
  3. Options: Simplification checkbox, title/composer/school text boxes
  4. “Transcribe for Concert Band” button
  5. Progress bar with emojis (🎺 Processing stems… 🥁 Transcribing…)
  6. Results: Preview score image (optional via music21.show()), download ZIP + “Open in MuseScore” button

**utils.py**
- Password hashing/storage (first-run setup)
- Auto-clean temp folder
- Add disclaimer footer via music21 `TextBox`

### 6. Installation & Deployment Guide
**For you (WSL dev)**:
1. `git clone ...`
2. `python -m venv venv; source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Install MuseScore 4 (Windows side, path in config)
5. `streamlit run app.py` → test

**requirements.txt** (exact):
```
streamlit
pydub
yt-dlp
demucs
basic-pitch
music21
Pillow
```

**For teacher (Windows one-click)**:
- Install MuseScore 4 from musescore.org (free)
- Run `start.bat` (creates venv if missing, installs deps, starts Streamlit + opens browser)

**start.bat** content:
```bat
@echo off
if not exist venv (
    python -m venv venv
    venv\Scripts\pip install -r requirements.txt
)
venv\Scripts\streamlit run app.py --server.headless true --server.port 8501
```

### 7. Testing & Quality Plan
- Test with 5 clean band recordings (various difficulties).
- Compare output to manual MuseScore entry (teacher validates first 3 songs).
- Simplification mode: visual + playback test.
- Edge cases: short clips, YouTube, AAC files, mono/stereo.
- Performance: <15 min per 3-min song expected on this hardware (quality > speed).

### 8. Maintenance for Students (2027+)
- All code commented, modular.
- Update paths in config.py only.
- If demucs/basic-pitch break, fallback to full-mix Basic-Pitch (still usable).
- GitHub repo recommended for version control.

### 9. Timeline Suggestion (No Deadline)
- Week 1: Core pipeline (audio → MusicXML)
- Week 2: Streamlit UI + MuseScore rendering + PDF parts
- Week 3: Auth, disclaimer, simplification, teacher testing
- Week 4: Polish, .bat launcher, documentation
