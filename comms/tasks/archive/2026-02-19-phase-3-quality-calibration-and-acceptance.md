# Task Spec: BTT Phase 3 - Quality Calibration and Acceptance

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add a practical quality-calibration workflow so the teacher can review, tune, and approve outputs across 3 representative songs with consistent criteria.

## Rationale
Core pipeline and reliability guardrails are in place. The next fundamental gap is decision quality: the teacher needs structured, repeatable controls and review data to decide whether outputs are rehearsal-ready. This phase converts “it runs” into “it is trusted.”

## User Stories
1. As a teacher, I can quickly compare simplification settings and keep the best result.
2. As a teacher, I can rate each run and record why it passed/failed for classroom use.
3. As a maintainer, I can see objective calibration records for the 3-song benchmark.

## In Scope
- Add run rating and review notes in app UI.
- Add per-run quality metadata to manifest.
- Add preset profiles for simplification (“Conservative”, “Balanced”, “Aggressive”).
- Add quick rerun flow using same stem assignments with only simplification/profile changes.
- Add benchmark tracking document for the 3-song acceptance gate.

## Out of Scope
- New transcription/separation models.
- Automatic orchestration/arrangement intelligence.
- Cloud sync, user accounts, or remote storage.

## Required File Changes
- `app.py`
- `config.py`
- `utils.py`
- `README_for_teacher.md`
- `docs/quality-benchmark.md` (new)

## Required Functional Changes
1. **Simplification Profiles**
   - Add 3 selectable profiles mapped to deterministic parameter sets:
     - `Conservative` (least simplification)
     - `Balanced` (default)
     - `Aggressive` (most simplification)
   - Advanced controls still available and override profile values.

2. **Run Rating + Notes**
   - After export, allow teacher to set:
     - `rating` (1-5)
     - `usable_for_rehearsal` (yes/no)
     - `notes` (short free text)
   - Save these fields into run manifest JSON.

3. **Quick Rerun**
   - Add button to rerun transcription/export with current loaded stems + assignments and updated simplification settings, without re-uploading/re-separating.
   - Must generate a new run ID and isolated run artifacts.

4. **Benchmark Tracking**
   - Add `docs/quality-benchmark.md` template with 3-song checklist:
     - song id/title
     - selected profile/settings
     - teacher rating
     - pass/fail
     - follow-up notes

## Constraints
- Preserve existing pipeline entry flow and Phase 2 checks.
- Do not remove manual advanced settings.
- Keep UI simple and teacher-readable.

## Acceptance Criteria
1. Teacher can select simplification profile and still override via advanced controls.
2. Each run manifest includes teacher rating, usability flag, and notes.
3. App supports rerun from existing prepared data (no new input upload required).
4. Rerun creates a distinct run ID and isolated artifacts.
5. `docs/quality-benchmark.md` exists and supports the 3-song acceptance process.
6. Existing behavior remains intact (inputs, preflight, manifests, score/parts export).

## Pseudocode (High Level)
```text
on options pane:
  profile = choose_profile()
  params = profile_defaults(profile)
  params = apply_advanced_overrides(params)

on export complete:
  collect teacher_rating + usable_flag + notes
  append to manifest and save

on quick rerun:
  assert stems + assignments exist
  create new run_id/run_dir
  rerun midi->score->pdf using current params
```

## Review Notes for Developer
- Keep profile defaults centralized in `config.py`.
- Ensure manifest schema remains backward-compatible (additive fields).
- Avoid rerunning demucs when quick rerun is used.
