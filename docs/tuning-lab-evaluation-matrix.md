# Tuning Lab Evaluation Matrix

## Goal
Ensure each calibration round tests all meaningful tuning levers, not just rhythm simplification, so feedback can drive reliable improvements.

## Reviewer Track (Middle School Friendly)
- Reviewers only answer simple UX rubric questions in the Tuning Lab UI.
- They do not choose parameters.
- They should evaluate what they see/hear:
  - Is this playable?
  - Is this the right difficulty?
  - Does it look clean/readable?
  - Does it resemble the song melody?

## Engineer Track (Parameter Coverage)
For each round, vary only 1-2 parameter families at a time to keep results interpretable.

### Family A: Transcription Filtering
- `min_note_length`
- `onset/activation threshold` (if exposed in current pipeline wrapper)
- `note merge gap`
- Why it matters: reduces noisy ornament artifacts from vocals.

### Family B: Rhythm Simplification
- quantization grid
- tuplet removal policy
- short-note floor and merge policy
- Why it matters: directly impacts beginner readability.

### Family C: Pitch Readability
- accidental-density cap
- chromatic neighbor collapse strength
- large-leap cap/smoothing
- Why it matters: reduces “looks scary” notation.

### Family D: Beginner Safety Gate
- unplayable gate threshold(s)
- skip vs fallback strategy
- Why it matters: prevents impossible parts from being printed as beginner material.

### Family E: Optional Support Line
- support line enabled/disabled
- support line density/strictness
- Why it matters: gives playable fallback when lead line is too hard.

### Family F: Upstream Model Choice (Lower Frequency)
- demucs model variant
- transcription backend version/config
- Why it matters: can improve raw note quality, but expensive to sweep often.

## Minimum Round Design
- Profiles: `Beginner`, `Easy Intermediate`
- Songs: at least 2 contrasting songs
- Variants per profile: 4-8
- Labels per sample: minimum 3 reviewers

## Required Round Artifacts
- `round_manifest.json`: sample + full parameter payload
- `ratings.csv`: reviewer responses
- `summary.json`: ranked outputs + parameter impact notes

## Decision Rule Template
- Promote parameter set when:
  - `playable_yes_rate` increases
  - `difficulty_fit=right` increases
  - readability/melody scores do not regress
- Reject parameter set when:
  - accidental confusion rises materially
  - more samples are marked unplayable

## Notes
- Keep production defaults unchanged until one full round shows consistent gains.
- Avoid mixing too many parameter changes in one batch.
