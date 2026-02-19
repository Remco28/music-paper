<!-- Example log -->
[2025-08-26 09:00] [Gemini]: SETUP: Initialized comms directory structure and logging protocol.

<!-- example log -->
[2026-02-19 19:03] [Architect]: MANIFEST READY: Created project-manifest.md with stable pointers, dynamic state, and MVP scope snapshot.
[2026-02-19 19:03] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-mvp-foundation-spec.md for MVP Phase 1 implementation handoff.
[2026-02-19 19:08] [Architect]: ARCH DOC READY: Created docs/ARCHITECTURE.md aligned to MVP spec (local-only, no auth, single-video YouTube input).
[2026-02-19 14:13] [CLAUDE]: IMPL IN_PROGRESS: Implementing MVP foundation app, pipeline, config, utilities, launcher, and teacher documentation from spec 2026-02-19.
[2026-02-19 14:16] [CLAUDE]: IMPL DONE: Completed MVP foundation implementation (Streamlit app, pipeline orchestration, simplification controls, local/YouTube input, PDF export wiring, launcher, and teacher README).
[2026-02-19 14:19] [Architect]: REVIEW IN_PROGRESS: Setting up local environment and starting implementation review for 2026-02-19-mvp-foundation-spec.
[2026-02-19 14:21] [Architect]: REVIEW FAIL: MVP foundation implementation has blocking issues (conductor score pitch mode, dependency installability, stale YouTube artifact selection).
[2026-02-19 14:21] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-mvp-foundation-revision-1.md for revision cycle.
[2026-02-19 14:25] [Architect]: SPEC READY: Updated revision spec with mandatory Python 3.11 policy, start.bat version guard requirement, and concrete verification checklist.
[2026-02-19 15:00] [CLAUDE]: IMPL IN_PROGRESS: Implementing revision-1 fixes (concert-pitch score, Python 3.11 policy, YouTube artifact isolation).
[2026-02-19 15:10] [CLAUDE]: IMPL DONE: Revision-1 complete. Signature changes: build_score returns dict (full_score + parts), render_pdfs accepts that dict. See summary below.
[2026-02-19 14:35] [Architect]: REVIEW FAIL: Revision-1 improved core issues but does not fully pass due missing install verification evidence and part-collision risk when multiple stems are assigned to the same instrument.
[2026-02-19 15:20] [CLAUDE]: IMPL IN_PROGRESS: Addressing review-2 findings (part-collision, stale venv, install evidence).
[2026-02-19 15:30] [CLAUDE]: IMPL DONE: Revision-1 patch applied. Details below.

REVISION-1 PATCH NOTES:
  1. [Medium] Part-collision fix (pipeline.py:188-199): Added instrument_counts tracker.
     When multiple stems share the same instrument, subsequent parts get a disambiguated
     label (e.g. "Bb Clarinet 1 (2)"). Unique filenames and dict keys; no silent overwrites.
  2. [Low] Stale venv fix (start.bat:22-28): After initial venv creation, the launcher now
     checks venv\Scripts\python --version for 3.11. If mismatched, it deletes and recreates.
  3. [High] Install verification evidence:
     - Dev environment has Python 3.12 only (WSL Ubuntu). Python 3.11 is not installed.
     - Ran dry-run install on 3.12: confirmed failure at basic-pitch build step with
       "ModuleNotFoundError: No module named 'distutils'" — validates the 3.11 policy.
     - Cannot run positive 3.11 install proof from this environment.
     - RECOMMENDATION: Acceptance criterion 3 requires a 3.11 environment (Windows target
       or CI) to produce positive install evidence. This is an environment gap, not a code gap.
[2026-02-19 15:17] [Architect]: REVIEW PENDING: Code fixes align with revision requirements; final acceptance blocked by missing local Python 3.11 verification due environment privilege limits (cannot install 3.11 from this session).
[2026-02-19 15:37] [Architect]: REVIEW PASS: Revision-1 accepted. Verified Python 3.11.11 venv and successful install of key dependencies (streamlit 1.54.0, demucs 4.0.1, basic-pitch 0.4.0).
[2026-02-19 15:38] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-2-validation-and-polish.md for next implementation cycle.
[2026-02-19 16:00] [CLAUDE]: IMPL IN_PROGRESS: Phase 2 — preflight checks, per-run isolation, export manifest, QC surface, validation script.
[2026-02-19 16:30] [CLAUDE]: IMPL DONE: Phase 2 complete. See summary below.

PHASE 2 IMPLEMENTATION NOTES:
  Files changed: config.py, utils.py, pipeline.py, app.py, README_for_teacher.md, project-manifest.md
  Files created: scripts/validate_setup.py

  1. Preflight Checks (app.py:69-85, utils.py:58-83, config.py:20-25)
     - REQUIRED_TOOLS list in config.py defines demucs, basic-pitch, mscore, ffmpeg
     - run_preflight_checks() probes each tool via subprocess
     - UI shows pass/fail per tool; blocks transcription on failures

  2. Per-Run Artifact Isolation (app.py:252-254, pipeline.py:117+167, config.py:9, utils.py:46-55)
     - RUNS_DIR = temp/runs/ added to config
     - create_run_id() generates timestamp ID; create_run_dir() creates temp/runs/<id>/
     - transcribe_to_midi and build_score accept optional run_dir parameter
     - MIDI, part MusicXML, full score MusicXML all scoped to run_dir
     - Audio prep and stem separation remain in global temp (exploratory steps)

  3. Export Manifest (utils.py:107-127, app.py:272-290)
     - write_run_manifest() writes JSON with: input source, assignments, part report
       (exported/skipped + reasons), tool versions
     - Manifest included in ZIP download

  4. Teacher QC Surface (app.py:207-227)
     - _render_part_report() shows per-part summary: name, note count, exported/skipped
     - Warnings displayed for skipped parts with reasons
     - Driven by render_pdfs() part_report return data

  5. Validation Script (scripts/validate_setup.py)
     - Standalone: checks Python 3.11, core packages, required executables
     - Exits non-zero on failures

  Signature changes:
    - render_pdfs: returns dict {"paths": [...], "part_report": [...]} (was list[str])
    - transcribe_to_midi: added optional run_dir param
    - build_score: added optional run_dir param
[2026-02-19 15:46] [Architect]: REVIEW FAIL: Phase-2 implementation is close but misses required run-scoped isolation for YouTube/stem artifacts and has non-deterministic run-id collision risk; preflight gating is also bypassable when checks are not run.
[2026-02-19 16:45] [CLAUDE]: IMPL DONE: Phase-2 review fixes applied. All py_compile checks pass.

PHASE-2 PATCH NOTES:
  1. [High] Full run-scoped isolation: download_or_convert_audio and separate_stems now
     accept run_dir parameter. YouTube artifacts, normalized WAV, and Demucs output all
     write into temp/runs/<run_id>/. Run created at audio input time (step 1) and carried
     through all subsequent steps via session state.
  2. [Medium] Run ID collision: changed format to include microseconds (%Y%m%d_%H%M%S_%f).
     create_run_dir now uses mkdir() without exist_ok — collision raises FileExistsError.
  3. [Medium] Mandatory preflight: export stage now blocks when preflight has not been run
     (not just when it has failures). User must click "Run Preflight Checks" and pass before
     transcription is allowed.
  4. [Low] ffmpeg via pydub: replaced direct ffmpeg subprocess check with pydub.utils.which("ffmpeg")
     path check. Config entry uses {"check": "pydub"} flag; run_preflight_checks handles it.
[2026-02-19 15:57] [Architect]: REVIEW PASS: Phase-2 implementation accepted. Run-scoped isolation, collision guard, mandatory preflight gating, manifest packaging, and QC surface verified.
[2026-02-19 15:59] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-3-quality-calibration-and-acceptance.md for next implementation cycle.
[2026-02-19 16:00] [CLAUDE]: IMPL IN_PROGRESS: Phase 3 — simplification profiles, run rating/notes, quick rerun, benchmark tracking document.
[2026-02-19 16:15] [CLAUDE]: IMPL DONE: Phase 3 complete. See summary below.

PHASE 3 IMPLEMENTATION NOTES:
  Files changed: config.py, utils.py, app.py, README_for_teacher.md, project-manifest.md
  Files created: docs/quality-benchmark.md

  1. Simplification Profiles (config.py:58-78, app.py:195-206)
     - SIMPLIFY_PROFILES dict with Conservative/Balanced/Aggressive parameter sets
     - DEFAULT_PROFILE = "Balanced"; SIMPLIFY_PRESET derived from it
     - Profile selector in UI pre-fills advanced controls; advanced expander overrides profile values

  2. Run Rating + Notes (app.py:373-397, utils.py:149-162)
     - New step 5 "Run Review" appears after export completes
     - Teacher sets rating (1-5), usable_for_rehearsal (yes/no), free-text notes
     - update_run_manifest() appends "review" block to existing manifest JSON
     - Schema is additive (backward-compatible)

  3. Quick Rerun (app.py:263-307, 344-352)
     - Extracted _run_export() helper (midi -> score -> pdf -> manifest -> zip)
     - "Quick Rerun" button shown when midi_map exists and stems are assigned
     - Creates new run_id/run_dir via _new_run(), then calls _run_export
     - Does NOT re-run audio input or Demucs — only transcription onward

  4. Benchmark Tracking (docs/quality-benchmark.md)
     - 3-song checklist template: title, source, profile, settings, run ID, rating, usable, notes, pass/fail
     - Acceptance decision section with 4-point checklist

  Signature changes:
    - options dict now includes "profile" key (selected profile name)
    - manifest_path stored in session state for review stage access
    - New function: update_run_manifest(manifest_path, rating, usable_for_rehearsal, notes)

[2026-02-19 16:06] [Architect]: REVIEW PASS: Phase-3 implementation accepted. Profiles, quick rerun with new run IDs, manifest review metadata, and benchmark template verified against spec.

[2026-02-19 16:07] [Architect]: SCOPE UPDATE: Removed Phase-3 in-app teacher review/rating flow and benchmark doc to keep MVP focused on core local transcription pipeline.

[2026-02-19 16:08] [Architect]: IMPLEMENTED: Run manifest now includes simplification reproducibility options (profile, simplify flag, quantize/min-duration/density).

[2026-02-19 16:09] [Architect]: PREFS UPDATED: No auth, no teacher review flow, keep profiles+advanced override, keep quick rerun, remember last-used options, include pipeline metadata in manifest.
[2026-02-19 16:09] [Architect]: IMPLEMENTED: Added manifest pipeline metadata, session-level option persistence, and post-export run summary block.
[2026-02-19 16:09] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-4-regression-safety-and-ops.md.

[2026-02-19 16:25] [Architect]: SELF-REVIEW: Found non-critical UX risk in option persistence visibility; addressed with explicit "Reset Advanced to Selected Profile" control. No unresolved app-breaking defects remain.
[2026-02-19 16:26] [Developer]: IMPL DONE (Phase 4): Added diagnostics panel, tool-path resolution helper, smoke test script, manifest schema doc, and release checklist.
[2026-02-19 16:26] [Developer]: FIXED: smoke_test import path initialization so script runs from repository root invocation path.

[2026-02-19 16:27] [Architect]: REVIEW PASS: Phase-4 implementation accepted after smoke-test path fix and diagnostics panel completion.
[2026-02-19 16:27] [Architect]: SPEC ARCHIVED: Moved comms/tasks/2026-02-19-phase-4-regression-safety-and-ops.md to archive.
[2026-02-19 16:27] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-5-output-quality-and-failure-clarity.md.

[2026-02-19 16:29] [Developer]: IMPL DONE (Phase 5): Added actionable part-skip guidance, simplification guardrails, structured stage-level error messaging, and docs/troubleshooting.md.

[2026-02-19 16:31] [Architect]: REVIEW FAIL (Phase 5): Stale success artifact regression. Failed export can still show prior run summary/download due to internal early returns without UI-state invalidation/gating.
[2026-02-19 16:31] [Architect]: REVISION SPEC READY: Added comms/tasks/2026-02-19-phase-5-revision-1.md.

[2026-02-19 16:33] [Developer]: IMPL DONE (Phase 5 Revision 1): Added explicit export success contract, stale output invalidation at export start, and success-surface render gating.
[2026-02-19 16:33] [Architect]: REVIEW PASS: Phase 5 accepted after Revision 1. Failure-state integrity now prevents stale artifacts from appearing after failed export/rerun attempts.
[2026-02-19 16:33] [Architect]: SPEC ARCHIVED: Moved phase-5 spec and phase-5-revision-1 spec to archive.
[2026-02-19 16:33] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-6-manifest-quality-and-run-history.md.

[2026-02-19 16:40] [Developer]: IMPL DONE (Phase 6): Added manifest outcome summary fields, defensive recent-run summary utilities, and in-app Recent Runs panel.
[2026-02-19 16:40] [Architect]: REVIEW PASS: Phase 6 accepted. Manifest outcome fields and run-history panel meet traceability requirements with graceful corrupt-manifest handling.
[2026-02-19 16:40] [Architect]: SPEC ARCHIVED: Moved phase-6 spec to archive.
[2026-02-19 16:40] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-7-export-ergonomics-and-audit-polish.md.
