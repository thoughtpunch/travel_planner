## 1. Router — emit FAILED markers

- [x] 1.1 Add `_failed_marker(query, reason)` helper to
      `app/sources/router.py` mirroring `_skipped_quota_marker`, but
      with `verification_status = FAILED` and `raw["reason"] = reason`.
- [x] 1.2 In `SourceRouter.sweep`, when `self.fallback is None` and
      the primary errored/empty, return a `RoutedResult` whose
      `offers` is `[_failed_marker(query, "no_fallback_available")]`
      (instead of `offers=[]`).
- [x] 1.3 In `SourceRouter.sweep`, when fallback also raises a
      `SourceError`, return `offers=[_failed_marker(query,
      f"fallback_failed: {error}")]` instead of `offers=[]`.
- [x] 1.4 Keep the existing `error` field populated so logs remain
      informative.

## 2. Runner — persist as Fare rows

- [x] 2.1 Confirm FAILED markers already pass through
      `sweep_offers_by_leg[leg.ordinal]` and into structure assembly.
      If structure assembly filters them out (cheapest-per-route
      ignores price=0 entries), wire them onto an `out_of_band_fares`
      list and add them to the persisted `Fare` rows alongside
      itinerary fares.
      (Done: split markers from `leg_offers` in the sweep loop into
      `out_of_band_markers` and persist them up-front as Fare rows
      with empty `structure`, so structure assembly never sees them.)
- [x] 2.2 Ensure persisted FAILED `Fare` rows have `price_per_pax=0`,
      `price_party=0`, `verification_status="FAILED"`, and
      `notes=json.dumps({"reason": <reason>, ...})`.

## 3. Results payload

- [x] 3.1 Add `failed_query_count: int` to `ResultsOut` in
      `app/schemas.py`. (Also `failed_fares: list[FailedFareOut]` for
      the UI table.)
- [x] 3.2 In `_build_results_payload`, set
      `failed_query_count = sum(1 for f in fare_rows if
      f.verification_status == "FAILED")`.

## 4. UI

- [x] 4.1 In `app/templates/run.html`, render a "Failed queries
      ({{ failed_query_count }})" disclosure block that lists each
      FAILED `Fare` row (route, date, reason).
- [x] 4.2 Ensure `.b-FAILED` badge style exists in `base.html`
      (already present).

## 5. Tests

- [x] 5.1 Add `tests/test_router.py` (new file) or extend
      `tests/test_serpapi_adapter.py` with a `SourceRouter` test:
      given a primary that raises and `fallback=None`, the routed
      result contains one FAILED marker with
      `reason="no_fallback_available"`.
- [x] 5.2 In `tests/test_runner_end_to_end.py`, add a test where the
      `FastFlightsSource` is monkeypatched to raise and the SerpAPI
      key is empty; assert at least one persisted `Fare` row has
      `verification_status="FAILED"` and the `ResultsOut` reports
      `failed_query_count > 0`.

## 6. Spec + validate

- [x] 6.1 Update `openspec/specs/fare-search/spec.md` per this
      change's delta in `specs/`.
- [x] 6.2 Run `openspec validate persist-no-fallback-failed-fares
      --strict`.
- [x] 6.3 Run `mise run test`.
