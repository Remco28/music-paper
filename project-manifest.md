# Project Manifest

## 1. Core Identity (Stable)
- Architecture (current source of truth): `docs/plan.md`
- Architecture (maintained summary): `docs/ARCHITECTURE.md` (to be created/maintained)
- Role definitions:
  - `comms/roles/ARCHITECT.md`
  - `comms/roles/DEVELOPER.md`
  - `comms/roles/TECHADVISOR.md`

## 2. Dynamic State (Volatile)
- Activity log: `comms/log.md`
- Active task specs: `comms/tasks/`
- Archived task specs: `comms/tasks/archive/`

## 3. Code & Config Entrypoints
- Main Streamlit app: `app.py`
- Pipeline logic: `pipeline.py`
- Project config/constants: `config.py`
- Utility helpers: `utils.py`
- Dependencies: `requirements.txt`
- Local launcher: `start.bat`
- Setup validation: `scripts/validate_setup.py`

## 4. Delivery Scope Snapshot (MVP)
- Product: Middle School Concert Band Transcription Assistant (offline/local-first)
- Inputs: local audio files and YouTube URL audio extraction
- Outputs: conductor score PDF + assigned/non-empty individual part PDFs
- Quality benchmark: 3 representative songs approved by teacher

## 5. Current Preferences (2026-02-19)
- No authentication for MVP (local trusted usage only).
- No in-app teacher rating/review workflow.
- Keep simplification profiles + advanced manual override.
- Keep quick rerun flow with run-scoped isolation.
- Persist last-used score options during session.
- Include pipeline metadata and simplification settings in run manifest.
