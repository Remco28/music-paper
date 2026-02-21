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
- MVP finalization status: `docs/mvp-finalization-2026-02-19.md`
- Post-MVP backlog: `docs/post-mvp-backlog.md`
- Tuning strategy baseline: `docs/tuning-lab-strategy-2026-02-20.md`
- Musicality strategy baseline: `docs/musicality-lab-strategy-2026-02-21.md`
- Musicality runbook: `docs/musicality-lab-runbook.md`
- Musicality Lab foundation spec: `comms/tasks/2026-02-21-phase-41-musicality-lab-v1-foundation-spec.md`
- Tuning Lab implementation spec: `comms/tasks/2026-02-20-phase-39-tuning-lab-mvp-spec.md`
- Supported input policy: `docs/supported-input-policy.md`
- Success optimization spec: `comms/tasks/2026-02-20-phase-40-fit-gating-and-success-optimization.md`

## 3. Code & Config Entrypoints
- Main Streamlit app: `app.py`
- Pipeline logic: `pipeline.py`
- Project config/constants: `config.py`
- Utility helpers: `utils.py`
- Dependencies: `requirements.txt`
- Local launcher: `start.bat`
- Setup validation: `scripts/validate_setup.py`
- Musicality batch scorer: `scripts/musicality_eval_batch.py`
- Musicality scoring module: `scripts/musicality_score.py`
- Musicality review UI: `apps/musicality_lab.py`

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
