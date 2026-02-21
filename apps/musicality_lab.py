from __future__ import annotations

import base64
import csv
import json
from datetime import datetime
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MUSICALITY_ROOT = PROJECT_ROOT / "datasets" / "musicality_rounds"


def _round_dirs() -> list[Path]:
    if not MUSICALITY_ROOT.exists():
        return []
    dirs = [path for path in MUSICALITY_ROOT.iterdir() if path.is_dir() and (path / "summary.json").exists()]
    dirs.sort(key=lambda path: path.name, reverse=True)
    return dirs


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _embed_pdf(path: Path) -> None:
    if not path.exists():
        st.warning(f"Missing PDF: {path}")
        return
    payload = base64.b64encode(path.read_bytes()).decode("utf-8")
    src = f"data:application/pdf;base64,{payload}"
    st.markdown(
        (
            f'<iframe src="{src}" width="100%" height="560" '
            'style="border:1px solid #ccc; border-radius:8px;"></iframe>'
        ),
        unsafe_allow_html=True,
    )


def _read_votes(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as handle:
        return list(csv.DictReader(handle))


def _append_vote(path: Path, row: dict) -> None:
    fieldnames = [
        "round_id",
        "timestamp",
        "reviewer_id",
        "candidate_a",
        "candidate_b",
        "winner",
        "confidence",
        "notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = _read_votes(path)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in existing:
            writer.writerow({key: item.get(key, "") for key in fieldnames})
        writer.writerow({key: row.get(key, "") for key in fieldnames})


def _candidate_pdf(run_id: str, title_hint: str | None = None) -> Path | None:
    output_dir = PROJECT_ROOT / "outputs" / run_id
    if not output_dir.exists():
        return None
    candidates = sorted(output_dir.glob("*_full_score.pdf"))
    if title_hint:
        for candidate in candidates:
            if title_hint.lower() in candidate.name.lower():
                return candidate
    return candidates[0] if candidates else None


def main() -> None:
    st.set_page_config(page_title="Musicality Lab", layout="wide")
    st.title("Musicality Lab")
    st.caption("Ranked candidate review with fast A/B voting for musicality tuning.")

    round_dirs = _round_dirs()
    if not round_dirs:
        st.error("No musicality rounds found in `datasets/musicality_rounds/`.")
        st.info("Run `python scripts/musicality_eval_batch.py --run-id ...` first.")
        return

    round_map = {item.name: item for item in round_dirs}
    round_name = st.selectbox("Round", options=list(round_map.keys()))
    round_dir = round_map[round_name]
    summary = _load_json(round_dir / "summary.json")
    auto_scores = _load_json(round_dir / "auto_scores.json")
    candidates = list(auto_scores.get("candidates") or [])
    if not candidates:
        st.error("No candidates found in auto_scores.")
        return

    st.markdown("### Ranked Candidates")
    table = [
        {
            "rank": item.get("rank"),
            "run_id": item.get("run_id"),
            "variant_id": item.get("variant_id"),
            "profile": item.get("profile"),
            "hard_gate_pass": item.get("hard_gate_pass"),
            "aggregate_score": item.get("aggregate_score"),
        }
        for item in candidates
    ]
    st.dataframe(table, use_container_width=True)

    st.markdown("### Top Candidate")
    winner = summary.get("winner") or {}
    st.json(
        {
            "run_id": winner.get("run_id"),
            "variant_id": winner.get("variant_id"),
            "profile": winner.get("profile"),
            "aggregate_score": winner.get("aggregate_score"),
            "hard_gate_pass": winner.get("hard_gate_pass"),
        }
    )

    st.markdown("### A/B Vote")
    reviewer_id = st.text_input("Reviewer ID")
    if not reviewer_id.strip():
        st.caption("Enter reviewer ID to record A/B votes.")
        return

    candidate_keys = [f"{item.get('run_id')} | {item.get('variant_id')}" for item in candidates]
    key_to_candidate = {key: item for key, item in zip(candidate_keys, candidates)}

    c1, c2 = st.columns(2)
    with c1:
        pick_a = st.selectbox("Candidate A", options=candidate_keys, key="ml_pick_a")
    with c2:
        pick_b = st.selectbox("Candidate B", options=candidate_keys, index=min(1, len(candidate_keys) - 1), key="ml_pick_b")

    cand_a = key_to_candidate[pick_a]
    cand_b = key_to_candidate[pick_b]

    left, right = st.columns(2)
    with left:
        st.markdown(f"**A:** `{cand_a.get('run_id')}`")
        st.caption(
            f"score={cand_a.get('aggregate_score')} | hard_gate={cand_a.get('hard_gate_pass')}"
        )
        pdf_a = _candidate_pdf(str(cand_a.get("run_id", "")))
        if pdf_a:
            _embed_pdf(pdf_a)
    with right:
        st.markdown(f"**B:** `{cand_b.get('run_id')}`")
        st.caption(
            f"score={cand_b.get('aggregate_score')} | hard_gate={cand_b.get('hard_gate_pass')}"
        )
        pdf_b = _candidate_pdf(str(cand_b.get("run_id", "")))
        if pdf_b:
            _embed_pdf(pdf_b)

    winner_choice = st.radio("Which sounds/looks more musical?", options=["A", "B", "Tie"], horizontal=True)
    confidence = st.radio("Confidence", options=["low", "medium", "high"], horizontal=True, index=1)
    notes = st.text_input("Notes (optional)")

    if st.button("Record Vote", use_container_width=True):
        votes_path = round_dir / "ab_votes.csv"
        row = {
            "round_id": str(summary.get("round_id", round_dir.name)),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "reviewer_id": reviewer_id.strip(),
            "candidate_a": str(cand_a.get("run_id", "")),
            "candidate_b": str(cand_b.get("run_id", "")),
            "winner": winner_choice,
            "confidence": confidence,
            "notes": notes,
        }
        _append_vote(votes_path, row)
        st.success(f"Vote recorded in `{votes_path}`")

    votes_path = round_dir / "ab_votes.csv"
    vote_count = len(_read_votes(votes_path))
    st.caption(f"Current votes: {vote_count} | file: `{votes_path}`")


if __name__ == "__main__":
    main()

