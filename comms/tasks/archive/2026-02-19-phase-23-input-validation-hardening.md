# Task Spec: BTT Phase 23 - Input Validation Hardening

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Harden input-stage validation to fail fast with clear guidance for unsupported local files and malformed/non-single-video YouTube URLs.

## Rationale
Pipeline and observability are mature, but early input rejection can still be clearer. Stronger upfront validation reduces wasted run attempts and support churn.

## User Stories
1. As a teacher, I get immediate clear feedback if my file type or URL is invalid.
2. As a maintainer, I can trust that input-stage failures are categorized before pipeline work starts.
3. As a user, valid single-video URLs and supported local files continue to work unchanged.

## In Scope
- Add stricter local-file extension and empty-file guards.
- Add stricter YouTube URL checks (single-video only, no playlist links).
- Provide concise, actionable error hints.
- Keep existing input flow and run creation semantics intact.
- Update troubleshooting docs if messaging changes materially.

## Out of Scope
- Network reachability probing before submit.
- New input sources.
- Full URL normalization library.

## Required File Changes
- `app.py`
- `pipeline.py` (only if helper extraction needed)
- `docs/troubleshooting.md`

## Required Functional Changes
1. **Local File Guards**
   - Reject unsupported extensions before processing.
   - Reject zero-byte uploads with clear message.

2. **YouTube URL Guards**
   - Reject empty/non-http URLs.
   - Reject playlist URLs (`list=` present) explicitly.
   - Require recognizable YouTube host patterns already in project scope.

3. **Error Messaging**
   - Keep messages short and next-step oriented.
   - Preserve current stage-specific error style.

4. **Behavior Preservation**
   - Do not alter successful input behavior.
   - Do not add new dependencies.

## Constraints
- Local-only app assumptions remain.
- No new dependencies.
- Maintain existing run isolation and preflight semantics.

## Acceptance Criteria
1. Invalid local files/URLs are blocked before heavy processing.
2. Error messages are specific and actionable.
3. Valid existing input paths continue to work.
4. Existing validation checks pass.

## Review Notes for Developer
- Keep validation logic explicit and easy to audit.
- Reuse existing config constants for supported formats/domains.
- Avoid overfitting to edge URL variants beyond stated scope.
