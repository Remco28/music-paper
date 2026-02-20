# Phase 40 Spec: Fit Gating and Success Optimization

## Objective
Raise real-world classroom success rate by adding song-fit guidance, automatic profile recommendation, and beginner-focused guardrails while keeping teacher UX simple.

## Scope
- Production app only (teacher-facing).
- Keep visible simplification choices limited to:
  - `Beginner`
  - `Easy Intermediate`
- Add pre-export song-fit analysis and recommendation.
- Add structured fallback path when parts are not beginner-playable.

## Functional Requirements
1. Song Fit Score
- Add pre-export fit scoring with labels:
  - `Good Fit`
  - `Borderline`
  - `Poor Fit`
- Fit score must be based on measurable signals (not manual opinion), such as:
  - note fragmentation / short-note rate
  - accidental density
  - large leap rate
  - empty/sparse part rate

2. Auto Profile Recommendation
- App should recommend `Beginner` or `Easy Intermediate` from fit signals.
- Recommendation is advisory by default (user can override).
- If `Poor Fit`, show explicit warning that beginner output may be unusable.

3. Two-Pass Export Option
- Optional export mode that runs:
  - pass A: `Beginner`
  - pass B: `Easy Intermediate`
- Output both sets with clear labeling so teacher can choose.

4. Beginner Safety Guardrails
- Keep/extend hard limits for beginner playability:
  - accidental density cap
  - large leap cap
  - fast-note rate cap
- If a part fails gate:
  - skip with clear reason, or
  - route to fallback support-line flow (if enabled in current build).

5. Instrument-Family Sensitivity
- Allow stricter beginner thresholds for melody instruments (e.g., flute/clarinet) than low brass/percussion.

## UX Requirements
- Keep settings minimal and non-technical.
- Expose “Why this recommendation?” with plain-language bullet points.
- Avoid surfacing advanced tuning controls in teacher app.

## Data / Traceability
- Manifest must record:
  - fit label + score
  - recommendation
  - gate trigger reasons per skipped part
- Run history should surface fit label and recommendation.

## Acceptance Criteria
1. Teacher app only shows `Beginner` and `Easy Intermediate`.
2. Fit label and recommendation appear before export.
3. At least one `Poor Fit` case shows warning and clear next action.
4. Manifest persists fit/recommendation metadata.
5. Existing compile/smoke checks pass.

## Risks / Mitigations
- Risk: False confidence from weak heuristic.
  - Mitigation: start conservative; show recommendation confidence and rationale.
- Risk: Over-filtering produces sparse parts.
  - Mitigation: two-pass mode and profile fallback guidance.

## Exit Condition
Phase 40 completes when teacher can reliably identify bad-fit songs before full export and pick between two beginner-safe output levels with clear guidance.
