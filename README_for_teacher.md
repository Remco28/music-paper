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
0. Check the in-app `Workflow snapshot` line near the top to confirm stage readiness.
1. Choose input source:
   - upload local audio file, or
   - paste single-video YouTube URL (no playlists).
2. Click audio preparation button.
3. Run stem separation.
4. Assign each stem to a target instrument (leave unneeded stems as `Unassigned`).
5. Set song metadata and optional simplification settings.
6. Click `Transcribe + Export ZIP`.
7. Download ZIP containing rendered outputs.

## Simplification
- **Simplification Profiles** let you choose from three presets:
  - `Beginner` — most simplification, best for new players
  - `Easy Intermediate` — default middle ground
  - `Intermediate` — least simplification, keeps more musical detail
- `Student Simplification Mode` enables/disables simplification entirely.
- `Advanced Simplification Settings` lets you override the profile values for quantization, min note duration, and density threshold.

## Reviewing and Rerunning
- Use **Quick Rerun** to try different simplification settings without re-uploading audio or re-separating stems. Each rerun gets its own isolated output.
- The app shows a compact run summary after export (run ID + exported/skipped part counts).
- The app shows a `Complexity Summary` table after export (difficulty, fast-note count, tuplet count, average duration, pages) to help choose simplification settings.
- ZIP exports include a run-ID suffix: `<song_title>_<run_id>_exports.zip`.
- Last-used score options are remembered during the session so repeated runs are faster.
- In **Recent Runs**, select a run to inspect its manifest-backed details and re-download that run's ZIP if it still exists in `downloads/`.
- From selected run details, use **Apply Settings to Current Options** to copy that run's simplification options into the active controls.
- **Recent Runs** supports filters for input/status/warning state/warning category, sort mode, `Run ID Search`, and a bounded `History Limit` (5/10/20).
- A small health line in **Recent Runs** summarizes manifest readability and ZIP presence for the current filtered set.
- Use **Copyable Summary** in Recent Runs to share a quick snapshot; an optional session note can be included and stays session-only.
- Use **Download CSV (Current Filtered Set)** in Recent Runs for spreadsheet-friendly review of the visible run set.
- Use **Refresh Run Cache** (or keep **Auto Refresh Run Cache** enabled) when validating many historical runs.
- Recent Runs table labels are teacher-friendly (`Run Outcome`, `Manifest`, `ZIP`) for faster scanning.

## Cleanup Controls
- Use **Run Artifact Maintenance** to prune older run folders from the UI.
- Set `Keep latest N runs`, confirm deletion, then click `Prune Old Runs`.
- The active run is always preserved, and the app reports deleted count + reclaimed storage.

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

## Handoff Path (Teacher + Maintainer)
1. Run setup checks (`python scripts/validate_setup.py`, then `python scripts/smoke_test.py`).
2. Complete the three-song benchmark worksheet: `docs/benchmark-3-song-pass.md`.
3. Review release gates: `docs/release-checklist.md`.
4. Capture any findings in `comms/log.md`.

Troubleshooting guide:
- `docs/troubleshooting.md`
- `docs/labeling-playability.md` (student-friendly part labeling workflow)
- `docs/run-history.md`
- `docs/export-verification.md`
- `docs/benchmark-3-song-pass.md` (teacher benchmark worksheet + pass criteria)
- In-app `Diagnostics` now includes a **Copyable Diagnostics Summary** block for sharing environment/tool status quickly.

## Notes
- No login/authentication in MVP.
- Processing runs locally after dependencies are installed.
- The app runs preflight checks on required tools before each pipeline run.
- Re-running preflight now shows a session-local change indicator (`baseline`, `no change`, or changed tool names).
- Preflight now also shows freshness (last-run time + age) and a non-blocking stale reminder after ~30 minutes.
- The app includes read-only `Diagnostics` and `Recent Runs` panels for environment context and run traceability.
- `Recent Runs` supports simple filters by input type and run status (`success`/`unknown`).
- Each transcription run produces an isolated set of artifacts and a JSON manifest in the ZIP.
- The manifest includes selected simplification settings and pipeline metadata (`app_version`, `demucs_model`) for traceability.
- If a stage fails, the app displays concise stage-specific guidance with next-step hints.
- `Reset Temp Workspace` now requires explicit confirmation and shows what will be cleared; it does not delete files in `downloads/`.
