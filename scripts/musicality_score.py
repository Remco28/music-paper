#!/usr/bin/env python3
"""Musicality auto-scoring utilities for candidate ranking."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from music21 import chord, converter, note, stream


@dataclass(frozen=True)
class NoteEvent:
    onset: float
    duration: float
    pitch_midi: int


def _iter_note_events(score_stream) -> list[NoteEvent]:
    events: list[NoteEvent] = []
    for element in list(score_stream.recurse().notes):
        if isinstance(element, chord.Chord):
            if not element.pitches:
                continue
            pitch_midi = int(max(p.midi for p in element.pitches))
        elif isinstance(element, note.Note):
            if element.pitch is None:
                continue
            pitch_midi = int(element.pitch.midi)
        else:
            continue
        try:
            onset = float(element.getOffsetInHierarchy(score_stream))
        except Exception:
            onset = 0.0
        duration = float(element.duration.quarterLength)
        events.append(NoteEvent(onset=max(0.0, onset), duration=max(0.0625, duration), pitch_midi=pitch_midi))
    events.sort(key=lambda item: (item.onset, item.pitch_midi))
    return events


def _load_events(path: Path) -> list[NoteEvent]:
    parsed = converter.parse(str(path))
    part = parsed.parts[0] if parsed.parts else parsed
    return _iter_note_events(part)


def _bin(onset: float, step: float = 0.25) -> int:
    return int(round(onset / step))


def _f1(precision: float, recall: float) -> float:
    if precision + recall <= 1e-9:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def _best_onset_alignment(reference: Iterable[NoteEvent], candidate: Iterable[NoteEvent]) -> tuple[float, int]:
    ref_bins = [_bin(item.onset) for item in reference]
    cand_bins = [_bin(item.onset) for item in candidate]
    if not ref_bins or not cand_bins:
        return 0.0, 0

    ref_set = set(ref_bins)
    best = (0.0, 0)
    for shift in range(-16, 17):
        shifted = {_bin_: True for _bin_ in (value + shift for value in cand_bins)}
        hit = sum(1 for value in shifted if value in ref_set)
        precision = hit / max(1, len(shifted))
        recall = hit / max(1, len(ref_set))
        score = _f1(precision, recall)
        if score > best[0]:
            best = (score, shift)
    return best


def _map_pitch_by_onset(events: Iterable[NoteEvent], shift_bins: int) -> dict[int, int]:
    mapped: dict[int, int] = {}
    for item in events:
        bucket = _bin(item.onset) + shift_bins
        # keep latest pitch in bucket deterministically
        mapped[bucket] = item.pitch_midi
    return mapped


def _pitch_similarity(reference: Iterable[NoteEvent], candidate: Iterable[NoteEvent], shift_bins: int) -> float:
    ref_map = _map_pitch_by_onset(reference, 0)
    cand_map = _map_pitch_by_onset(candidate, shift_bins)
    shared = sorted(set(ref_map.keys()) & set(cand_map.keys()))
    if not shared:
        return 0.0
    diffs = [abs(ref_map[idx] - cand_map[idx]) for idx in shared]
    avg = sum(diffs) / len(diffs)
    return max(0.0, min(1.0, 1.0 - (avg / 24.0)))


def _durations_by_onset(events: Iterable[NoteEvent], shift_bins: int) -> dict[int, float]:
    mapped: dict[int, float] = {}
    for item in events:
        bucket = _bin(item.onset) + shift_bins
        mapped[bucket] = float(item.duration)
    return mapped


def _rhythm_similarity(reference: Iterable[NoteEvent], candidate: Iterable[NoteEvent], shift_bins: int) -> float:
    ref_map = _durations_by_onset(reference, 0)
    cand_map = _durations_by_onset(candidate, shift_bins)
    shared = sorted(set(ref_map.keys()) & set(cand_map.keys()))
    if not shared:
        return 0.0
    ratios: list[float] = []
    for idx in shared:
        ref_d = max(0.0625, ref_map[idx])
        cand_d = max(0.0625, cand_map[idx])
        ratios.append(min(ref_d, cand_d) / max(ref_d, cand_d))
    return sum(ratios) / len(ratios)


def _fragmentation_penalty(events: Iterable[NoteEvent]) -> float:
    items = list(events)
    if not items:
        return 1.0
    short = sum(1 for item in items if item.duration <= 0.25)
    tiny = sum(1 for item in items if item.duration <= 0.125)
    return min(1.0, (0.65 * (short / len(items))) + (0.35 * (tiny / len(items))))


def _measure_integrity(path: Path) -> float:
    parsed = converter.parse(str(path))
    part = parsed.parts[0] if parsed.parts else parsed
    measures = list(part.recurse().getElementsByClass(stream.Measure))
    if not measures:
        return 0.0
    broken = 0
    for measure in measures:
        signatures = measure.getTimeSignatures(returnDefault=True)
        ts = signatures[0] if signatures else None
        target = float(ts.barDuration.quarterLength) if ts else 4.0
        duration = float(measure.duration.quarterLength)
        if abs(duration - target) > 1e-5:
            broken += 1
    return 1.0 - (broken / len(measures))


def _chord_density(path: Path) -> float:
    parsed = converter.parse(str(path))
    part = parsed.parts[0] if parsed.parts else parsed
    notes = list(part.recurse().notes)
    if not notes:
        return 0.0
    chords = sum(1 for item in notes if isinstance(item, chord.Chord))
    return chords / len(notes)


def score_candidate_part(reference_midi: Path, candidate_musicxml: Path) -> dict[str, float | bool]:
    """Score one part against its reference stem transcription."""
    reference_events = _load_events(reference_midi)
    candidate_events = _load_events(candidate_musicxml)
    onset_score, shift = _best_onset_alignment(reference_events, candidate_events)
    pitch_score = _pitch_similarity(reference_events, candidate_events, shift)
    rhythm_score = _rhythm_similarity(reference_events, candidate_events, shift)
    frag_penalty = _fragmentation_penalty(candidate_events)
    measure_integrity = _measure_integrity(candidate_musicxml)
    chord_density = _chord_density(candidate_musicxml)
    hard_gate_pass = bool(measure_integrity >= 0.999 and chord_density <= 0.05 and len(candidate_events) > 0)
    final_score = (0.40 * onset_score) + (0.30 * pitch_score) + (0.20 * rhythm_score) - (0.10 * frag_penalty)
    return {
        "hard_gate_pass": hard_gate_pass,
        "onset_score": round(onset_score, 4),
        "pitch_score": round(pitch_score, 4),
        "rhythm_score": round(rhythm_score, 4),
        "fragmentation_penalty": round(frag_penalty, 4),
        "measure_integrity": round(measure_integrity, 4),
        "chord_density": round(chord_density, 4),
        "time_shift_bins": int(shift),
        "part_score": round(max(0.0, min(1.0, final_score)), 4),
    }

