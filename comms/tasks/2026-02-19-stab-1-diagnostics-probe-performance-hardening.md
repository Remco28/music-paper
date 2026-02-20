# Task Spec: STAB-1 Diagnostics Probe Performance Hardening

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Reduce rerun-time overhead from diagnostics tool probing.

## Required File Changes
- `app.py`
- `utils.py` (if helper extraction needed)

## Required Changes
1. Avoid running heavy subprocess probes on every rerender.
2. Use explicit refresh action and/or session-cache timestamp for diagnostics probe data.
3. Keep displayed diagnostics behavior equivalent for users.

## Acceptance
- Diagnostics remains usable and accurate.
- UI rerenders are lighter when diagnostics is unchanged.
- Existing checks pass.
