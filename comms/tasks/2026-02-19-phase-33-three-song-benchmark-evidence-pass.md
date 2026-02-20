# Task Spec: BTT Phase 33 - Three-Song Benchmark Evidence Pass

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Run and document a structured three-song benchmark pass to establish MVP quality evidence before freeze.

## Rationale
Recent phases hardened reliability and traceability. We now need objective end-to-end benchmark evidence against teacher-approved songs before final release decisions.

## User Stories
1. As a teacher, I can see clear evidence that representative songs produce usable outputs.
2. As a maintainer, I can trace benchmark outcomes to run IDs/manifests.
3. As a reviewer, I can make go/no-go decisions from a standardized rubric.

## In Scope
- Define benchmark protocol for 3 teacher-approved songs.
- Define per-song evidence fields and pass/fail rubric.
- Tie benchmark completion into release checklist gating.

## Out of Scope
- New pipeline features.
- Automated audio quality scoring.
- Changes to app runtime behavior.

## Required File Changes
- `docs/benchmark-3-song-pass.md` (new)
- `docs/release-checklist.md`
- `README_for_teacher.md` (benchmark reference link)

## Required Functional Changes
1. Add a benchmark worksheet/protocol with per-song capture fields:
   - source type and song identifier
   - run ID and ZIP filename
   - chosen profile/settings
   - warning summary
   - teacher usability verdict and notes
2. Add explicit benchmark pass criteria:
   - 3/3 runs complete
   - no unresolved blocker warnings/errors
   - teacher usability baseline met
3. Add release-checklist references to benchmark evidence doc.

## Constraints
- No new dependencies.
- Documentation-only phase; no app logic changes.

## Acceptance Criteria
1. Benchmark protocol doc exists and is actionable.
2. Release checklist includes benchmark evidence gate.
3. Teacher README links to benchmark protocol/results doc.
