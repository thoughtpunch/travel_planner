## Why

`fare-search`'s **Fallback fare source via SerpAPI** requirement contains
the scenario:

> **WHEN** no SerpAPI API key is configured **AND** the primary scraper
> fails **THEN** the system SHALL record the query as `FAILED` with reason
> `no_fallback_available` and continue the run without aborting the whole
> sweep.

Today, when the scraper fails and no SerpAPI fallback is configured,
`SourceRouter.sweep` returns `RoutedResult(offers=[], error="primary
failed (...); no fallback configured")`. The runner logs a warning but
**no `Fare` row is persisted** — the failure is invisible in the audit
trail. Operators reviewing a run see "0 fares for this leg" with no
distinction between "scraper said no flights" (which the spec also
forbids treating as truth) and "scraper crashed and we had no fallback".

This change closes the gap so the audit trail matches what the spec
requires.

## What Changes

- `SourceRouter.sweep` returns a `FAILED` marker offer (analogous to
  the existing `_skipped_quota_marker`) when the primary fails and no
  fallback is configured.
- The runner persists these markers as `Fare` rows with
  `verification_status = FAILED`, `source = fast-flights` (the one that
  failed), `price_per_pax = 0`, and `notes` containing the failure
  reason (`"no_fallback_available"` or the raw fallback error).
- The results payload includes a `failed_query_count` so the UI can
  surface "N queries failed; results may be incomplete" rather than
  pretending those queries didn't happen.
- The Jinja `run.html` template renders FAILED rows in a "Failed
  queries" disclosure block with the failure reason.

The same persistence path also applies to the existing
`primary-failed-and-fallback-also-failed` branch, which today returns
`offers=[]` and an error string.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `fare-search`: clarify that **FAILED queries are persisted as Fare
  rows** with `verification_status = FAILED` and a machine-readable
  reason, so the audit trail records the failure rather than dropping
  it.

## Impact

- **Affected code:**
  - `app/sources/router.py` — emit a `_failed_marker(query, reason)`
    in the two failure paths that currently return `offers=[]`.
  - `app/orchestrator/runner.py` — persist FAILED markers as `Fare`
    rows (they already flow through `sweep_offers_by_leg`, so the
    persistence path is largely free; check `notes` capture).
  - `app/schemas.py` — add `failed_query_count: int` to `ResultsOut`.
  - `app/api/runs.py:_build_results_payload` — compute and include the
    count.
  - `app/templates/run.html` — render a "Failed queries" section.
- **Affected specs:** `openspec/specs/fare-search/spec.md` MODIFIED.
- **Affected tests:**
  - New unit test in `tests/test_serpapi_adapter.py` or a new
    `tests/test_router.py` covering the no-fallback path.
  - Assertion in `tests/test_runner_end_to_end.py` that a forced
    scraper-failure-with-no-fallback produces a FAILED Fare row.
- **Dependency:** lands after `seed-openspec-specs`. Independent of
  `flag-incomplete-structures` (can land in either order).
