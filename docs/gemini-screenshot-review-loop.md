# Gemini Screenshot Review Loop

## Goal
Use Gemini as a fast interim notation-quality screener between student test windows.
This does not replace Tuning Lab human ratings.

## Workflow
1. Generate PDFs from selected run(s).
2. Stage a Gemini pack:
```bash
./venv/bin/python scripts/prepare_gemini_review_pack.py \
  --round-id <round_id> \
  --run-id <run_id_1> \
  --run-id <run_id_2> \
  --include-full-score
```
3. Open `datasets/Gemini/<round_id>/artifacts/` PDFs and take screenshots.
4. Send screenshots to Gemini with prompt:
   - `datasets/Gemini/<round_id>/gemini_prompt.md`
5. Share Gemini ratings back here.
6. Tune parameters and regenerate.

## Notes
- Gemini is a screening tool, not final acceptance.
- Final quality gate remains real player feedback (your kids + teacher context).
- If Gemini feedback conflicts with parsed MusicXML metrics, prefer MusicXML as source of truth.
