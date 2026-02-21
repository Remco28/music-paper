# Task Spec: Phase 41 - Musicality Lab v1 Foundation

## Objective
Establish a first implementation slice for automated musicality tuning so iteration speed does not depend on continuous human review.

## Rationale (First Principles)
The pipeline is now structurally stable (bar math, monophony, range, export integrity). Remaining quality gaps are musical interpretation gaps.  
From first principles:
1. Expressive performance data includes micro-variation that should not always be preserved in classroom notation.
2. We need repeatable measurement to optimize interpretation behavior.
3. Human review is authoritative but scarce, so automation must pre-rank candidates before A/B review.

Therefore the simplest path is to build a minimal end-to-end loop:
- generate candidate variants
- compute automatic musicality scores
- rank and surface top candidates
- collect lightweight human A/B on finalists

## User Stories
1. As a maintainer, I can run one command to evaluate multiple parameter variants for a song and receive ranked results.
2. As a maintainer, I can inspect objective scoring breakdowns (timing, pitch, rhythm, penalties) per variant.
3. As a reviewer, I can open a small web UI that plays/compares top-ranked candidates and records A/B votes.
4. As an architect, I can trace every decision back to manifests and score artifacts.

## Scope
### In Scope (v1)
- Auto-scoring module for transcription feasibility + musicality proxies.
- Batch evaluation runner for variant sets.
- Minimal web UI to review top-N candidates with A/B voting.
- Persisted artifacts + schema for reproducibility.

### Out of Scope (v1)
- Full articulation inference.
- Genre-wide perfect key inference.
- Replacing Tuning Lab; this is a companion loop.

## Files / Functions to Add or Modify

### New
1. `scripts/musicality_eval_batch.py`
- CLI runner for:
  - selecting input/run source
  - applying parameter variants
  - producing ranked `summary.json`

2. `scripts/musicality_score.py`
- Core scoring utilities:
  - onset alignment
  - pitch contour similarity
  - rhythm consistency
  - fragmentation/overlap penalties

3. `apps/musicality_lab.py`
- Streamlit front-end for:
  - viewing ranked candidates
  - previewing PDFs/audio
  - recording A/B decisions

4. `docs/musicality-lab-runbook.md`
- Step-by-step local workflow and interpretation guide.

### Modify
1. `pipeline.py`
- Expose a reusable programmatic path for evaluating parameter variants without UI coupling.
- Ensure run manifests include variant identifiers used by the new scorer.

2. `project-manifest.md`
- Add pointers to new Musicality Lab entrypoints/docs.

## Data Contract (v1)
Directory: `datasets/musicality_rounds/<round_id>/`
- `round_manifest.json` (input, variants, run ids)
- `auto_scores.json` (per variant metric breakdown + aggregate rank)
- `ab_votes.csv` (human pairwise selections)
- `summary.json` (recommended winner + confidence notes)

## Scoring Model (v1)
Composite rank score (initial):
`score = 0.40*onset + 0.30*pitch + 0.20*rhythm - 0.10*fragmentation_penalty`

Hard-gate check must remain pass/fail and blocks promotion.

## Acceptance Criteria
1. Batch runner can evaluate >= 5 variants in one run and produce deterministic ranked output.
2. Score output includes metric components, not only final aggregate.
3. Musicality Lab UI can load ranked variants and capture A/B votes to CSV.
4. All artifacts are round-scoped and reproducible from manifest data.
5. Existing teacher-facing export flow remains unchanged.

## Validation Plan
1. Unit-level sanity checks for metric functions (on synthetic MIDI/audio fixtures).
2. Dry-run on one existing benchmark song with >= 5 variants.
3. Confirm top-3 shortlist is generated and reviewable in UI.
4. Confirm A/B votes persist and tie back to candidate IDs in summary.

## Risks / Mitigations
1. Risk: Metric gaming (high score but musically poor).
- Mitigation: keep mandatory human A/B acceptance before promoting defaults.

2. Risk: Runtime cost with many variants.
- Mitigation: cache intermediate artifacts and score only changed variant stages.

3. Risk: Overfitting to one song.
- Mitigation: benchmark set must contain multiple representative songs.

## Deliverable Marker
When implemented, append `SPEC READY` and `IMPL/REVIEW` entries to `comms/log.md` per workflow protocol.
