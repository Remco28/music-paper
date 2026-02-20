from __future__ import annotations

import base64
import csv
import json
from datetime import datetime
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TUNING_ROOT = PROJECT_ROOT / "datasets" / "tuning_rounds"

RUBRIC_OPTIONS = {
    "playable": ("yes", "no"),
    "difficulty_fit": ("too_easy", "right", "too_hard"),
    "readability": ("1", "2", "3", "4", "5"),
    "melody_match": ("1", "2", "3", "4", "5"),
    "accidentals_confusing": ("yes", "no"),
}


def _round_dirs() -> list[Path]:
    if not TUNING_ROOT.exists():
        return []
    round_dirs = [p for p in TUNING_ROOT.iterdir() if p.is_dir() and (p / "round_manifest.json").exists()]
    round_dirs.sort(key=lambda p: p.name, reverse=True)
    return round_dirs


def _load_round_manifest(round_dir: Path) -> dict:
    return json.loads((round_dir / "round_manifest.json").read_text())


def _ratings_path(round_dir: Path) -> Path:
    return round_dir / "ratings.csv"


def _load_ratings_map(round_dir: Path, reviewer_id: str) -> dict[str, dict]:
    path = _ratings_path(round_dir)
    if not path.exists():
        return {}
    rows: dict[str, dict] = {}
    with path.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if str(row.get("reviewer_id", "")).strip() != reviewer_id:
                continue
            sample_id = str(row.get("sample_id", "")).strip()
            if sample_id:
                rows[sample_id] = row
    return rows


def _upsert_rating(round_dir: Path, rating_row: dict) -> None:
    path = _ratings_path(round_dir)
    existing: list[dict] = []
    fieldnames = [
        "round_id",
        "sample_id",
        "reviewer_id",
        "timestamp",
        "playable",
        "difficulty_fit",
        "readability",
        "melody_match",
        "accidentals_confusing",
        "comment",
    ]
    if path.exists():
        with path.open() as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                existing.append({key: row.get(key, "") for key in fieldnames})

    replaced = False
    for idx, row in enumerate(existing):
        if (
            row.get("round_id") == rating_row["round_id"]
            and row.get("sample_id") == rating_row["sample_id"]
            and row.get("reviewer_id") == rating_row["reviewer_id"]
        ):
            existing[idx] = rating_row
            replaced = True
            break
    if not replaced:
        existing.append(rating_row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in existing:
            writer.writerow(row)


def _embed_pdf(pdf_path: Path) -> None:
    if not pdf_path.exists():
        st.error(f"PDF missing: {pdf_path}")
        return
    b64 = base64.b64encode(pdf_path.read_bytes()).decode("utf-8")
    src = f"data:application/pdf;base64,{b64}"
    st.markdown(
        (
            f'<iframe src="{src}" width="100%" height="720" '
            'style="border:1px solid #ccc; border-radius:8px;"></iframe>'
        ),
        unsafe_allow_html=True,
    )


def _is_complete(row: dict) -> bool:
    return all(
        str(row.get(key, "")).strip()
        for key in ("playable", "difficulty_fit", "readability", "melody_match", "accidentals_confusing")
    )


def _estimate_remaining_minutes(remaining_samples: int) -> int:
    # ~35s/sample in practice for this rubric
    return max(1, int(round((remaining_samples * 35) / 60.0)))


def main() -> None:
    st.set_page_config(page_title="Tuning Lab", layout="wide")
    st.title("Tuning Lab")
    st.caption("Calibration review app for Beginner and Easy Intermediate tuning rounds.")

    st.markdown("### 1) Start Round")
    round_dirs = _round_dirs()
    if not round_dirs:
        st.error("No tuning rounds found in `datasets/tuning_rounds/`.")
        st.info("Run `python scripts/generate_tuning_batch.py` first.")
        return

    round_options = {d.name: d for d in round_dirs}
    selected_round_name = st.selectbox("Select round", options=list(round_options.keys()))
    round_dir = round_options[selected_round_name]
    manifest = _load_round_manifest(round_dir)
    samples = list(manifest.get("samples") or [])
    round_id = str(manifest.get("round_id") or round_dir.name)
    if not samples:
        st.error("Round has no samples.")
        return

    reviewer_id = st.text_input("Reviewer name or ID", value=st.session_state.get("tl_reviewer_id", ""))
    if reviewer_id:
        st.session_state.tl_reviewer_id = reviewer_id.strip()
    reviewer_id = st.session_state.get("tl_reviewer_id", "").strip()
    if not reviewer_id:
        st.warning("Enter reviewer name/ID to begin.")
        return

    ratings_map = _load_ratings_map(round_dir, reviewer_id)
    completed = sum(1 for s in samples if _is_complete(ratings_map.get(str(s.get("sample_id", "")), {})))
    remaining = max(len(samples) - completed, 0)

    st.markdown("### 2) Review Samples")
    st.caption(
        f"Progress: {completed}/{len(samples)} complete | "
        f"{remaining} remaining | about {_estimate_remaining_minutes(remaining)} minute(s) left"
    )
    with st.expander("What to look for", expanded=False):
        st.markdown("- `Playable`: can a middle-school player perform this after light practice?")
        st.markdown("- `Difficulty Fit`: too easy, right, or too hard for class level.")
        st.markdown("- `Readability`: how clear and clean the notation looks.")
        st.markdown("- `Melody Match`: how much it resembles the song.")
        st.markdown("- `Accidentals Confusing`: too many sharps/flats for students.")

    sample_ids = [str(s.get("sample_id", "")) for s in samples]
    if "tl_sample_id" not in st.session_state or st.session_state.tl_sample_id not in sample_ids:
        first_incomplete = next((sid for sid in sample_ids if not _is_complete(ratings_map.get(sid, {}))), sample_ids[0])
        st.session_state.tl_sample_id = first_incomplete

    current_sample_id = st.selectbox("Sample", options=sample_ids, key="tl_sample_id")
    sample = next(s for s in samples if str(s.get("sample_id", "")) == current_sample_id)

    left, right = st.columns([2, 1])
    with right:
        st.markdown(f"- Round: `{round_id}`")
        st.markdown(f"- Profile: `{sample.get('profile', '')}`")
        st.markdown(f"- Part: `{sample.get('part_name', '')}`")
        st.markdown(f"- Run: `{sample.get('run_id', '')}`")

    with left:
        pdf_path = Path(str(sample.get("pdf_path", "")))
        _embed_pdf(pdf_path)

    existing = ratings_map.get(current_sample_id, {})

    w1, w2, w3 = st.columns(3)
    with w1:
        playable = st.radio(
            "Playable?",
            RUBRIC_OPTIONS["playable"],
            index=RUBRIC_OPTIONS["playable"].index(existing.get("playable", "yes"))
            if existing.get("playable", "") in RUBRIC_OPTIONS["playable"] else None,
            key=f"tl_playable_{current_sample_id}",
        )
    with w2:
        difficulty_fit = st.radio(
            "Difficulty Fit",
            RUBRIC_OPTIONS["difficulty_fit"],
            index=RUBRIC_OPTIONS["difficulty_fit"].index(existing.get("difficulty_fit", "right"))
            if existing.get("difficulty_fit", "") in RUBRIC_OPTIONS["difficulty_fit"] else None,
            key=f"tl_difficulty_{current_sample_id}",
        )
    with w3:
        accidentals_confusing = st.radio(
            "Accidentals Confusing?",
            RUBRIC_OPTIONS["accidentals_confusing"],
            index=RUBRIC_OPTIONS["accidentals_confusing"].index(existing.get("accidentals_confusing", "no"))
            if existing.get("accidentals_confusing", "") in RUBRIC_OPTIONS["accidentals_confusing"] else None,
            key=f"tl_accidentals_{current_sample_id}",
        )

    x1, x2 = st.columns(2)
    with x1:
        readability = st.radio(
            "Readability (1-5)",
            RUBRIC_OPTIONS["readability"],
            horizontal=True,
            index=RUBRIC_OPTIONS["readability"].index(existing.get("readability", "3"))
            if existing.get("readability", "") in RUBRIC_OPTIONS["readability"] else None,
            key=f"tl_readability_{current_sample_id}",
        )
    with x2:
        melody_match = st.radio(
            "Melody Match (1-5)",
            RUBRIC_OPTIONS["melody_match"],
            horizontal=True,
            index=RUBRIC_OPTIONS["melody_match"].index(existing.get("melody_match", "3"))
            if existing.get("melody_match", "") in RUBRIC_OPTIONS["melody_match"] else None,
            key=f"tl_melody_{current_sample_id}",
        )

    comment = st.text_input(
        "Comment (optional)",
        value=existing.get("comment", ""),
        key=f"tl_comment_{current_sample_id}",
    )

    rating_row = {
        "round_id": round_id,
        "sample_id": current_sample_id,
        "reviewer_id": reviewer_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "playable": str(playable),
        "difficulty_fit": str(difficulty_fit),
        "readability": str(readability),
        "melody_match": str(melody_match),
        "accidentals_confusing": str(accidentals_confusing),
        "comment": str(comment),
    }
    _upsert_rating(round_dir, rating_row)
    st.caption("Response auto-saved.")

    n1, n2 = st.columns(2)
    with n1:
        if st.button("Previous Sample", use_container_width=True):
            idx = sample_ids.index(current_sample_id)
            st.session_state.tl_sample_id = sample_ids[max(0, idx - 1)]
            st.rerun()
    with n2:
        if st.button("Next Sample", use_container_width=True):
            idx = sample_ids.index(current_sample_id)
            st.session_state.tl_sample_id = sample_ids[min(len(sample_ids) - 1, idx + 1)]
            st.rerun()

    st.markdown("### 3) Submit and Finish")
    if remaining == 0:
        st.success("All samples completed for this round. Thank you.")
    else:
        st.info("Finish all samples, then return to this section for completion.")
    st.markdown(f"- Ratings file: `{_ratings_path(round_dir)}`")


if __name__ == "__main__":
    main()
