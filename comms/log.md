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

[2026-02-19 16:43] [Developer]: IMPL DONE (Phase 7): Added run-ID ZIP naming, export artifact summary (filename/size/run), and non-blocking export integrity warning against manifest outcome counts.
[2026-02-19 16:43] [Architect]: REVIEW PASS: Phase 7 accepted. Export naming, summary visibility, and audit warning behavior meet ergonomics/audit criteria.
[2026-02-19 16:43] [Architect]: SPEC ARCHIVED: Moved phase-7 spec to archive.
[2026-02-19 16:43] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-8-history-filtering-and-manifest-resilience.md.

[2026-02-19 16:46] [Developer]: IMPL DONE (Phase 8): Added manifest outcome.success, resilient history status parsing, and Recent Runs filter controls (input/status).
[2026-02-19 16:46] [Architect]: REVIEW PASS: Phase 8 accepted. Filters work, missing/partial manifests default safely, and outcome.success is additive/backward-compatible.
[2026-02-19 16:46] [Architect]: SPEC ARCHIVED: Moved phase-8 spec to archive.
[2026-02-19 16:46] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-9-lightweight-ops-controls-and-cleanup.md.

[2026-02-19 16:47] [Developer]: IMPL IN_PROGRESS (Phase 9): Adding maintenance cleanup panel with safe run-prune controls and docs/test updates.
[2026-02-19 16:48] [Developer]: IMPL DONE (Phase 9): Added run artifact maintenance panel, safe prune helper (keep latest N + active run protection), and cleanup docs/smoke coverage.
[2026-02-19 16:48] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-9 implementation against cleanup safety and acceptance criteria.
[2026-02-19 16:48] [Architect]: REVIEW PASS: Phase 9 accepted. Confirmed explicit prune confirmation, active-run protection, deterministic keep-latest behavior, reclaimed-size reporting, and passing smoke checks.
[2026-02-19 16:48] [Architect]: SPEC ARCHIVED: Moved phase-9 spec to comms/tasks/archive/.
[2026-02-19 16:48] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-10-run-detail-inspection-and-artifact-reopen.md.
[2026-02-19 16:50] [Developer]: IMPL IN_PROGRESS (Phase 10): Adding run-detail inspector and prior-zip reopen from manifest-backed recent runs.
[2026-02-19 16:51] [Developer]: IMPL DONE (Phase 10): Added recent-run detail inspector, safe manifest loader statuses (ok/missing/corrupt), and prior ZIP reopen/download controls.
[2026-02-19 16:51] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-10 run-detail/reopen behavior and resilience paths.
[2026-02-19 16:51] [Architect]: REVIEW PASS: Phase 10 accepted. Selected-run details render from manifest, missing/corrupt/absent-ZIP cases are non-blocking, and smoke/compile checks pass.
[2026-02-19 16:51] [Architect]: SPEC ARCHIVED: Moved phase-10 spec to comms/tasks/archive/.
[2026-02-19 16:51] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-11-run-config-reapply-and-manifest-detail-polish.md.
[2026-02-19 16:52] [Developer]: IMPL IN_PROGRESS (Phase 11): Adding selected-run part summary and apply-settings action for simplification options.
[2026-02-19 16:53] [Developer]: IMPL DONE (Phase 11): Added selected-run part summary and one-click apply-settings action with safe validation for simplification options.
[2026-02-19 16:53] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-11 run-config reapply and manifest detail behavior.
[2026-02-19 16:53] [Architect]: REVIEW PASS: Phase 11 accepted. Option reapply updates only valid fields, part summary is resilient to malformed manifests, and compile/smoke checks pass.
[2026-02-19 16:53] [Architect]: SPEC ARCHIVED: Moved phase-11 spec to comms/tasks/archive/.
[2026-02-19 16:53] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-12-manifest-versioning-and-compatibility-guards.md.
[2026-02-19 16:53] [Developer]: IMPL IN_PROGRESS (Phase 12): Implementing manifest schema versioning and compatibility normalization across readers/UI/docs/tests.
[2026-02-19 16:55] [Developer]: IMPL DONE (Phase 12): Added manifest schema_version write path, normalization compatibility helper, and schema visibility in selected run details.
[2026-02-19 16:55] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-12 schema versioning and compatibility behavior.
[2026-02-19 16:55] [Architect]: REVIEW PASS: Phase 12 accepted. New manifests are versioned, legacy/unversioned manifests remain readable, and compile/smoke checks pass.
[2026-02-19 16:55] [Architect]: SPEC ARCHIVED: Moved phase-12 spec to comms/tasks/archive/.
[2026-02-19 16:55] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-13-history-search-and-limit-controls.md.
[2026-02-19 16:56] [Developer]: IMPL IN_PROGRESS (Phase 13): Adding Recent Runs run-id search and configurable history-limit controls with resilient selection behavior.
[2026-02-19 16:57] [Developer]: IMPL DONE (Phase 13): Added Recent Runs run-id search and history-limit controls (5/10/20) with stable selected-run behavior under filtering.
[2026-02-19 16:57] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-13 history search/limit controls and selection resilience.
[2026-02-19 16:57] [Architect]: REVIEW PASS: Phase 13 accepted. Search and bounded limit controls work with existing filters/details, and compile/smoke checks pass.
[2026-02-19 16:57] [Architect]: SPEC ARCHIVED: Moved phase-13 spec to comms/tasks/archive/.
[2026-02-19 16:57] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-14-manifest-and-zip-presence-health-surface.md.
[2026-02-19 17:00] [Developer]: IMPL IN_PROGRESS (Phase 14): Adding Recent Runs health summary for manifest readability and ZIP presence across the filtered bounded set.
[2026-02-19 17:00] [Developer]: IMPL DONE (Phase 14): Added Recent Runs health summary metrics for filtered bounded runs (manifest readability + ZIP presence).
[2026-02-19 17:00] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-14 health surface integration and non-blocking behavior.
[2026-02-19 17:00] [Architect]: REVIEW PASS: Phase 14 accepted. Health metrics are scoped and lightweight, existing run-detail workflows remain intact, and compile/smoke checks pass.
[2026-02-19 17:00] [Architect]: SPEC ARCHIVED: Moved phase-14 spec to comms/tasks/archive/.
[2026-02-19 17:00] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-15-recent-runs-copyable-summary-and-session-note.md.
[2026-02-19 17:01] [Developer]: IMPL IN_PROGRESS (Phase 15): Adding session note and copyable Recent Runs operational summary block.
[2026-02-19 17:01] [Developer]: IMPL DONE (Phase 15): Added session-note input and copyable Recent Runs summary block (filters, health, run lines, optional note).
[2026-02-19 17:01] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-15 copyable summary behavior and non-destructive guarantees.
[2026-02-19 17:01] [Architect]: REVIEW PASS: Phase 15 accepted. Summary is session-only/non-destructive, reflects current filters and health metrics, and compile/smoke checks pass.
[2026-02-19 17:01] [Architect]: SPEC ARCHIVED: Moved phase-15 spec to comms/tasks/archive/.
[2026-02-19 17:01] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-16-diagnostics-copyable-environment-snapshot.md.
[2026-02-19 17:02] [Developer]: IMPL IN_PROGRESS (Phase 16): Adding copyable Diagnostics environment snapshot and troubleshooting doc guidance.
[2026-02-19 17:03] [Developer]: IMPL DONE (Phase 16): Added Copyable Diagnostics Summary in Diagnostics panel using current environment/tool data.
[2026-02-19 17:03] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-16 diagnostics snapshot behavior and non-destructive constraints.
[2026-02-19 17:03] [Architect]: REVIEW PASS: Phase 16 accepted. Diagnostics snapshot is copy-friendly/session-local and compile/smoke checks pass.
[2026-02-19 17:03] [Architect]: SPEC ARCHIVED: Moved phase-16 spec to comms/tasks/archive/.
[2026-02-19 17:03] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-17-preflight-snapshot-and-change-indicator.md.
[2026-02-19 17:06] [Developer]: IMPL IN_PROGRESS (Phase 17): Added preflight snapshot capture and changed/unchanged indicator using tool status + resolved paths.
[2026-02-19 17:06] [Developer]: IMPL DONE (Phase 17): Added session preflight baseline/snapshot comparison and changed-tool indicator messaging.
[2026-02-19 17:06] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-17 preflight snapshot/change indicator behavior.
[2026-02-19 17:06] [Architect]: REVIEW PASS: Phase 17 accepted. Indicator correctly reports baseline/no-change/changed tools, remains non-blocking, and validation checks pass.
[2026-02-19 17:06] [Architect]: SPEC ARCHIVED: Moved phase-17 spec to comms/tasks/archive/.
[2026-02-19 17:06] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-18-preflight-staleness-and-reminder-surface.md.
[2026-02-19 17:07] [Developer]: IMPL IN_PROGRESS (Phase 18): Adding preflight freshness timestamp/age indicator and stale reminder with diagnostics snapshot integration.
[2026-02-19 17:08] [Developer]: IMPL DONE (Phase 18): Added preflight freshness (last-run timestamp + age), stale reminder, and diagnostics snapshot freshness lines.
[2026-02-19 17:08] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-18 preflight staleness/reminder behavior and diagnostics integration.
[2026-02-19 17:08] [Architect]: REVIEW PASS: Phase 18 accepted. Freshness context and stale reminders are advisory/non-blocking, diagnostics include preflight timing, and validation checks pass.
[2026-02-19 17:08] [Architect]: SPEC ARCHIVED: Moved phase-18 spec to comms/tasks/archive/.
[2026-02-19 17:08] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-19-reset-workspace-safety-confirmation.md.
[2026-02-19 17:09] [Developer]: IMPL IN_PROGRESS (Phase 19): Adding reset workspace impact preview and explicit confirmation gate.
[2026-02-19 17:10] [Developer]: IMPL DONE (Phase 19): Added reset impact preview + explicit confirmation gate; preserved reset semantics post-confirmation.
[2026-02-19 17:10] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-19 reset safety confirmation and impact preview behavior.
[2026-02-19 17:10] [Architect]: REVIEW PASS: Phase 19 accepted. Reset is now confirmation-gated with clear preview, remains deterministic, and validation checks pass.
[2026-02-19 17:10] [Architect]: SPEC ARCHIVED: Moved phase-19 spec to comms/tasks/archive/.
[2026-02-19 17:10] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-20-run-history-export-csv-lite.md.
[2026-02-19 17:14] [Developer]: IMPL IN_PROGRESS (Phase 20): Adding scoped Recent Runs CSV download from current filtered record set.
[2026-02-19 17:15] [Developer]: IMPL DONE (Phase 20): Added Recent Runs CSV export for current filtered set with deterministic columns and timestamped filename.
[2026-02-19 17:15] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-20 scoped CSV export behavior and compatibility with existing history panel features.
[2026-02-19 17:15] [Architect]: REVIEW PASS: Phase 20 accepted. CSV export is correctly scoped/non-destructive with stable columns, and validation checks pass.
[2026-02-19 17:15] [Architect]: SPEC ARCHIVED: Moved phase-20 spec to comms/tasks/archive/.
[2026-02-19 17:15] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-21-history-table-clarity-polish.md.
[2026-02-19 17:16] [Developer]: IMPL IN_PROGRESS (Phase 21): Applying Recent Runs table presentation polish (labels/status wording/truncation) with no behavior changes.
[2026-02-19 17:16] [Developer]: IMPL DONE (Phase 21): Polished Recent Runs table headers/status wording/truncation for readability with no behavior changes.
[2026-02-19 17:16] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-21 presentation-layer table clarity changes.
[2026-02-19 17:16] [Architect]: REVIEW PASS: Phase 21 accepted. Readability improved with explicit outcome/manifest/ZIP labels and no regressions in history behavior.
[2026-02-19 17:16] [Architect]: SPEC ARCHIVED: Moved phase-21 spec to comms/tasks/archive/.
[2026-02-19 17:16] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-22-run-outcome-status-contract-tightening.md.
[2026-02-19 17:17] [Developer]: IMPL IN_PROGRESS (Phase 22): Centralizing outcome status derivation (success/failed/unknown) in manifest normalization and propagating to UI filters/details/docs/tests.
[2026-02-19 17:18] [Developer]: IMPL DONE (Phase 22): Tightened normalized run outcome status contract to success/failed/unknown across read paths, filters, and detail surfaces.
[2026-02-19 17:18] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-22 status contract tightening and backward compatibility behavior.
[2026-02-19 17:18] [Architect]: REVIEW PASS: Phase 22 accepted. Failed runs are now distinguishable from unknown legacy runs, UI filters include failed, and validation checks pass.
[2026-02-19 17:18] [Architect]: SPEC ARCHIVED: Moved phase-22 spec to comms/tasks/archive/.
[2026-02-19 17:18] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-23-input-validation-hardening.md.
[2026-02-19 17:19] [Developer]: IMPL IN_PROGRESS (Phase 23): Hardening local-file and YouTube URL validation at input stage with clear fail-fast guidance.
[2026-02-19 17:20] [Developer]: IMPL DONE (Phase 23): Added fail-fast local upload and YouTube URL validation with clearer actionable input errors.
[2026-02-19 17:20] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-23 input validation hardening and behavior preservation.
[2026-02-19 17:20] [Architect]: REVIEW PASS: Phase 23 accepted. Invalid input now fails early with clear guidance while valid paths remain unchanged; validation checks pass.
[2026-02-19 17:20] [Architect]: SPEC ARCHIVED: Moved phase-23 spec to comms/tasks/archive/.
[2026-02-19 17:20] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-24-assignment-safety-guards.md.
[2026-02-19 17:21] [Developer]: IMPL IN_PROGRESS (Phase 24): Adding assignment safety guards (minimum blocking check + non-blocking quality warnings).
[2026-02-19 17:21] [Developer]: IMPL DONE (Phase 24): Added assignment safety guards (coverage summary, non-blocking quality warnings, and explicit minimum-assignment block at export).
[2026-02-19 17:21] [Architect]: REVIEW IN_PROGRESS: Reviewing Phase-24 assignment safety guard behavior and workflow compatibility.
[2026-02-19 17:21] [Architect]: REVIEW PASS: Phase 24 accepted. Minimum assignment block and warning surfaces behave as intended without over-constraining valid workflows.
[2026-02-19 17:21] [Architect]: SPEC ARCHIVED: Moved phase-24 spec to comms/tasks/archive/.
[2026-02-19 17:21] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-25-export-package-consistency-checks.md.
[2026-02-19 17:26] [Architect]: REVIEW COMPLETE: Added broad health assessment at docs/health-review-2026-02-19.md with prioritized risks and stabilization recommendations.
[2026-02-19 17:26] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-pre-final-stabilization-package.md.
[2026-02-19 17:26] [Architect]: SPEC READY: Added STAB-1..STAB-4 specs for diagnostics performance, URL rule unification, PDF isolation hardening, and smoke expansion.
[2026-02-19 17:26] [Architect]: SEQUENCE UPDATE: Phase 25 feature work deferred until stabilization package completion.
[2026-02-19 17:31] [Developer]: IMPL DONE (STAB-1): Hardened Diagnostics probe overhead via session-scoped probe cache + explicit refresh action + probe timestamp surface.
[2026-02-19 17:31] [Architect]: REVIEW PASS (STAB-1): Diagnostics remains functionally equivalent while avoiding repeated subprocess probes on ordinary rerenders.
[2026-02-19 17:31] [Developer]: IMPL DONE (STAB-2): Unified source/YouTube URL validation/classification in utils and applied consistently across app input gating and pipeline source handling.
[2026-02-19 17:31] [Architect]: REVIEW PASS (STAB-2): App/pipeline source decisions now align for the same URL inputs with single-video constraints preserved.
[2026-02-19 17:31] [Developer]: IMPL DONE (STAB-3): Made PDF rendering run-scoped (`outputs/<run_id>/`) and wired export orchestration to pass run_id; updated export verification docs.
[2026-02-19 17:31] [Architect]: REVIEW PASS (STAB-3): Cross-run PDF overwrite risk removed while preserving ZIP packaging and manifest traceability.
[2026-02-19 17:31] [Developer]: IMPL DONE (STAB-4): Expanded smoke coverage to include outcome-status contract assertions and deterministic source-validation helper checks.
[2026-02-19 17:31] [Architect]: REVIEW PASS (STAB-4): Stabilization package complete; compile and smoke checks pass in project venv.
[2026-02-19 17:31] [Architect]: PHASE SEQUENCING UPDATE: Pre-final stabilization package accepted; Phase 25 may resume on stabilized baseline.
[2026-02-19 17:35] [Developer]: IMPL DONE (Phase 25): Added post-package ZIP consistency checks (manifest/full-score MusicXML presence + part-PDF count/name alignment) with non-blocking warning surface reuse.
[2026-02-19 17:35] [Developer]: DOCS/TESTS UPDATED (Phase 25): Updated docs/export-verification.md and expanded smoke coverage for ZIP inspection helper.
[2026-02-19 17:35] [Architect]: REVIEW PASS (Phase 25): Export packaging trust checks are in place, non-destructive, and existing validation gates pass.
[2026-02-19 17:39] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-26-manifested-export-warning-traceability.md.
[2026-02-19 17:39] [Developer]: IMPL DONE (Phase 26): Persisted export/package warning list to manifest outcome (`integrity_warnings`) and surfaced warning summary in selected-run details.
[2026-02-19 17:39] [Developer]: DOCS/TESTS UPDATED (Phase 26): Updated manifest/export docs and expanded smoke coverage for integrity warning normalization + persistence helper.
[2026-02-19 17:39] [Architect]: REVIEW PASS (Phase 26): Warning traceability is additive/backward-compatible and compile/smoke checks pass.
[2026-02-19 17:42] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-27-recent-runs-warning-visibility-and-filtering.md.
[2026-02-19 17:42] [Developer]: IMPL DONE (Phase 27): Added Recent Runs warning-state filter and warning-count visibility across table, copy summary, health caption, and CSV export.
[2026-02-19 17:42] [Developer]: DOCS UPDATED (Phase 27): Updated docs/run-history.md with warning count/filter/CSV field behavior.
[2026-02-19 17:42] [Architect]: REVIEW PASS (Phase 27): Warning presence is now first-class in run history while preserving additive, backward-compatible behavior.
[2026-02-19 17:43] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-28-warning-triage-rollups-and-preview.md.
[2026-02-19 17:43] [Developer]: IMPL DONE (Phase 28): Added warning preview and warning-category rollup surfaces in Recent Runs table, health caption, copy summary, and CSV export.
[2026-02-19 17:43] [Developer]: DOCS UPDATED (Phase 28): Updated docs/run-history.md with warning preview/rollup/CSV behavior.
[2026-02-19 17:43] [Architect]: REVIEW PASS (Phase 28): Warning triage context is richer while preserving existing warning generation and compatibility behavior.
[2026-02-19 17:45] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-29-warning-category-filter-and-selected-run-digest.md.
[2026-02-19 17:45] [Developer]: IMPL DONE (Phase 29): Added warning category query filter, warning categories table column, and selected-run copyable warning digest.
[2026-02-19 17:45] [Developer]: DOCS UPDATED (Phase 29): Updated docs/run-history.md for warning category filter and warning digest behavior.
[2026-02-19 17:45] [Architect]: REVIEW PASS (Phase 29): Warning triage depth improved without changing warning generation or export contracts; validations pass.
[2026-02-19 17:47] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-30-run-history-sort-and-filter-first-limiting.md.
[2026-02-19 17:47] [Developer]: IMPL DONE (Phase 30): Added Recent Runs sort mode and changed processing order to filter/sort first, then apply history limit; updated summary/count surfaces accordingly.
[2026-02-19 17:47] [Developer]: DOCS UPDATED (Phase 30): Updated docs/run-history.md for sort options and filter-first limit behavior.
[2026-02-19 17:47] [Architect]: REVIEW PASS (Phase 30): Discoverability improved (no pre-limit filter blind spots) with deterministic sorting and no regressions in validation checks.
[2026-02-19 17:51] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-31-recent-runs-manifest-cache-and-refresh-control.md.
[2026-02-19 17:51] [Developer]: IMPL DONE (Phase 31): Added session-scoped Recent Runs manifest cache with auto-refresh on run/manifest signature changes and explicit Refresh Run Cache control.
[2026-02-19 17:51] [Developer]: DOCS UPDATED (Phase 31): Updated docs/run-history.md with run-cache refresh behavior and timestamp surface.
[2026-02-19 17:51] [Architect]: REVIEW PASS (Phase 31): Recent Runs rerender overhead reduced while preserving existing filter/sort/CSV/detail behavior; validation checks pass.
[2026-02-19 17:53] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-32-run-cache-auto-refresh-toggle-and-staleness-indicator.md.
[2026-02-19 17:53] [Developer]: IMPL DONE (Phase 32): Added Auto Refresh Run Cache toggle, cache freshness age display, stale reminder, and signature-drift note when auto refresh is disabled.
[2026-02-19 17:53] [Developer]: DOCS UPDATED (Phase 32): Updated docs/run-history.md for cache auto-refresh and staleness/drift behavior.
[2026-02-19 17:53] [Architect]: REVIEW PASS (Phase 32): Cache-control behavior is explicit/non-blocking and existing Recent Runs workflows remain intact; validations pass.
[2026-02-19 17:55] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-33-three-song-benchmark-evidence-pass.md.
[2026-02-19 17:55] [Developer]: IMPL DONE (Phase 33): Added docs/benchmark-3-song-pass.md with 3-song protocol, severity rubric, per-song evidence capture, and final PASS/FAIL decision block.
[2026-02-19 17:55] [Developer]: DOCS UPDATED (Phase 33): Integrated benchmark gating in docs/release-checklist.md and linked benchmark worksheet from README_for_teacher.md.
[2026-02-19 17:55] [Architect]: REVIEW PASS (Phase 33): Benchmark evidence workflow is now defined and release-gated without introducing runtime complexity.
[2026-02-19 17:58] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-34-core-workflow-ux-clarity-polish.md.
[2026-02-19 17:58] [Developer]: IMPL DONE (Phase 34): Added top-level workflow snapshot and clarified core action labels/captions across input/stem/export stages.
[2026-02-19 17:58] [Developer]: DOCS UPDATED (Phase 34): Updated README_for_teacher.md to reference workflow snapshot for stage readiness.
[2026-02-19 17:58] [Architect]: REVIEW PASS (Phase 34): UX clarity improved with no pipeline behavior changes; validation checks pass.
[2026-02-19 18:00] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-35-failure-traceability-and-failed-run-manifest-hardening.md.
[2026-02-19 18:00] [Developer]: IMPL DONE (Phase 35): Added failed-run manifest hardening with outcome failure context fields (`failure_stage`, `failure_summary`) and best-effort failed-manifest persistence for export stage failures.
[2026-02-19 18:00] [Developer]: DOCS/TESTS UPDATED (Phase 35): Updated manifest schema + troubleshooting docs and expanded smoke coverage for failure-context normalization/persistence helpers.
[2026-02-19 18:00] [Architect]: REVIEW PASS (Phase 35): Failed runs now retain actionable manifest-backed context in run history/details while preserving backward compatibility and passing validations.
[2026-02-19 18:04] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-36-documentation-and-handoff-consolidation.md.
[2026-02-19 18:04] [Developer]: IMPL DONE (Phase 36): Consolidated teacher/maintainer docs to align with current workflow labels, run-history behavior, manifest outcome fields, and handoff sequence.
[2026-02-19 18:04] [Developer]: DOCS UPDATED (Phase 36): Updated README_for_teacher.md, docs/ARCHITECTURE.md, docs/release-checklist.md, and docs/run-history.md.
[2026-02-19 18:04] [Architect]: REVIEW PASS (Phase 36): Documentation now matches current app behavior through Phase 35 with a clear setup->benchmark->release handoff path.
[2026-02-19 18:05] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-37-rc-freeze-and-validation-gate.md.
[2026-02-19 18:05] [Developer]: VALIDATION RUN (Phase 37): py_compile PASS, smoke PASS, setup validator FAIL due missing external executables (`demucs`, `basic-pitch`, `mscore`, `ffmpeg`) on this environment PATH.
[2026-02-19 18:05] [Developer]: REPORT READY (Phase 37): Added docs/release-candidate-report-2026-02-19.md with freeze policy, validation evidence, pending gates, and blocker list.
[2026-02-19 18:05] [Architect]: REVIEW PASS (Phase 37): RC gate documentation is complete and actionable; final sign-off correctly deferred pending environment + benchmark gates.
[2026-02-19 18:08] [Architect]: SPEC READY: Added comms/tasks/2026-02-19-phase-38-mvp-finalization-and-post-mvp-backlog.md.
[2026-02-19 18:08] [Developer]: IMPL DONE (Phase 38): Added MVP finalization record and post-MVP prioritized backlog; updated project manifest pointers.
[2026-02-19 18:08] [Developer]: VALIDATION (Phase 38): py_compile PASS and smoke PASS on current baseline.
[2026-02-19 18:08] [Architect]: REVIEW PASS (Phase 38): MVP phase sequence is closed with explicit conditional readiness and actionable pending gates.
[2026-02-19 18:31] [Architect]: REVISION PASS START: Applying targeted part-export correctness patch for title metadata and instrument-clef enforcement.
[2026-02-19 18:31] [Developer]: IMPL DONE (Revision): Updated pipeline part export to apply explicit instrument + preferred clef policy and part-level metadata (title/composer) before MusicXML write.
[2026-02-19 18:31] [Architect]: REVIEW PASS (Revision): py_compile + smoke passed; ready for in-app retest of clarinet clef/title correctness.
[2026-02-19 18:42] [Architect]: REVISION PASS START: Addressing repeated "Instrument change" engraving artifact observed in regenerated PDFs.
[2026-02-19 18:42] [Developer]: IMPL DONE (Revision): Normalized each part to a single instrument object (removed embedded MIDI-import instrument events), then applied notation cleanup (`makeNotation`) before MusicXML export.
[2026-02-19 18:42] [Architect]: REVIEW PASS (Revision): py_compile + smoke passed; ready for re-export verification that instrument-change text no longer appears.
[2026-02-19 19:07] [Developer]: IMPL DONE (Revision): Fixed percussion clef regression by routing percussion-family instruments (e.g., Snare Drum) to `PercussionClef` instead of treble clef.
[2026-02-19 19:07] [Architect]: REVIEW PASS (Revision): End-to-end local generation rerun complete; no `Instrument change`/`Music21 Fragment` markers found in generated MusicXML, and snare part now emits percussion clef.
[2026-02-20 10:12] [Developer]: TOOLING UPDATE: Added `pypdf` to requirements and validated PDF text-content checks for generated outputs (no `Instrument change` / `Music21 Fragment` markers detected).
[2026-02-20 10:18] [Architect]: BACKLOG UPDATE: Deferred outputs/downloads artifact retention policy decisions; added explicit post-MVP TODO for separate retention controls.
[2026-02-20 10:34] [Developer]: IMPL DONE (Revision): Fixed simplify pass no-op by enabling recursive quantization and stream-owned element mutation; corrected density bucketing to use part-global offsets.
[2026-02-20 10:34] [Developer]: TESTING EVIDENCE: Profile benchmark now shows simplification effect on melody parts (off/conservative/balanced/aggressive produce distinct note-density outcomes).
[2026-02-20 10:34] [Developer]: TESTS UPDATED: Added smoke guard `simplify part effectiveness` to prevent future no-op regressions.
[2026-02-20 10:34] [Architect]: REVIEW PASS (Revision): py_compile + smoke pass; simplification behavior is now functionally active and measurable.
[2026-02-20 10:52] [Developer]: IMPL DONE (UX): Added post-export Complexity Summary block (per-part difficulty, fast-note count, tuplet count, avg duration, page count) for teacher-facing simplification decisions.
[2026-02-20 10:52] [Developer]: DOCS/VALIDATION: Updated README_for_teacher.md and verified py_compile + smoke pass.
[2026-02-20 11:07] [Developer]: IMPL DONE (UX/Terminology): Renamed simplification profiles to `Beginner`, `Easy Intermediate` (default), and `Intermediate`.
[2026-02-20 11:07] [Developer]: COMPATIBILITY: Added legacy profile alias mapping (`Aggressive`->`Beginner`, `Balanced`->`Easy Intermediate`, `Conservative`->`Intermediate`) for manifest option reapply.
[2026-02-20 11:07] [Developer]: VALIDATION: py_compile + smoke pass; relabel comparison run confirms expected difficulty ordering and preserved title/clef/no-spam PDF quality.
[2026-02-20 11:28] [Developer]: IMPL DONE (Revision): Added Beginner melody-aware cleanup + playability gate in pipeline with explicit `unplayable_beginner` skipped-part reason propagation.
[2026-02-20 11:28] [Developer]: VALIDATION EVIDENCE: Replayed Laufey run artifacts; Beginner now blocks non-playable melodic parts (clarinet/sax/trombone) and exports safe subset; Easy Intermediate remains available for fuller draft output.
[2026-02-20 11:28] [Developer]: UX POLISH: Complexity summary now reports accidental/leap metrics and ignores percussion for those pitch-based indicators.
[2026-02-20 11:36] [Developer]: IMPL DONE (Labeling UX): Added `scripts/prepare_labeling_pack.py` to auto-generate student-friendly labeling CSV + markdown review packet from existing run manifests/part PDFs.
[2026-02-20 11:36] [Developer]: DOCS UPDATED: Added `docs/labeling-playability.md` and linked it from README for quick reviewer onboarding.
[2026-02-20 12:05] [Architect]: STRATEGY UPDATE: Adopted separate Tuning Lab calibration track; added durable strategy doc `docs/tuning-lab-strategy-2026-02-20.md`.
[2026-02-20 12:05] [Architect]: SPEC READY: Added Phase 39 Tuning Lab MVP implementation spec `comms/tasks/2026-02-20-phase-39-tuning-lab-mvp-spec.md`.
[2026-02-20 12:05] [Developer]: DOCS UPDATED: Linked Tuning Lab strategy/spec in `project-manifest.md` and added calibration addendum in `docs/plan.md`.
[2026-02-20 12:26] [Architect]: POLICY UPDATE: Narrowed production target scope to beginner-focused classroom outcomes; added `docs/supported-input-policy.md`.
[2026-02-20 12:26] [Developer]: IMPL DONE (UX Scope): Teacher simplification profile selector now exposes only `Beginner` and `Easy Intermediate`.
[2026-02-20 12:26] [Architect]: SPEC READY: Added Phase 40 success-optimization spec `comms/tasks/2026-02-20-phase-40-fit-gating-and-success-optimization.md` (fit scoring + auto recommendation + two-pass + guardrails).
[2026-02-20 12:49] [Developer]: IMPL DONE (Phase 40 Step 1/2): Added pre-export `Analyze Song Fit` flow with fit scoring (`Good Fit`/`Borderline`/`Poor Fit`) and plain-language rationale.
[2026-02-20 12:49] [Developer]: IMPL DONE (Phase 40 Step 1/2): Added auto profile recommendation (`Beginner`/`Easy Intermediate`) with optional auto-apply on export and manifest persistence (`fit_score`, `fit_label`, `recommended_profile`).
[2026-02-20 12:49] [Architect]: REVIEW PASS (Phase 40 Step 1/2): compile + smoke pass; run history and selected-run details now surface fit/recommendation metadata.
[2026-02-20 13:08] [Developer]: IMPL DONE (Phase 40 Step 2/2): Added optional two-pass export mode that generates both `Beginner` and `Easy Intermediate` ZIP packages with explicit per-profile download buttons.
[2026-02-20 13:08] [Developer]: IMPL DONE (Phase 40 Step 2/2): Added workflow snapshot fit-state indicator and tightened beginner playability gates by instrument family in pipeline.
[2026-02-20 13:08] [Architect]: REVIEW PASS (Phase 40 Step 2/2): compile + smoke pass after two-pass flow + family-threshold gating updates.
[2026-02-20 15:20] [Developer]: IMPL DONE (Phase 39 MVP): Added separate Tuning Lab app entrypoint `apps/tuning_lab.py` with round selection, embedded PDF review, auto-save rubric, progress, and resume-by-reviewer workflow.
[2026-02-20 15:20] [Developer]: IMPL DONE (Phase 39 MVP): Added `scripts/generate_tuning_batch.py` and `scripts/score_tuning_round.py` plus runbook `docs/tuning-lab.md`.
[2026-02-20 15:20] [Developer]: ROUND READY: Created first tuning round manifest at `datasets/tuning_rounds/cheers_phase40_round1/round_manifest.json` from two-pass Cheers exports.
[2026-02-20 10:58] [Architect]: SCOPE UPDATE (Tuning Lab): Re-focused evaluation to clarinet/sax reviewer strengths; no prior round data preservation required.
[2026-02-20 10:58] [Developer]: IMPL DONE (Tuning Lab Batch Filters): Added `--include-part-keyword` and `--allowed-profile` filters to `scripts/generate_tuning_batch.py`.
[2026-02-20 10:58] [Developer]: ROUND READY: Created `datasets/tuning_rounds/woodwinds_round1/round_manifest.json` with clarinet/sax-only samples and Beginner/Easy Intermediate profiles.
[2026-02-20 11:54] [Developer]: IMPL DONE (Revision): Added woodwind sanitization pass in pipeline with contour-aware monophony, instrument-range clamps, and overlap-bucket cleanup (no chordify).
[2026-02-20 11:54] [Developer]: VALIDATION EVIDENCE: New tuned run `woodwinds_tune3_easy-intermediate_20260220_115415` exports Alto Sax + Bb Clarinet parts (previous tune1/tune2 had woodwind no-note skips).
[2026-02-20 11:54] [Developer]: TOOLING UPDATE: Added Gemini pack reset behavior and prepared clean `datasets/Gemini/woodwinds_gemini_round2` for screenshot review.
[2026-02-20 12:12] [Developer]: IMPL DONE (Revision): Added explicit woodwind primary-voice flattening and measure-duration rebalance pass before notation/export.
[2026-02-20 12:12] [Developer]: VALIDATION EVIDENCE: `woodwinds_tune4_easy-intermediate_20260220_121213` now exports 4 parts with zero voice objects on Alto Sax/Bb Clarinet part MusicXML.
[2026-02-20 12:12] [Developer]: ROUND READY: Prepared `datasets/Gemini/woodwinds_gemini_round3` from tune4 runs for screenshot review.
[2026-02-20 23:00] [Developer]: IMPL DONE (Round 4 revision): Added global score-measure alignment pass, extended monophony sanitization to low-brass/percussion, and tightened per-part grid normalization for woodwinds/percussion.
[2026-02-20 23:00] [Architect]: REVIEW NOTE: Objective XML checks improved for Alto/Clarinet/Snare (polyphony removed; bad-measure counts materially reduced). Tuba remains partially unstable and is flagged for next calibration pass.
[2026-02-20 23:00] [Developer]: ROUND READY: Prepared `datasets/Gemini/woodwinds_gemini_round4` from run `woodwinds_tune4_round4_rebuild2_20260220_230000` for screenshot review.
[2026-02-20 23:15] [Developer]: IMPL DONE (Round 5 pass): Added post-transposition written-range clamp for clarinet/sax, stricter monophonic timeline rebuild, shared highestTime padding before full-score measure alignment, and moved disclaimer injection to score-level only.
[2026-02-20 23:16] [Architect]: REVIEW NOTE: Objective XML checks show major stability gain vs Round 4: full-score bad-measure counts dropped to zero across all parts; Alto written ceiling reduced from 90 to 79; watermark text-per-part removed.
[2026-02-20 23:16] [Developer]: ROUND READY: Prepared `datasets/Gemini/woodwinds_gemini_round5` from run `woodwinds_tune5_rebuild_20260220_231500` for screenshot review.
[2026-02-20 23:30] [Developer]: IMPL DONE (Round 6 polish): Added final engraving polish pass (second score-level makeNotation), hard-fixed snare pitch-line mapping to C5, and guarded woodwind key-signature insertion when accidental density is high.
[2026-02-20 23:31] [Architect]: REVIEW NOTE: Round 6 preserves Round 5 structural stability (zero bad-measure counts across full score parts) while adding snare visual flattening and woodwind key signatures.
[2026-02-20 23:31] [Developer]: ROUND READY: Prepared `datasets/Gemini/woodwinds_gemini_round6` from run `woodwinds_tune6_rebuild_20260220_233000` for screenshot review.
[2026-02-20 23:40] [Architect]: REVIEW PASS (Round 6): Gemini notes report PASS on Alto Sax, Bb Clarinet, and Full Score; notation output accepted for current calibration target.
[2026-02-20 23:41] [Architect]: BACKLOG UPDATE: Added deferred feature item for output playback player (MIDI-first with mute/solo + tempo controls) to docs/post-mvp-backlog.md.
[2026-02-20 23:55] [Architect]: DOCS UPDATED: Added current-state and main-focus addenda to `docs/plan.md`, refreshed `docs/ARCHITECTURE.md`, and expanded `docs/tuning-lab-strategy-2026-02-20.md` for musicality-phase calibration.
[2026-02-20 23:55] [Architect]: BRANCH CREATED: `feature/musicality-phase` is now the working branch for rhythm/key/phrasing musicality strategy and implementation.
