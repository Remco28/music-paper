# Tuning Lab Strategy (2026-02-20)

## Purpose
Create a separate local app for calibration experiments so we can improve simplification and musicality quality (especially Beginner and Easy Intermediate) without adding complexity to the teacher-facing production app.

## Scope Boundary
- Production app stays focused on reliable score generation for classroom use.
- Tuning Lab app is only for generating controlled experiment batches, collecting ratings, and guiding parameter updates.
- No authentication for MVP calibration workflow (trusted local usage).

## Core Loop (Round-Based)
1. Prepare a song set for the round (small, representative).
2. Generate a fixed batch of variants from parameter presets/ranges.
3. Export PDFs and write a round manifest with exact parameters.
4. Reviewers rate samples in a short rubric form.
5. Aggregate scores and rank parameter sets.
6. Update defaults/candidate ranges and run next round.

## Musicality Calibration Focus (Current)
- Move beyond structural correctness into playable musical feel.
- Evaluate and tune:
  - rhythmic smoothing behavior
  - key-signature policy (`auto` vs simplified/manual)
  - swing/groove readability strategy
  - phrasing/breath friendliness for wind parts
- Keep objective integrity checks (measure math, monophony, range) as non-regression gates.

## Success Criteria
- We can identify a clearly better parameter profile for:
  - `Beginner`
  - `Easy Intermediate`
- Improvement is based on repeated human ratings, not one-off impressions.
- Every decision is traceable to a manifested round and score summary.
- Student reviewers describe outputs as musically playable, not only visually valid.

## Data Contract
- Round folder: `datasets/tuning_rounds/<round_id>/`
- Required files:
  - `round_manifest.json` (sample id, source song, profile, params)
  - `ratings.csv` (reviewer scores per sample)
  - `summary.json` (aggregated results, selected next candidates)
  - `exports/` (generated PDFs)

## Reviewer Rubric (Kid-Friendly, Short)
- `playable` (`yes/no`)
- `difficulty_fit` (`too_easy/right/too_hard`)
- `readability` (`1-5`)
- `melody_match` (`1-5`)
- `accidentals_confusing` (`yes/no`)
- `comment` (optional)

## Guardrails
- Randomized sample order to reduce bias.
- Hide parameter details from reviewers during rating.
- Require minimum labels per sample before using it for tuning decisions.
- Keep production defaults unchanged until round evidence is accepted.

## What This Enables Later
- Automated threshold calibration from labeled data.
- Support-line generation only when readability/playability gates fail.
- Profile-specific objective tuning by grade level.

## Resume Checklist (When Returning Later)
1. Open this file and `comms/tasks/2026-02-20-phase-39-tuning-lab-mvp-spec.md`.
2. Check latest labeling artifacts in `datasets/labeling/`.
3. Confirm unresolved TODOs in `docs/post-mvp-backlog.md`.
4. Start implementation/review from Phase 39 acceptance criteria.

## Related Docs
- Evaluation coverage matrix: `docs/tuning-lab-evaluation-matrix.md`
