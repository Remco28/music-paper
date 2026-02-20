# Release Checklist (MVP)

Use this checklist before handing a build to the teacher.

## Preconditions
- [ ] `venv` activated
- [ ] Dependencies installed from `requirements.txt`
- [ ] Required local tools installed (`demucs`, `basic-pitch`, `mscore`, `ffmpeg`)

## Quick Validation (target < 10 minutes)
- [ ] Run setup validator: `python scripts/validate_setup.py`
- [ ] Run smoke test: `python scripts/smoke_test.py`
- [ ] Start app: `streamlit run app.py --server.headless true --server.port 8501`

## Functional Pass
- [ ] Local-file pipeline run completes
- [ ] Single-video YouTube pipeline run completes
- [ ] Preflight gate blocks run when tools are missing
- [ ] Quick rerun generates a new run ID and isolated output folder
- [ ] Three-song benchmark worksheet completed: `docs/benchmark-3-song-pass.md`
- [ ] Benchmark decision is PASS (or blockers are explicitly documented)

## Artifact Validation
- [ ] ZIP contains conductor PDF
- [ ] ZIP contains assigned and non-empty part PDFs only
- [ ] ZIP contains full-score MusicXML
- [ ] ZIP contains `manifest.json`
- [ ] `manifest.json` includes: `run_id`, `timestamp`, `input`, `options`, `pipeline`, `assignments`, `parts`, `tool_versions`
- [ ] `manifest.json` outcome includes: `success`, `integrity_warnings`, `failure_stage`, `failure_summary`

## Sign-off
- [ ] Notes/issues captured in `comms/log.md`
- [ ] Commit includes updated docs/spec references when applicable
- [ ] Benchmark evidence and decision captured in `docs/benchmark-3-song-pass.md`
