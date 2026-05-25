## Why

The Phase-1 primary fare scraper is `fast-flights` (AWeirdDev/flights, currently pinned to the `thoughtpunch/flights` fork at v3.0rc1). Per the research in `docs/research-fli-vs-fast-flights.md`, that library has been in release-candidate purgatory since 2026-02-16 with one human maintainer who has publicly disclosed low bandwidth, an HTML-scrape parser that still ships a stray `print(data)` on every call, and an open unfixed regression (#146) where a single row of a different shape crashes the whole parser. For a project whose central design constraint is "the scraper WILL break and the system must degrade gracefully" (see `docs/design.md` Decision 2), this is a chronic failure surface.

The alternative `fli` (`punitarani/fli`, PyPI package name `flights`) is more actively maintained (last commit 2026-05-24, 160 commits from the lead maintainer, 2,667 stars), hits Google's internal `FlightsFrontendService` POST endpoints directly via `curl_cffi` (no HTML scrape), is Pydantic v2 native, ships typed exceptions (`SearchParseError`, `SearchClientError`, `SearchTimeoutError`, `SearchConnectionError`, `SearchHTTPError`), has a built-in 10 req/s token-bucket rate limiter shared across threads, has `tenacity`-backed retries, and exposes a richer per-fare data model (flight numbers, per-leg layovers, CO2, amenities, aircraft, plus a follow-up `get_booking_options()` call returning vendor booking URLs).

The Trip Planner already isolates the scraper behind the `FareSource` Protocol in `app/sources/base.py`, so swapping it is a single new adapter file plus an enum value — no orchestrator changes.

This change does **not** alter the LEAD / VALIDATED contract: `fli` still returns Google Flights display fares and cannot resolve the 6-pax display-fare collapse, so SerpAPI remains the only authoritative validation source. The migration is about reliability and data quality of the *sweep* step, not about the validation contract.

## What Changes

- Add `app/sources/fli_source.py` implementing the `FareSource` Protocol against the `fli` library, branching on `TripType.ONE_WAY` (list of `FlightResult`) vs `TripType.ROUND_TRIP` / `MULTI_CITY` (list of `(outbound, return)` tuples).
- Add `Source.FLI = "fli"` to `app/enums.py`.
- Update `app/sources/router.py` so the primary source is selectable; default flips to `FliSource` once the contract test passes against a live call.
- Add `PRIMARY_SOURCE` env var (`fli` | `fast-flights`, default `fli`) read by `app/config.py`; runner wires the configured source at startup.
- Update `pyproject.toml`: add the `flights` package from `https://github.com/punitarani/fli` (the `fli` repo), keep `fast-flights` installed for one release cycle so an operator can flip the env var to A/B compare.
- Add `tests/test_fli_contract.py` pinning the `fli` attributes the adapter reads (`FlightResult.legs`, `FlightLeg.airline`, `FlightLeg.duration`, `FlightResult.stops`, `FlightResult.price`, `FlightResult.currency`, `FlightSegment(departure_airport=[[Airport[...], 0]], …)` wire-format) so an upstream rename fails loudly.
- Map typed `fli` exceptions onto the existing `SourceError` envelope so the router's fallback-on-error behaviour keeps working without source-specific glue.

After one cycle of production use, a follow-up change will REMOVE the `fast-flights` dependency, the `Source.FAST_FLIGHTS` enum value, and `app/sources/fast_flights_source.py`. That removal is deliberately **out of scope** here.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `fare-search`: the existing "Primary fare source via fast-flights scraper" requirement is **renamed and rewritten** to "Primary fare source via configured scraper" with `fli` as the new default and `fast-flights` retained as a switchable legacy backend for one cycle. The other four requirements (Scraper fares are LEADs, Fallback fare source via SerpAPI, SerpAPI quota protection, Passenger count fidelity) are unchanged.

## Impact

- **Affected code:**
  - `app/sources/fli_source.py` — new adapter.
  - `app/enums.py` — `Source.FLI`.
  - `app/config.py` — `PRIMARY_SOURCE` setting.
  - `app/sources/router.py` — primary-source selection.
  - `app/orchestrator/runner.py` — wire selected primary instead of hard-coding `FastFlightsSource`.
  - `pyproject.toml` — add `flights` (fli) as a git dependency from `https://github.com/punitarani/fli`; keep `fast-flights` for now.
- **Affected specs:** `openspec/specs/fare-search/spec.md` rewrites the primary-source requirement.
- **Affected tests:** new `tests/test_fli_contract.py` mirrors `tests/test_fast_flights_contract.py`; `tests/test_runner_end_to_end.py` patches `FliSource.search` instead of (or in addition to) `FastFlightsSource.search` once the default flips.
- **Failure mode mapping (per `docs/design.md`):** addresses **Failure mode 3** ("Scraper outage producing silent wrong answers") — fli's typed errors let the router distinguish "Google responded with unparseable shape" (raises `SearchParseError`) from "network failed" (raises `SearchConnectionError`), so fallback decisions can be more precise than today's blanket `except Exception`.
- **SerpAPI quota cost:** zero. This change touches the sweep source only; validation continues to use SerpAPI exactly as before.
- **Phase:** Phase 1.
- **Dependency:** lands after `seed-openspec-specs` (uses the seeded `fare-search` main spec). Independent of `flag-incomplete-structures`, `persist-no-fallback-failed-fares`, and `port-models-to-pydantic-with-alembic`.
