# Musicality Lab Strategy (2026-02-21)

## Purpose
Build a repeatable tuning system that improves musical quality of generated scores without regressing structural correctness.

This strategy is separate from core pipeline integrity work. Integrity remains mandatory; musicality becomes the primary optimization target.

## First-Principles Framing
1. The system converts expressive human performance into symbolic notation.
2. Literal extraction is not the same as playable, musical notation.
3. Therefore we need a post-transcription interpretation layer that trades micro-accuracy for musical usefulness.
4. "Correctness" has two categories:
   - Non-negotiable structural correctness (objective)
   - Musical plausibility/readability (partly subjective)

## Objective vs Subjective Boundaries
### Hard Gates (must pass)
- Measure math integrity per part
- Instrument monophony/range validity
- Correct transposition semantics
- Export/package metadata consistency

### Musicality Targets (optimize)
- Rhythmic naturalness (not over-fragmented)
- Key readability burden (accidental load)
- Phrase continuity/breath-friendly contour
- Groove representation (for swung material)

## Validation Architecture
Three-tier loop to reduce human bottleneck:

1. Tier A: Automatic scoring (fast, every run)
- Compare generated symbolic/audio output against reference stems/audio
- Rank candidate parameter sets
- Reject candidates that fail hard gates

2. Tier B: AI screenshot screening (fast interim triage)
- Gemini reviews top-ranked candidates only
- Used as a quick diagnostic lens, not source of truth

3. Tier C: Human A/B acceptance (authoritative)
- Students/teacher compare top candidates vs baseline
- Decide promotion to default profiles

## Recommended Auto-Scoring Signals (v1)
- Onset alignment score
- Pitch contour similarity score
- Rhythm pattern consistency score
- Over-fragmentation penalty
- Overlap/chord-noise penalty for monophonic targets

Composite score example:
`rank_score = 0.40*onset + 0.30*pitch + 0.20*rhythm - 0.10*fragmentation_penalty`

## Parameter Families to Tune
1. Rhythm smoothing aggressiveness
2. Tie/fragment merge policy
3. Key policy (`auto`, `simplified`, `manual override`)
4. Swing notation toggle/annotation behavior
5. Phrase-gap heuristics (breath-friendly splitting)

## Experiment Protocol
1. Fix benchmark song set (representative and stable)
2. Freeze baseline parameter bundle
3. Change one parameter family per round
4. Run full automatic scoring
5. Send top-N candidates to A/B human review
6. Promote only if:
   - hard gates remain green
   - auto-score improves beyond threshold
   - human A/B favors candidate over baseline

## Initial Success Criteria (v1)
- 100% hard-gate pass rate on benchmark set
- >= 8% median auto-score improvement vs baseline
- >= 70% A/B preference for candidate among human reviewers

## Non-Goals (v1)
- Perfect transcription of all genres
- Full expressive articulation inference
- Cloud-model dependence or paid APIs

## Immediate Next Deliverables
1. Musicality Lab v1 spec (automation + UI loop)
2. Auto-scoring module specification and schema
3. Minimal web front-end flow for tune -> score -> rank -> review
