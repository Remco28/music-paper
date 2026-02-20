# Task Spec: STAB-2 URL Validation Unification

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Unify URL validation and source classification rules between app input and pipeline.

## Required File Changes
- `app.py`
- `pipeline.py`
- `config.py` (if helper constants need minor adjustment)

## Required Changes
1. Define one canonical validation/classification function path.
2. Reuse it for input gate and pipeline handling.
3. Maintain single-video YouTube constraint and host allowlist consistency.

## Acceptance
- App/pipeline decisions match for same URL inputs.
- No regression for valid single-video URLs.
- Existing checks pass.
