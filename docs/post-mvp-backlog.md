# Post-MVP Backlog

Prioritized follow-up items after MVP final release.

## P1 - Release Hardening
1. Add a small automated regression script for run-history UI contracts (filters/sort/cache semantics).
2. Add fixture-based manifest compatibility tests for corrupted/partial/future fields.
3. Add explicit benchmark-result summary exporter (markdown/csv) for archival handoff.

## P2 - Workflow Quality
1. Add optional quick preview thumbnails for generated PDFs in-app.
2. Add richer part diagnostics (per-part note density/tessitura hints).
3. Add user-selectable default profile presets per session startup.
4. Add an output playback player (MIDI-first, with part mute/solo + tempo control) alongside MusicXML exports.
5. Add a readability-focused key-signature mode selector (`auto` vs `simplified/manual`) for cleaner beginner notation.

## P3 - Operational Ergonomics
1. Add one-click environment snapshot export (diagnostics + selected run detail).
2. Add retention presets for run maintenance (for example: keep 20/50/all).
3. Add explicit retention policy controls for `outputs/` and `downloads/` artifacts (separate from `temp/runs` prune).
4. Add optional scheduled stale reminders for preflight/run cache.

## P4 - Future Product Direction
1. Optional authentication model if deployment expands beyond trusted local use.
2. Team/teacher collaboration mode for shared benchmark notes.
3. Optional cloud/off-device execution path (if local constraints become limiting).
