# Band Transcription Tool (MVP)

This app runs locally and converts a song into:
- a full conductor score PDF
- assigned, non-empty part PDFs for concert band instruments

## What You Need (Windows)
1. **Python 3.11** (project runtime)
2. MuseScore 4 (installed and available as `mscore` command, or update `MUSESCORE_CMD` in `config.py`)
3. FFmpeg (required by pydub/yt-dlp workflows)

## First Launch (Windows)
1. Open this project folder.
2. Double-click `start.bat`.
3. A local browser tab opens at `http://localhost:8501`.

## Manual Setup (any OS)
```
python3.11 -m venv venv
# Linux/macOS: source venv/bin/activate
# Windows:     venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.headless true --server.port 8501
```

## WSL Setup (Ubuntu via Deadsnakes)
Use this if Python 3.12 remains your system default and you want a dedicated Python 3.11 project venv.

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# from project root
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.headless true --server.port 8501
```

## Basic Workflow
1. Choose input source:
   - upload local audio file, or
   - paste single-video YouTube URL (no playlists).
2. Click audio preparation button.
3. Run stem separation.
4. Assign each stem to a target instrument (leave unneeded stems as `Unassigned`).
5. Set song metadata and optional simplification settings.
6. Click `Transcribe for Concert Band`.
7. Download ZIP containing rendered outputs.

## Simplification
- **Simplification Profiles** let you choose from three presets:
  - `Conservative` — least simplification, keeps more musical detail
  - `Balanced` — default middle ground
  - `Aggressive` — most simplification, best for beginners
- `Student Simplification Mode` enables/disables simplification entirely.
- `Advanced Simplification Settings` lets you override the profile values for quantization, min note duration, and density threshold.

## Reviewing and Rerunning
- Use **Quick Rerun** to try different simplification settings without re-uploading audio or re-separating stems. Each rerun gets its own isolated output.
- The app shows a compact run summary after export (run ID + exported/skipped part counts).
- Last-used score options are remembered during the session so repeated runs are faster.

## Verifying Your Setup
After installing, run the validation script to confirm everything is in place:
```
python scripts/validate_setup.py
```
This checks Python version, required packages, and external tools (demucs, basic-pitch, mscore, ffmpeg).

Maintainer smoke test:
```
python scripts/smoke_test.py
```
This performs import checks, config invariant checks, and manifest schema sanity checks.

Troubleshooting guide:
- `docs/troubleshooting.md`
- `docs/run-history.md`

## Notes
- No login/authentication in MVP.
- Processing runs locally after dependencies are installed.
- The app runs preflight checks on required tools before each pipeline run.
- The app includes read-only `Diagnostics` and `Recent Runs` panels for environment context and run traceability.
- Each transcription run produces an isolated set of artifacts and a JSON manifest in the ZIP.
- The manifest includes selected simplification settings and pipeline metadata (`app_version`, `demucs_model`) for traceability.
- If a stage fails, the app displays concise stage-specific guidance with next-step hints.
