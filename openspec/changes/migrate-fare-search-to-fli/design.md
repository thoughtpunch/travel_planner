## Context

The primary fare scraper (`fast-flights`) is breaking with increasing frequency and the sole human maintainer has effectively signed off (README: _"i have other projects and life to do"_). The project's design explicitly anticipated this and isolated the dependency behind `FareSource` (`app/sources/base.py`) so a swap would be cheap. The research doc `docs/research-fli-vs-fast-flights.md` did the head-to-head; this change executes the recommendation.

## Goals / Non-Goals

**Goals:**
- Replace the default sweep scraper with `fli` and verify against a contract test analogous to `tests/test_fast_flights_contract.py`.
- Surface `fli`'s typed exceptions to the router so fallback decisions can distinguish parse failures from network failures.
- Keep `fast-flights` available behind a feature flag (`PRIMARY_SOURCE` env var) for one cycle so the swap is reversible without a code change.

**Non-Goals:**
- Removing the `fast-flights` adapter or dependency. That belongs to a follow-up change after one cycle of `fli`-default operation.
- Adopting any of `fli`'s richer fields (per-leg flight numbers, layovers, amenities, CO2, booking URLs). The `FareOffer` model stays as-is; richer fields will be picked up in a separate change with its own UI work.
- Using `fli.search.SearchFlights.get_booking_options()` as a substitute for SerpAPI validation. Booking options are still display-fare prices on the booking-vendor side; the 6-pax collapse still requires a SerpAPI re-query at full party.
- Changing the validation pass or the LEAD/VALIDATED contract.

## Decisions

### Decision 1: `fli` package is installed under its PyPI name `flights`, sourced from GitHub

`fli` publishes to PyPI as `flights` (not `fli` — the CLI is `fli`, the package is `flights`). To match the existing pattern (the `fast-flights` fork is already pinned to a GitHub source), we'll pin `flights` to `https://github.com/punitarani/fli` so we ride upstream HEAD. A `uv.sources` entry maps `flights = { git = "https://github.com/punitarani/fli" }`. This collides namespace-wise with the *concept* of "flights" but not with the `fast-flights` Python package, because the import path is `from fli import ...` (the `fli/` directory is the importable package; `flights` is just the distribution name).

### Decision 2: Feature flag with default flip after contract test passes

`PRIMARY_SOURCE` env var, read by `app/config.py`, controls which source the runner constructs as primary. `fast-flights` stays selectable via `PRIMARY_SOURCE=fast-flights` for one cycle. The new contract test (`tests/test_fli_contract.py`) is the precondition for flipping the default to `fli` — until then the default stays `fast-flights` so the merge is risk-free.

### Decision 3: Exception mapping is centralised in the adapter

`fli` raises typed exceptions (`SearchClientError`, `SearchHTTPError`, `SearchTimeoutError`, `SearchConnectionError`, `SearchParseError`). The router currently treats any non-empty offer list as success and any exception as fallback-trigger. We won't change the router contract; the adapter maps `SearchParseError` and connectivity/HTTP errors to the existing `SourceError` so the router sees the same envelope it sees from `FastFlightsSource`. A future change can teach the router to handle parse-vs-network differently if that proves valuable.

### Decision 4: `FlightSegment` shape stays awkward

`fli.models.FlightSegment.departure_airport` takes `list[list[Airport | int]]` because that's the wire format Google's RPC endpoint expects. We pass it through verbatim in the adapter rather than building a friendlier wrapper. If multi-stop or filter-rich features are added later, we can introduce a builder.

### Decision 5: One-way vs round-trip return shapes

`SearchFlights.search()` returns `list[FlightResult]` for ONE_WAY and `list[tuple[FlightResult, ...]]` for ROUND_TRIP / MULTI_CITY. The adapter branches once on `query.is_round_trip` and produces a flat `list[FareOffer]`; for round-trip we collapse each `(outbound, return)` tuple into a single round-trip `FareOffer` carrying both segments' carriers and the combined total price (`outbound.price` is already the full RT total on Google's side — verified by the round-trip test in `tests/test_fast_flights_rt.py`).

## Risks / Trade-offs

- **Risk:** `fli`'s upstream-HEAD pin could break the build mid-cycle. **Mitigation:** the contract test fails loudly on attribute drift, and `PRIMARY_SOURCE=fast-flights` is a one-env-var rollback. We accept this for the same reason `fast-flights` is pinned to a fork rather than a PyPI release: scraper libraries against an undocumented surface need to chase the surface aggressively, and stale pins lie.
- **Trade-off:** two scraper deps in the lock file for one cycle. The disk cost is negligible; the value of a flag-based rollback during the swap is high.
- **Trade-off:** the awkward `[[Airport, 0]]` shape leaks into the adapter. Acceptable — it's a single function and the cost of wrapping it is more code than it saves.
- **Risk:** `fli`'s `model_validator` rejects past travel dates. The Trip Planner only forward-searches so this is fine in production, but tests must use rolling future dates (a problem `tests/test_fast_flights_contract.py` also has).
- **Open question:** does the `fli` rate limiter (10 req/s, shared via a process-singleton) collide with the orchestrator's own sweep concurrency, if any? The current runner is sequential, so no collision today; if we add concurrency later we should consult `fli/search/client.py` `DEFAULT_CALLS_PER_SECOND`.
