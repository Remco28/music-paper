# Phase 39 Spec: Tuning Lab MVP (Parameter Calibration App)

## Objective
Implement a separate local Streamlit app to run controlled simplification experiments, collect reviewer ratings, and produce ranked recommendations for `Beginner` and `Easy Intermediate` parameter tuning.

## Why Now
Recent classroom feedback confirms score readability/playability gaps remain for melodic parts. We need a repeatable calibration loop with evidence instead of ad-hoc tuning.

## In Scope
- New app entrypoint: `apps/tuning_lab.py`.
- Batch generation command/script for predefined parameter variants.
- Embedded PDF review workflow in the Tuning Lab UI.
- Structured survey capture to CSV per round.
- Round summary scoring script/report.

## Out of Scope
- Any teacher-facing production UX changes.
- Authentication.
- Long-term retention policy implementation (tracked TODO).
- Model retraining or replacement of Demucs/Basic Pitch.

## Deliverables
1. `apps/tuning_lab.py`
2. `scripts/generate_tuning_batch.py`
3. `scripts/score_tuning_round.py`
4. `docs/tuning-lab.md` (how to run rounds end-to-end)
5. Round folder structure under `datasets/tuning_rounds/`

## Functional Requirements
- User can create a new round with:
  - selected source song(s)
  - target profiles (`Beginner`, `Easy Intermediate`)
  - number of variants per profile
- System generates variants and exports PDFs into round-scoped folder.
- UI presents one sample at a time with:
  - part/full-score PDF viewer
  - simple rating form
  - next/previous navigation
- Ratings persist incrementally (no data loss on refresh/restart).
- Summary script outputs:
  - ranked variants
  - per-profile recommended next candidates
  - confidence notes based on label count

## Student Self-Serve Requirements
- UI must be usable by middle-school reviewers without adult supervision.
- Home screen must have a 3-step flow:
  - `Start Round`
  - `Review Samples`
  - `Submit and Finish`
- Each screen must include plain-language instructions (no music theory jargon by default).
- Survey must use short labels and button-based choices; avoid free text as required input.
- The app must auto-save each response immediately.
- Progress indicator must show:
  - samples completed
  - samples remaining
  - estimated time left
- A reviewer can pause and resume without losing place.
- Include an in-app “What to listen/look for” help panel with examples.

## Data Requirements
- Round manifest must include:
  - `round_id`, timestamp, app version
  - sample ids, profile, parameter payload
  - file paths to exported PDFs
- Ratings CSV must include:
  - `round_id`, `sample_id`, `reviewer_id`, timestamp
  - rubric fields (`playable`, `difficulty_fit`, `readability`, `melody_match`, `accidentals_confusing`, `comment`)

## Tuning Coverage Requirements
- Round generation must support controlled parameter variation across these families:
  - Stem separation options (model choice, if changed)
  - Transcription thresholds (minimum note length, confidence/gate thresholds where available)
  - Simplification controls (quantization grid, short-note handling, merge policy, contour smoothing)
  - Pitch readability controls (accidental-density limits, leap caps, beginner playability gate)
  - Support-line options (enabled/disabled and strictness), when present
- Every sample in a round must store full parameter payload in manifest for traceability.
- Scoring output must include per-parameter impact summary so we can see what actually helped.

## Acceptance Criteria
1. End-to-end round can be run locally without touching production app flow.
2. At least one completed round produces a non-empty ranked summary.
3. All generated samples and ratings are traceable via `sample_id`.
4. No regressions in existing app compile/smoke checks.

## Validation Plan
- `python -m py_compile app.py pipeline.py config.py utils.py`
- Existing smoke test script.
- Manual Tuning Lab dry run on one song with 2-3 variants/profile.
- Verify reload persistence by restarting Streamlit and re-opening round.

## Risks / Mitigations
- Risk: Reviewer fatigue.
  - Mitigation: Keep survey short and cap samples per session.
- Risk: Noisy ratings from small sample size.
  - Mitigation: minimum labels-per-sample gate in summary.
- Risk: Mixing production and experiment outputs.
  - Mitigation: strict round-scoped directories under `datasets/tuning_rounds/`.

## Exit Condition
Phase 39 is complete when the team can run one full calibration round and produce a ranked recommendation report that is reproducible from saved artifacts.
