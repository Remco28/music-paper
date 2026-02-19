# Task Spec: BTT Phase 2 - Validation and Teacher Polish

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Harden the MVP into a teacher-usable release candidate by improving runtime reliability, reviewability of outputs, and install/runtime ergonomics without changing core model choices.

## Rationale
Phase 1 proved core pipeline feasibility. The next minimum step is confidence and usability: predictable environment behavior, clear failure diagnostics, and a faster teacher feedback loop for output quality checks. This reduces iteration cost while preserving transcription quality priority.

## User Stories
1. As a teacher, I can quickly verify that generated parts are usable before handing them to students.
2. As a teacher, I can understand exactly which stage failed and how to recover.
3. As a maintainer, I can run a single validation script/checklist and know whether setup is healthy.

## In Scope
- Add environment + tool preflight checks surfaced in UI.
- Add run artifact manifest for each export (what was generated, skipped, and why).
- Add optional low-friction QC preview hooks in app (part list summary, durations, empty-part warnings).
- Improve deterministic temp/output lifecycle per run ID.
- Add a lightweight validation script for local setup confidence.

## Out of Scope
- New ML transcription models.
- Cloud/off-device execution.
- Multi-user auth.
- Batch library management.

## Required File Changes
- `app.py`
- `pipeline.py`
- `utils.py`
- `config.py`
- `README_for_teacher.md`
- `requirements.txt` (only if needed for added validation tooling)
- `scripts/validate_setup.py` (new)

## Required Functional Changes
1. **Preflight Checks**
   - Add explicit checks for required executables/libraries:
     - `demucs`, `basic-pitch`, `mscore`, ffmpeg availability via pydub path check
   - Show pass/fail table in Streamlit before transcription run.
   - Block run if required checks fail; provide actionable message.

2. **Per-Run Artifact Isolation**
   - Generate a run identifier (timestamp or UUID).
   - Store transient artifacts under `temp/runs/<run_id>/...`.
   - Ensure YouTube artifacts and stem/midi outputs are always run-scoped.

3. **Export Manifest**
   - Write JSON manifest per run in outputs folder containing:
     - input source type/path/url
     - assigned stems
     - generated part PDFs
     - skipped parts (with reason: unassigned/empty/failed)
     - major tool versions used
   - Include manifest in ZIP.

4. **Teacher QC Surface**
   - Show generated part summary in UI:
     - part name
     - note count (or non-empty marker)
     - exported/skipped status
   - If a part is skipped as empty, display warning and reason.

5. **Setup Validation Script**
   - Add `scripts/validate_setup.py` to print:
     - python version
     - package presence/versions for core deps
     - executable resolution for demucs/basic-pitch/mscore
   - Exit non-zero on required failures.

## Constraints
- Maintain existing function behavior unless explicitly extended.
- Keep current Phase 1 outputs unchanged in naming contract where possible.
- Avoid major UI redesign; add clarity, not complexity.

## Acceptance Criteria
1. App can display preflight check results and blocks run on hard failures.
2. Consecutive runs do not share temp artifacts.
3. ZIP output contains a run manifest JSON.
4. UI clearly identifies exported vs skipped parts and reasons.
5. `scripts/validate_setup.py` exits success on healthy setup and failure otherwise.
6. Existing Phase 1 capabilities still work (local + YouTube single video, simplification, score + assigned/non-empty parts).

## Pseudocode (High Level)
```text
on app load:
  preflight = run_preflight_checks()
  show preflight table

on transcribe:
  assert preflight pass
  run_id = new_run_id()
  workdir = temp/runs/run_id
  pipeline(workdir, options)
  manifest = collect_run_manifest(run_id, results, skips, versions)
  zip(outputs + manifest)
```

## Review Notes for Developer
- Keep logging/messages teacher-readable.
- Prefer additive changes with minimal signature breakage.
- Add at least one small self-check test or deterministic check around manifest generation.
