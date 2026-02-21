from __future__ import annotations

import base64
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from musicality_eval_batch import run_batch


MUSICALITY_ROOT = PROJECT_ROOT / "datasets" / "musicality_rounds"
RUNS_ROOT = PROJECT_ROOT / "temp" / "runs"
BENCHMARK_TEMPLATE = PROJECT_ROOT / "docs" / "templates" / "phase42_benchmark_set_v1.template.json"


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


def _load_benchmark_songs() -> list[dict]:
    if not BENCHMARK_TEMPLATE.exists():
        return []
    data = _load_json(BENCHMARK_TEMPLATE)
    return list(data.get("songs") or [])


def _discover_success_runs() -> list[dict]:
    rows: list[dict] = []
    if not RUNS_ROOT.exists():
        return rows
    for manifest_path in sorted(RUNS_ROOT.glob("*/manifest.json"), key=lambda path: path.parent.name, reverse=True):
        try:
            data = _load_json(manifest_path)
        except Exception:
            continue
        outcome = data.get("outcome") or {}
        if outcome.get("success") is not True:
            continue
        rows.append(
            {
                "run_id": str(data.get("run_id") or manifest_path.parent.name),
                "timestamp": str(data.get("timestamp", "")),
                "input_value": str((data.get("input") or {}).get("value", "")),
                "profile": str((data.get("options") or {}).get("profile", "")),
                "fit_label": str((data.get("options") or {}).get("fit_label", "")),
                "exported_parts": int((data.get("outcome") or {}).get("exported_part_count", 0)),
            }
        )
    return rows


def _filter_runs_for_song(all_runs: list[dict], song: dict) -> list[dict]:
    song_url = str(song.get("url", "")).strip()
    if not song_url:
        return all_runs
    match = [row for row in all_runs if song_url in str(row.get("input_value", ""))]
    if match:
        return match
    return all_runs


def _render_round_builder() -> None:
    st.markdown("### 1) Build Round (Automated)")
    songs = _load_benchmark_songs()
    runs = _discover_success_runs()
    if not songs:
        st.warning(f"Missing benchmark template: `{BENCHMARK_TEMPLATE}`")
        return
    if not runs:
        st.info("No successful runs found yet in `temp/runs`.")
        return

    song_map = {f"{item.get('title')} - {item.get('artist')}": item for item in songs}
    song_label = st.selectbox("Benchmark song", options=list(song_map.keys()))
    song = song_map[song_label]
    filtered = _filter_runs_for_song(runs, song)
    run_ids = [row["run_id"] for row in filtered]
    if not run_ids:
        st.warning("No candidate runs found for selected song.")
        return

    st.caption(f"Found {len(run_ids)} successful runs for selection.")
    with st.expander("Show matching runs", expanded=False):
        st.dataframe(filtered, use_container_width=True)

    baseline = st.selectbox("Baseline run", options=run_ids, key="ml_baseline")
    default_candidates = [rid for rid in run_ids if rid != baseline][:5]
    candidates = st.multiselect(
        "Candidate runs",
        options=[rid for rid in run_ids if rid != baseline],
        default=default_candidates,
        key="ml_candidates",
    )
    default_round = f"phase42_{song.get('id','song')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    round_id = st.text_input("Round ID", value=default_round, key="ml_round_id")

    if st.button("Create + Score Round", use_container_width=True):
        if not candidates:
            st.error("Select at least one candidate run.")
            return
        run_sequence = [baseline] + [item for item in candidates if item != baseline]
        with st.spinner("Scoring variants..."):
            try:
                result = run_batch(
                    run_ids=run_sequence,
                    runs_dir=RUNS_ROOT,
                    out_root=MUSICALITY_ROOT,
                    round_id=round_id,
                    top_n=3,
                )
            except Exception as exc:
                st.error(f"Round creation failed: {exc}")
                return
        st.session_state.ml_selected_round = str(result["round_id"])
        st.success(
            f"Round ready: `{result['round_id']}` | candidates={result['candidate_count']}"
        )
        st.rerun()


def _render_round_review() -> None:
    st.markdown("### 2) Ranked Review + A/B")
    round_dirs = _round_dirs()
    if not round_dirs:
        st.info("No musicality rounds found yet. Build one above.")
        return

    round_map = {item.name: item for item in round_dirs}
    options = list(round_map.keys())
    preselected = st.session_state.get("ml_selected_round", "")
    index = options.index(preselected) if preselected in round_map else 0
    round_name = st.selectbox("Round", options=options, index=index)
    round_dir = round_map[round_name]
    summary = _load_json(round_dir / "summary.json")
    auto_scores = _load_json(round_dir / "auto_scores.json")
    round_manifest = _load_json(round_dir / "round_manifest.json")
    candidates = list(auto_scores.get("candidates") or [])
    if not candidates:
        st.error("No candidates found in auto_scores.")
        return

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

    st.markdown("**Top Candidate (Auto-Score)**")
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

    st.markdown("### 3) A/B Queue")
    reviewer_id = st.text_input("Reviewer ID", key="ml_reviewer_id")
    if not reviewer_id.strip():
        st.caption("Enter reviewer ID to record A/B votes.")
        return

    baseline_run_id = str((round_manifest.get("runs_requested") or [""])[0])
    by_run = {str(item.get("run_id", "")): item for item in candidates}
    top_candidates = [item for item in candidates if str(item.get("run_id", "")) != baseline_run_id][:3]
    queue: list[tuple[dict, dict]] = []
    if baseline_run_id in by_run and top_candidates:
        baseline = by_run[baseline_run_id]
        for item in top_candidates:
            queue.append((baseline, item))
    if not queue:
        # fallback generic queue
        for i in range(len(candidates) - 1):
            queue.append((candidates[i], candidates[i + 1]))

    queue_labels = [
        f"{idx+1}. {a.get('run_id')} vs {b.get('run_id')}" for idx, (a, b) in enumerate(queue)
    ]
    queue_choice = st.selectbox("A/B Pair", options=queue_labels, key="ml_queue_choice")
    pair_idx = queue_labels.index(queue_choice)
    cand_a, cand_b = queue[pair_idx]

    left, right = st.columns(2)
    with left:
        st.markdown(f"**A:** `{cand_a.get('run_id')}`")
        st.caption(f"score={cand_a.get('aggregate_score')} | hard_gate={cand_a.get('hard_gate_pass')}")
        pdf_a = _candidate_pdf(str(cand_a.get("run_id", "")))
        if pdf_a:
            _embed_pdf(pdf_a)
    with right:
        st.markdown(f"**B:** `{cand_b.get('run_id')}`")
        st.caption(f"score={cand_b.get('aggregate_score')} | hard_gate={cand_b.get('hard_gate_pass')}")
        pdf_b = _candidate_pdf(str(cand_b.get("run_id", "")))
        if pdf_b:
            _embed_pdf(pdf_b)

    winner_choice = st.radio("Which is more musical?", options=["A", "B", "Tie"], horizontal=True)
    confidence = st.radio("Confidence", options=["low", "medium", "high"], horizontal=True, index=1)
    notes = st.text_input("Notes (optional)", key="ml_vote_notes")

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
        st.rerun()

    votes_path = round_dir / "ab_votes.csv"
    votes = _read_votes(votes_path)
    st.caption(f"Current votes: {len(votes)} | file: `{votes_path}`")

    st.markdown("### 4) Decision Summary")
    candidates_by_id = {str(item.get("run_id", "")): item for item in candidates}
    counts: dict[str, int] = {key: 0 for key in candidates_by_id}
    for vote in votes:
        outcome = str(vote.get("winner", "")).strip()
        if outcome == "A":
            counts[str(vote.get("candidate_a", ""))] = counts.get(str(vote.get("candidate_a", "")), 0) + 1
        elif outcome == "B":
            counts[str(vote.get("candidate_b", ""))] = counts.get(str(vote.get("candidate_b", "")), 0) + 1
    voted_winner = max(counts.items(), key=lambda item: item[1])[0] if counts else ""
    suggested = voted_winner or str((summary.get("winner") or {}).get("run_id", ""))
    promote_pick = st.selectbox(
        "Promote Candidate",
        options=list(candidates_by_id.keys()),
        index=list(candidates_by_id.keys()).index(suggested) if suggested in candidates_by_id else 0,
        key="ml_promote_pick",
    )
    if st.button("Write Decision Summary", use_container_width=True):
        decision = {
            "round_id": str(summary.get("round_id", round_dir.name)),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "auto_winner": str((summary.get("winner") or {}).get("run_id", "")),
            "vote_counts": counts,
            "human_top": voted_winner,
            "promoted_run_id": promote_pick,
            "vote_count": len(votes),
        }
        decision_path = round_dir / "decision_summary.json"
        decision_path.write_text(json.dumps(decision, indent=2))
        st.success(f"Wrote `{decision_path}`")


def main() -> None:
    st.set_page_config(page_title="Musicality Lab", layout="wide")
    st.title("Musicality Lab")
    st.caption("Guided workflow: build round -> score automatically -> A/B vote -> decision summary.")
    _render_round_builder()
    st.divider()
    _render_round_review()


if __name__ == "__main__":
    main()

