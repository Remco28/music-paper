# Project Health Review - 2026-02-19

## Scope
Architectural and implementation health review after Phase 24, before continuing feature phases.

## Summary
The project is functionally healthy and shippable for ongoing local use, with no unresolvable blockers found. However, four cross-cutting risks should be addressed before final-phase completion to reduce regressions and support burden.

## Findings

### 1) Diagnostics performance overhead (High)
- `app.py` currently calls tool version/path probes during render of `Diagnostics`.
- These probes use subprocess calls and can be expensive across reruns.
- Risk: UI sluggishness and perceived instability as the app grows.

### 2) URL-validation rule drift across layers (Medium)
- Input validation in `app.py` and source classification in `pipeline.py` are not fully aligned.
- Risk: inconsistent behavior and edge-case misclassification.

### 3) Global PDF output collision risk (Medium)
- Rendered PDFs currently land in shared `OUTPUT_DIR` with name-based paths.
- Risk: artifact overwrites across runs and weaker reproducibility/isolation.

### 4) Insufficient behavior-level test coverage (Medium)
- Smoke checks validate imports/invariants/basic manifest helpers, but not many newer safety/ops behaviors.
- Risk: regressions in UI logic and guardrails going undetected.

## Recommended Stabilization Sequence
1. Diagnostics probe caching/deferred execution.
2. Centralized URL validation helper shared by app + pipeline.
3. Run-scoped PDF artifact naming/isolation hardening.
4. Expanded smoke checks for critical guardrails and status flows.

## Exit Criteria
- Diagnostics no longer triggers heavy probes on every rerun.
- URL validation behavior is consistent between input gate and pipeline handling.
- PDF collisions across runs are prevented by contract.
- Smoke suite covers key safety and status semantics introduced in recent phases.
