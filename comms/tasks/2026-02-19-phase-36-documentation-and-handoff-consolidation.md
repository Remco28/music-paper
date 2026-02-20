# Task Spec: BTT Phase 36 - Documentation and Handoff Consolidation

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Consolidate teacher and maintainer documentation so it matches current MVP behavior and provides a single handoff path to benchmark/release decisions.

## Rationale
After multiple reliability/UX phases, documentation drift can create operator confusion even when code is stable.

## User Stories
1. As a teacher, I can follow one clear path from setup to benchmark run.
2. As a maintainer, docs reflect current UI labels and manifest behavior.
3. As a reviewer, architecture/checklist/docs references are coherent and up to date.

## In Scope
- Sync teacher README wording with current app labels/workflow.
- Update release checklist for current manifest outcome fields.
- Refresh architecture doc references and storage/runtime notes.
- Add concise handoff sequence in docs.

## Out of Scope
- Runtime code changes.
- New product features.

## Required File Changes
- `README_for_teacher.md`
- `docs/ARCHITECTURE.md`
- `docs/release-checklist.md`
- `docs/run-history.md`

## Acceptance Criteria
1. Key docs are aligned with current behavior through Phase 35.
2. Handoff sequence from setup -> validation -> benchmark -> release is explicit.
3. Existing validations pass.
