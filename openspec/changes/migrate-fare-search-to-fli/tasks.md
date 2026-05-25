## 1. Dependency

- [ ] 1.1 Add the `flights` package (the `fli` library) as a git
      dependency in `pyproject.toml`: under `[tool.uv.sources]` add
      `flights = { git = "https://github.com/punitarani/fli" }` and
      list `flights` under `[project.dependencies]`. Keep
      `fast-flights` installed and pinned to the existing GitHub
      source for one cycle.
- [ ] 1.2 Run `uv lock` and commit the updated `uv.lock`.
- [ ] 1.3 Run `mise run setup` to verify both libraries install
      cleanly side by side.

## 2. Enum + config

- [ ] 2.1 Add `Source.FLI = "fli"` to `app/enums.py`.
- [ ] 2.2 Add `primary_source: Literal["fli", "fast-flights"] = "fast-flights"`
      to `app/config.Settings` (env var `PRIMARY_SOURCE`). Default
      stays `fast-flights` until task 5.3 flips it.

## 3. Adapter

- [ ] 3.1 Create `app/sources/fli_source.py` exposing `FliSource`,
      implementing the `FareSource` Protocol from `app/sources/base.py`.
      Constructor accepts `currency: str = "USD"`; `name` is
      `Source.FLI`.
- [ ] 3.2 Translate `FareQuery` to a `fli.models.FlightSearchFilters`
      with one `FlightSegment` per logical leg (two for round-trips),
      using `Airport[code]` enum lookup, `TripType.ONE_WAY` /
      `TripType.ROUND_TRIP`, `SeatType.ECONOMY`, and
      `PassengerInfo(adults, children, infants_in_seat, infants_on_lap)`
      mapped from the existing `FareQuery` fields.
- [ ] 3.3 Map results to `FareOffer`: one-way → flatten
      `list[FlightResult]`; round-trip → collapse each
      `(outbound, return) tuple` into a single round-trip `FareOffer`
      whose `price_per_pax` is the tuple's total, carrier is the
      outbound primary airline, and `return_date` is the return
      `legs[0].departure_datetime.date()`.
- [ ] 3.4 Map `fli` typed exceptions
      (`SearchParseError`, `SearchHTTPError`, `SearchTimeoutError`,
      `SearchConnectionError`, `SearchClientError`) onto the existing
      `SourceError` envelope so the router treats them like any other
      adapter failure. Preserve the original exception class name in
      the `SourceError` message so logs can disambiguate.

## 4. Router + runner wiring

- [ ] 4.1 In `app/orchestrator/runner.py`, replace the hard-coded
      `FastFlightsSource(...)` construction with a small factory
      driven by `settings.primary_source` that returns either
      `FliSource` or `FastFlightsSource`.
- [ ] 4.2 Confirm `app/sources/router.py` does not need changes
      (the router takes any `FareSource`-shaped object).
- [ ] 4.3 Update `app/sources/__init__.py` to re-export `FliSource`.

## 5. Tests

- [ ] 5.1 Create `tests/test_fli_contract.py` modelled on
      `tests/test_fast_flights_contract.py`. Assert the public
      attributes the adapter relies on: `FlightSearchFilters`,
      `FlightSegment`, `PassengerInfo`, `SeatType`, `TripType`,
      `Airport` enum, `SearchFlights.search`, and on `FlightResult`:
      `legs`, `stops`, `price`, `currency`,
      `primary_airline_name`. Test should NOT issue live HTTP — use
      `unittest.mock.patch` against
      `fli.search.client.HttpClient.post` to return a fixed JSON
      payload, then verify the parser path produces an expected
      `FlightResult`. If the upstream surface drifts the contract
      test fails first, not the orchestrator.
- [ ] 5.2 Add a parametrised unit test in
      `tests/test_fli_contract.py` (or a new
      `tests/test_fli_adapter.py`) that drives `FliSource.search`
      with a mocked `SearchFlights.search` returning canned
      one-way and round-trip results and asserts the resulting
      `FareOffer` list shape and values, including correct
      `return_date` population for the round-trip branch.
- [ ] 5.3 Once 5.1 and 5.2 pass, flip the default in
      `app/config.Settings`: `primary_source: Literal[...] = "fli"`.
      Verify the full `mise run test` suite still passes.

## 6. Docs

- [ ] 6.1 Update `README.md` "Configuration (`.env`)" table with a
      `PRIMARY_SOURCE` row (default `fli`, alternatives
      `fast-flights`).
- [ ] 6.2 Add a one-line pointer at the top of
      `docs/research-fli-vs-fast-flights.md` noting the migration
      change that implemented its recommendation.

## 7. Spec + validate

- [ ] 7.1 Sync the modified `fare-search` requirement from this
      change's `specs/fare-search/spec.md` into
      `openspec/specs/fare-search/spec.md` (rename + rewrite of
      "Primary fare source via fast-flights scraper" →
      "Primary fare source via configured scraper" with the new
      parse-error and operator-override scenarios).
- [ ] 7.2 Run `openspec validate migrate-fare-search-to-fli --strict`.
- [ ] 7.3 Run `mise run test`.
