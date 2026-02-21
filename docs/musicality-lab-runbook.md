# Musicality Lab Runbook

## Goal
Run fast automated ranking of candidate variants, then capture lightweight A/B votes on top candidates.
Preferred workflow is now UI-first (minimal CLI).

## 1) Generate Candidate Runs
Use the production app as usual to generate multiple run variants for the same song.

Benchmark source-of-truth:
- `docs/musicality-benchmark-set-v1.md`
- `docs/templates/phase42_benchmark_set_v1.template.json`

Recommendation:
- keep assignment map fixed
- vary one parameter family at a time
- generate at least 5 variants per round

## 2) Launch Musicality Lab (UI)

```bash
./venv/bin/streamlit run apps/musicality_lab.py
```

In the UI:
1. Choose benchmark song and baseline/candidate runs.
2. Click **Create + Score Round** (writes round artifacts automatically).
3. Inspect ranking table + top candidate.
4. Use A/B queue to record votes.
5. Click **Write Decision Summary**.

Round artifacts are stored in `datasets/musicality_rounds/<round_id>/`:
- `round_manifest.json`
- `auto_scores.json`
- `summary.json`
- `ab_votes.csv`
- `decision_summary.json` (after UI decision export)

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
- CLI fallback remains available for scripting:
```bash
./venv/bin/python scripts/musicality_eval_batch.py --round-id <round> --run-id <id> --run-id <id> ...
```
