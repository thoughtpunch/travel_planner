## Why

`itinerary-orchestration`'s **Dual structure pricing** requirement says:

> if a structure cannot be fully validated, reports it as "incomplete —
> cannot compare" rather than silently dropping it

The data model already has the slot for this signal — `Flag.INCOMPLETE`
is defined in `app/enums.py:33` — but nothing in the orchestrator or
ranker ever applies it. When Structure A produces only LEAD-or-failed
candidates and Structure B produces a VALIDATED winner, the UI today
shows the B winner alone and silently omits A. That is exactly the
silent-drop failure mode the spec was written to prevent.

## What Changes

- After validation, the orchestrator computes per-structure validation
  completeness. A structure is "complete" when at least one of its
  candidates reaches `VALIDATED`; otherwise it is "incomplete".
- Each candidate of an incomplete structure receives `Flag.INCOMPLETE`
  in `Itinerary.flags`.
- The structure-comparison summary in `_build_results_payload`
  (`app/api/runs.py`) exposes per-structure completeness so the UI can
  render the "incomplete — cannot compare" message instead of an
  empty/missing section.
- The Jinja `run.html` template renders an explicit per-structure note
  when `INCOMPLETE` is present, instead of just rendering nothing.
- Tests in `tests/test_orchestrator.py` cover both halves: a structure
  with at least one VALIDATED is *not* flagged INCOMPLETE; a structure
  with only LEAD/VALIDATION_FAILED *is* flagged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `itinerary-orchestration`: add an explicit **Incomplete-structure
  flagging** requirement specifying *how* "incomplete — cannot compare"
  is signalled (via `Flag.INCOMPLETE`) and *where* it surfaces (run
  results payload + UI).

## Impact

- **Affected code:**
  - `app/orchestrator/structures.py` — helper to detect incomplete
    structures.
  - `app/orchestrator/runner.py` — apply `Flag.INCOMPLETE` to each
    candidate of an incomplete structure before persisting itineraries.
  - `app/api/runs.py` — surface `structures: {"A": "complete",
    "B": "incomplete"}` (or similar) in `ResultsOut`.
  - `app/schemas.py` — extend `ResultsOut` with the new field.
  - `app/templates/run.html` — render the incomplete-structure notice.
- **Affected specs:** `openspec/specs/itinerary-orchestration/spec.md`
  gains the new requirement.
- **Affected tests:** new cases in `tests/test_orchestrator.py`; an
  end-to-end assertion in `tests/test_runner_end_to_end.py`.
- **Dependency:** lands after `seed-openspec-specs`.
