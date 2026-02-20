# Tuning Lab Guide

## Purpose
Run calibration rounds in a separate app so students can rate generated PDFs and we can tune parameters with evidence.
Tuning Lab is the primary human-evaluation workflow.

## 1) Create a Round
Use existing successful runs to generate a round manifest:

```bash
./venv/bin/python scripts/generate_tuning_batch.py \
  --run-id cheers_phase40_20260220_013515_beginner_rerun_20260220_014050 \
  --run-id cheers_phase40_20260220_013515_easy-intermediate_rerun_20260220_014050 \
  --round-id cheers_phase40_round1
```

Output:
- `datasets/tuning_rounds/<round_id>/round_manifest.json`

### Woodwinds Focus Example (Clarinet/Sax only)
If you want students to review only clarinet/sax outputs:

```bash
./venv/bin/python scripts/generate_tuning_batch.py \
  --round-id woodwinds_round1 \
  --limit-runs 80 \
  --include-part-keyword clarinet \
  --include-part-keyword sax \
  --allowed-profile Beginner \
  --allowed-profile "Easy Intermediate"
```

## 2) Launch Tuning Lab App

```bash
./venv/bin/streamlit run apps/tuning_lab.py
```

Student flow in app:
1. Start Round (choose round + reviewer name)
2. Review Samples (PDF + quick rubric)
3. Submit and Finish

Notes:
- Responses auto-save to `datasets/tuning_rounds/<round_id>/ratings.csv`.
- Students can stop and resume later using the same reviewer name.

## 3) Score the Round

```bash
./venv/bin/python scripts/score_tuning_round.py \
  --round-dir datasets/tuning_rounds/cheers_phase40_round1
```

Output:
- `datasets/tuning_rounds/<round_id>/summary.json`

## Recommended Workflow
1. Use the production app to generate candidate runs.
2. Build a round with `scripts/generate_tuning_batch.py`.
3. Collect student ratings in Tuning Lab (`apps/tuning_lab.py`).
4. Aggregate with `scripts/score_tuning_round.py`.
5. Use Gemini screenshot review only as a fast interim screener between student sessions.

## Round Folder Contract
- `round_manifest.json` - sample list + parameter payload
- `ratings.csv` - all reviewer responses
- `summary.json` - aggregated ranking and parameter impact (after scoring)
