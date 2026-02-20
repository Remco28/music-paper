# Playability Labeling (Student-Friendly)

Use this workflow to collect quick, consistent labels from students.

## Generate a Label Pack

From repo root:

```bash
./venv/bin/python scripts/prepare_labeling_pack.py --limit-runs 20
```

Outputs are written to `datasets/labeling/`:

- `playability_labels_latest.csv`
- `labeling_packet_latest.md`

Timestamped versions are also written each run.

## Student Instructions

Each row is one exported PDF part.

Fill these columns:

1. `student_name`
2. `playable_yes_no`:
   - `yes` = playable by a middle-schooler after light practice
   - `no` = unreadable/unplayable
3. `resembles_song_1_to_5`:
   - `1` not recognizable, `5` clearly resembles song
4. `difficulty_1_to_5`:
   - `1` very easy, `5` too hard for class
5. `confidence_1_to_5`:
   - `1` unsure, `5` very sure
6. `notes`:
   - short reason (for example: "too many accidentals")

## Quality Tips

- Keep each judgment fast (about 30 seconds).
- Use headphones if possible.
- Don’t overthink theory terms; practical usability is what matters.
