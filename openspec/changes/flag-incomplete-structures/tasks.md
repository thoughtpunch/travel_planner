## 1. Orchestrator change

- [ ] 1.1 Add `mark_incomplete_structures(candidates)` helper to
      `app/orchestrator/structures.py` that returns a new list where
      every candidate belonging to a structure with no VALIDATED
      member has `Flag.INCOMPLETE` appended to `flags`.
- [ ] 1.2 In `app/orchestrator/runner.py`, call the helper after
      `validate_top_n` and before `rank_candidates`, so the flag is
      persisted on the `Itinerary` row.

## 2. Results payload

- [ ] 2.1 In `app/api/runs.py:_build_results_payload`, compute a
      `structures: {"A": "complete"|"incomplete"|"absent",
      "B": "complete"|"incomplete"|"absent"}` map from the candidate
      set.
- [ ] 2.2 Extend `ResultsOut` in `app/schemas.py` with a `structures`
      field (mapping `str → str`).

## 3. UI

- [ ] 3.1 In `app/templates/run.html`, for each structure in `["A",
      "B"]`, if `results.structures[s] == "incomplete"`, render a
      visible "Structure {s} — incomplete; cannot compare" note in
      place of an empty section.
- [ ] 3.2 Verify the existing `Flag.INCOMPLETE` badge style is defined
      in `base.html`; add `.b-INCOMPLETE` if missing.

## 4. Tests

- [ ] 4.1 In `tests/test_orchestrator.py`, add a unit test where
      Structure A has at least one VALIDATED candidate and Structure
      B has only LEADs; assert A is NOT flagged INCOMPLETE and B IS.
- [ ] 4.2 In `tests/test_orchestrator.py`, add a test where every
      structure has at least one VALIDATED candidate; assert no
      INCOMPLETE flag appears.
- [ ] 4.3 In `tests/test_runner_end_to_end.py`, add an assertion that
      the persisted `Itinerary.flags` of an only-LEAD structure
      includes `"INCOMPLETE"`.

## 5. Spec + validate

- [ ] 5.1 Update `openspec/specs/itinerary-orchestration/spec.md` with
      the new requirement (see this change's `specs/` delta).
- [ ] 5.2 Run `openspec validate flag-incomplete-structures --strict`.
- [ ] 5.3 Run `mise run test`.
