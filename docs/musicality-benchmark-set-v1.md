# Musicality Benchmark Set v1

## Purpose
Use a fixed, representative benchmark set for Musicality Lab tuning rounds so score changes are comparable over time.

## Benchmark Songs (Phase 42 Baseline)
1. **Laufey - From The Start**  
   URL: `https://www.youtube.com/watch?v=lSD_L-xic9o`  
   Role: swing/groove + key ambiguity stress test

2. **Bruno Mars - Just The Way You Are**  
   URL: `https://www.youtube.com/watch?v=u7XjPmN-tHw`  
   Role: mainstream pop melodic baseline

3. **WALK THE MOON - Shut Up and Dance**  
   URL: `https://www.youtube.com/watch?v=nbcCG7PkI18`  
   Role: upbeat/dense rhythm stress test

4. **The White Stripes - Seven Nation Army**  
   URL: `https://www.youtube.com/watch?v=0J2QdDbelmY`  
   Role: simple riff/control anchor

5. **Journey - Any Way You Want It**  
   URL: `https://www.youtube.com/watch?v=kLDVTfQGDe4`  
   Role: classic rock complexity stress test

6. **Bill Withers - Lean on Me**  
   URL: `https://www.youtube.com/watch?v=fOZ-MySzAac`  
   Role: easy/clean control track

## Usage Rules
1. Keep this set fixed while tuning one metric family.
2. Use consistent assignment strategy per song across variants.
3. Capture run IDs for each variant and score via `scripts/musicality_eval_batch.py`.
4. Promote parameter changes only after:
   - hard-gate pass remains stable
   - auto-score improves
   - human A/B confirms improvement

## Tracking Template
For each song, store:
- baseline run id
- candidate run ids
- top-ranked variant
- A/B winner
- promotion decision
