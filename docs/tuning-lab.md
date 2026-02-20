# Tuning Lab Guide

## Purpose
Run calibration rounds in a separate app so students can rate generated PDFs and we can tune parameters with evidence.

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

## Round Folder Contract
- `round_manifest.json` - sample list + parameter payload
- `ratings.csv` - all reviewer responses
- `summary.json` - aggregated ranking and parameter impact (after scoring)
