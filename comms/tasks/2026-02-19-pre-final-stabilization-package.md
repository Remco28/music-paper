# Task Spec: Pre-Final Stabilization Package (Before Remaining Feature Phases)

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Execute a focused stabilization package that resolves identified cross-cutting risks before continuing remaining feature phases.

## Rationale
Recent work added strong capability breadth. Before final phases, we should remove avoidable reliability/performance risks that could multiply future rework and regressions.

## Evidence
- `docs/health-review-2026-02-19.md`

## Workstreams (in order)

1. **STAB-1 Diagnostics Probe Performance Hardening**
   - Defer or cache expensive version/path probe operations.
   - Ensure Diagnostics panel remains informative without rerun-heavy subprocess churn.

2. **STAB-2 URL Validation Unification**
   - Introduce one canonical URL validation/classification helper.
   - Consume the same rules in both input gate (`app.py`) and pipeline source handling (`pipeline.py`).

3. **STAB-3 PDF Artifact Isolation Hardening**
   - Eliminate cross-run PDF collision risk (run-scoped pathing and/or run-ID-safe naming).
   - Preserve export download ergonomics and manifest traceability.

4. **STAB-4 Smoke Coverage Expansion**
   - Add targeted smoke coverage for recently added operational safeguards:
     - status derivation (`success/failed/unknown`)
     - assignment guard baseline behavior
     - validation helper behaviors where testable without external tools

## Constraints
- No new dependencies.
- Preserve local-only workflow and existing user-facing capabilities.
- Keep additive changes backward-compatible with legacy manifests.

## Acceptance Criteria
1. All four workstreams are implemented and validated.
2. `py_compile` and smoke checks pass after stabilization changes.
3. No functional regression in export/history/diagnostics/reset flows.
4. Remaining feature phases resume on a cleaner baseline.

## Notes on Phase Sequencing
- Existing `Phase 25` feature spec is **temporarily deferred** until this stabilization package is complete.
- After stabilization pass, Phase 25+ resumes with lower regression risk.
