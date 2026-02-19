# Task Spec: BTT Phase 4 - Regression Safety and Teacher Operations

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Harden day-to-day usability and reduce regression risk with lightweight diagnostics and repeatable smoke checks, while preserving the current MVP simplicity.

## Rationale
Core local pipeline is functional. The highest leverage next step is operational reliability: clear diagnostics, reproducible run records, and a fast way to validate that key pipeline paths still work after changes.

## User Stories
1. As a teacher, I can quickly see what failed and what to fix without reading stack traces.
2. As a maintainer, I can run a short smoke check and detect regressions before handing builds to the teacher.
3. As a maintainer, I can trace each artifact back to exact options and runtime context.

## In Scope
- Add a simple in-app diagnostics panel for environment/tool visibility.
- Add a scripted smoke-test path for local validation (non-UI).
- Strengthen manifest traceability fields and schema docs.
- Add short maintainer runbook for release checks.

## Out of Scope
- Authentication, multi-user roles, cloud sync.
- New ML models or arrangement intelligence.
- Major UI redesign.

## Required File Changes
- `app.py`
- `utils.py`
- `scripts/` (new smoke-check script)
- `docs/` (manifest schema + release checklist)
- `README_for_teacher.md`

## Required Functional Changes
1. **Diagnostics Panel (UI)**
   - Display current Python version, detected tool availability, and key executable paths.
   - Show latest run ID and latest output ZIP path if available.
   - Keep read-only and simple.

2. **Smoke Test Script**
   - Add `scripts/smoke_test.py` that performs minimal non-interactive checks:
     - imports core modules
     - runs manifest write/read sanity check
     - validates config invariants (profile keys, ranges)
   - Exit non-zero on failure.

3. **Manifest Traceability**
   - Ensure manifest schema remains stable and documented:
     - `run_id`, `timestamp`, `input`, `options`, `pipeline`, `assignments`, `parts`, `tool_versions`
   - Add `docs/manifest-schema.md` with field definitions and examples.

4. **Release Checklist**
   - Add `docs/release-checklist.md` with concise pass criteria:
     - preflight pass
     - one local-file run success
     - one YouTube single-video run success
     - ZIP contains expected artifacts and manifest fields

## Constraints
- Preserve current teacher workflow and no-auth policy.
- No new heavy dependencies.
- Keep implementation local-first and Windows-friendly.

## Acceptance Criteria
1. Diagnostics panel renders and does not block pipeline flow.
2. `scripts/smoke_test.py` runs in venv and returns success on healthy setup.
3. Manifest schema doc exists and matches runtime output fields.
4. Release checklist exists and is actionable in under 10 minutes.
5. Existing pipeline behavior remains intact.

## Review Notes for Developer
- Prefer additive, low-risk changes.
- Keep diagnostics text concise and teacher-readable.
- Avoid coupling smoke checks to external network calls.
