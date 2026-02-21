# Musicality Lab Runbook

## Goal
Run fast automated ranking of candidate variants, then capture lightweight A/B votes on top candidates.

## 1) Generate Candidate Runs
Use the production app as usual to generate multiple run variants for the same song.

Recommendation:
- keep assignment map fixed
- vary one parameter family at a time
- generate at least 5 variants per round

## 2) Score a Musicality Round
Run:

```bash
./venv/bin/python scripts/musicality_eval_batch.py \
  --round-id mygirl_musicality_round1 \
  --run-id <run_id_1> \
  --run-id <run_id_2> \
  --run-id <run_id_3> \
  --run-id <run_id_4> \
  --run-id <run_id_5>
```

Outputs in `datasets/musicality_rounds/<round_id>/`:
- `round_manifest.json`
- `auto_scores.json`
- `summary.json`
- `ab_votes.csv`

## 3) Review in Musicality Lab UI
Run:

```bash
./venv/bin/streamlit run apps/musicality_lab.py
```

In the UI:
1. Select round
2. Inspect ranked candidates
3. Compare A/B top candidates
4. Record vote

## 4) Interpreting Scores
Composite score:

`0.40*onset + 0.30*pitch + 0.20*rhythm - 0.10*fragmentation_penalty`

Hard gate pass requires:
- strong measure integrity
- low chord density
- non-empty candidate content

Use score as pre-ranking only. Final promotion still requires human A/B preference.

## 5) Promotion Rule (Suggested)
Promote a candidate only when:
1. Hard-gate pass stays true
2. Auto-score improves over baseline
3. Human A/B votes prefer candidate over baseline

## 6) Notes
- This loop complements Tuning Lab; it does not replace it.
- If automatic score conflicts with human results, prefer human decision for default profile changes.
