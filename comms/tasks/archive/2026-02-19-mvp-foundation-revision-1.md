# Task Spec: BTT MVP Foundation Revision 1

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY  
**Supersedes:** `comms/tasks/2026-02-19-mvp-foundation-spec.md` (implementation revision cycle)

## Objective
Resolve review findings that currently block MVP acceptance for Phase 1.

## Rationale
The current implementation is close, but it violates core functional requirements: full score pitch mode, environment compatibility, and deterministic input behavior. Fixing these is the shortest path to a valid MVP baseline.

## Blocking Issues To Fix
1. **Conductor score is not guaranteed concert pitch**
   - Current pipeline transposes each part before writing a single score, which causes the full score export to be transposed.
   - Requirement is: full conductor score in concert pitch, individual parts transposed.

2. **Dependency installation fails on current Python 3.12 environment**
   - `pip install -r requirements.txt` fails due resolver/build chain (`distutils` issue while resolving old `numpy` through `basic-pitch` compatibility path).
   - MVP install instructions currently claim Python 3.11/3.12 support, but the dependency set is not installable here as written.

3. **YouTube extraction can pick stale local artifacts**
   - `download_or_convert_audio` collects `temp/youtube_input.*` and selects the first match without clearing prior files.
   - This can bind a new URL request to an older downloaded artifact.

## Required File Changes
- `pipeline.py`
- `requirements.txt`
- `README_for_teacher.md`
- `start.bat`

## Required Behavior Changes
1. **Pitch-mode correctness**
   - Build concert-pitch score for conductor export.
   - Build transposed part exports for instrument PDFs.
   - Ensure part naming remains stable and mapped to assigned instruments.

2. **Installability on declared Python version(s)**
   - Set MVP support policy to **Python 3.11 only** for now.
   - Update `requirements.txt` and docs to match that policy.
   - Add a startup guard in `start.bat` that stops with a clear message if Python is not 3.11.

3. **Deterministic YouTube handling**
   - Ensure each URL conversion run isolates artifacts (unique temp path or pre-clean target pattern).
   - Keep single-video enforcement (`--no-playlist` and URL checks).

## Required Implementation Details
```text
For each assigned stem:
  parse MIDI once as concert-source
  derive:
    - concert version for full score
    - transposed version for part export according to instrument spec

Export:
  full_score.musicxml -> full_score.pdf (concert)
  each transposed_part.musicxml -> part PDF
```

For dependencies/runtime:
```text
Use Python 3.11 as required runtime for Phase 1.
Document setup with explicit 3.11 commands only.
Do not claim 3.12 support in MVP docs.
```

For YouTube isolation:
```text
Before each yt-dlp run:
  either clean prior youtube_input.* files
  or write into a unique per-run subdirectory/name
Then select only files produced by that run.
```

## Acceptance Criteria
1. Conductor score PDF is concert pitch.
2. Part PDFs are transposed to assigned instruments and include only assigned/non-empty parts.
3. Fresh clone + documented setup path can install dependencies successfully.
4. Repeated YouTube runs do not reuse stale files.
5. Existing MVP behaviors remain intact (local input, simplification controls, disclaimer text, ZIP export).

## Verification Checklist (Developer Must Run)
1. `python3.11 -m venv venv && ./venv/bin/pip install -r requirements.txt`
2. Run two consecutive YouTube imports with different URLs and verify distinct audio artifacts are used.
3. Generate one sample output and verify:
   - conductor PDF: concert pitch
   - at least one Bb instrument part: transposed pitch
4. Confirm unassigned stems do not produce part PDFs.
5. Capture command outputs/screenshots or concise notes in PR/task handoff.

## Review Notes for Developer
- Keep revision minimal and scoped; do not redesign UI flow.
- Add one small validation script or command sequence in docs proving setup/install success.
- Preserve existing function signatures unless a signature change is essential and documented.
