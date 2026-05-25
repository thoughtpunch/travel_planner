# fli vs fast-flights: head-to-head research

## Summary & recommendation

**Recommendation: migrate to `fli`.** Both libraries scrape Google Flights without a license (Google has no public flights API since the 2018 QPX shutdown — see fast-flights' README rationale), so license risk is equal. Everything else favours `fli`: it is an order of magnitude more actively maintained (last commit `2026-05-24`, 2,667 stars, 160 commits by the lead maintainer, 11 open issues, MIT) versus fast-flights (last commit `2026-02-16`, 1,089 stars, 69 commits by one maintainer, 19 open issues, MIT, v3.0rc1 release candidate). `fli` hits Google's `FlightsFrontendService` POST endpoints directly via `curl_cffi` with a Pydantic-typed filter model, built-in token-bucket rate limiting (10 req/s shared across threads), tenacity-backed retries, typed exceptions, and a richer per-fare data model that includes per-leg flight numbers, layovers, CO2 emissions, amenities, aircraft type, and a follow-up `get_booking_options()` call that returns vendor-by-vendor fare URLs. fast-flights v3.0rc1 fetches `flights.google.com` HTML via `primp` with a chrome impersonation and pulls JSON out of an inline `<script class="ds:1">` tag using positional indices like `single_flight[20]` — fragile to UI changes, dataclass-based (not Pydantic), and has no rate limiter, no retries, no typed errors.

The single most decisive factor is **maintenance velocity in the face of Google schema drift**: this scraper class breaks every time Google ships a UI change. `fli` shipped a documented filter-shape fix as recently as May 2026 (see [`fli/models/google_flights/flights.py`](https://github.com/punitarani/fli/blob/main/fli/models/google_flights/flights.py) inline comment `"verified May 2026 by diffing the browser's POST body"`), has typed `SearchParseError` distinguishing "Google responded but shape changed" from network errors, and surfaces per-row failure samples. fast-flights' last fix was three months earlier and its `parse_js` still contains a stray `print(data)` ([`fast_flights/parser.py` line 32 on `dev`](https://github.com/AWeirdDev/flights/blob/dev/fast_flights/parser.py#L32)) — a tell that the parser isn't being driven by tests. Migration is straightforward because the Trip Planner already isolates the dependency behind `app/sources/fast_flights_source.py` and the `FareSource` Protocol; swapping in an `FliSource` is a single-file change.

---

## 1. Project health

| Metric | `fli` (punitarani/fli) | `fast-flights` upstream (AWeirdDev/flights) | Trip Planner's fork (thoughtpunch/flights) |
|---|---|---|---|
| Stars | **2,667** | 1,089 | 0 |
| Forks | 300 | 171 | n/a |
| Created | 2025-01-06 | 2024-05-12 | 2026-05-24 |
| Last push | **2026-05-24** | 2026-02-16 | 2026-05-25 |
| Default branch | `main` | `dev` | `dev` (inherits) |
| Open issues (non-PR) | **11** | 19 | — |
| Closed issues | 23 | 33 | — |
| Top contributor commits | 160 (punitarani) | 69 (AWeirdDev) | — |
| Distinct non-bot contributors | 10+ | 10 | — |
| License | MIT | MIT | MIT |
| Version | `flights` v0.10.0 on PyPI | `fast-flights` v3.0rc1 (release candidate) | fork of v3.0rc1 |

`fli` recent commits (top of `main` as of 2026-05-25):
- `4942911` `docs: add TypeScript docs/examples and reorganize by language (#186)` (2026-05-24)
- `e2063b9` `refactor: move demo media from data/ to docs/assets/ (#184)` (2026-05-24)
- `88d9d1d` `fix(ci): stop double npm publish on bot releases (TLOG 409) (#187)` (2026-05-24)

`fast-flights` recent commits (top of `dev`):
- `0138641` `fixed emoji name` (2026-02-16)
- `360c740` `fixed deps` (2026-02-16)
- `adfbc63` `fixed typing and shit` (2026-02-16)

**Maintainer signal**: `fli` shows a sustained author cadence with PR numbers in the high 180s, dependabot, a `docs/`, `mcp/`, and a TypeScript port being actively reorganised. `fast-flights` has one human maintainer who states in the README: _"really, i cant finish reading all of them, i have other projects and life to do. really sorry"_ — explicitly signalling low maintenance bandwidth.

> Subscriber count (active watchers) is 8 for both, so the on-paper "audience" parity does not match the actual development cadence.

---

## 2. Scraping vs API approach

### `fli`
Posts directly to Google's internal RPC-style endpoints:
- `https://www.google.com/_/FlightsFrontendUi/data/travel.frontend.flights.FlightsFrontendService/GetShoppingResults`
- `.../GetBookingResults`
- `.../GetCalendarGraph` (date search)

(`fli/search/flights.py` `BASE_URL` / `BOOKING_URL`, `fli/search/dates.py` `BASE_URL`.)

Filters are URL-form-encoded as `f.req=<urlencoded JSON>`. The JSON shape is reverse-engineered from the browser's own POST body — `fli/models/google_flights/flights.py` `FlightSearchFilters.format()` documents each slot of the wrapper array with comments like:

```python
# Segment classifier: 3 for outbound (or only leg), 1 for return.
# Empirically Google's `GetShoppingResults` accepts a uniform `3`
# for both segments without errors, but `GetBookingResults`
# rejects the request with INVALID_ARGUMENT unless the classifier
# matches the UI's pattern (verified May 2026 by diffing the
# browser's POST body against our own).
```

Responses are framed in Google's `)]}'` + `wrb.fr` chunked envelope; `fli/search/_wire.py` (`parse_first_wrb_payload`, `iter_wrb_chunks`) decodes the frames, then `fli/search/_decoders.py` (`parse_flight_row`, `parse_booking_chunk`) walks positional indices into Pydantic models. No HTML parsing, no headless browser, no protobuf wire format on the response side — the response is JSON nested arrays.

### `fast-flights`
v3.0rc1 fetches the public HTML page:

```python
URL = "https://www.google.com/travel/flights"
client = Client(impersonate="chrome_145", impersonate_os="macos", ...)  # primp
res = client.get(URL, params=params)
return res.text
```

(`fast_flights/fetcher.py`.)

The **request side** is protobuf: query filters are built as protobuf messages (`fast_flights/pb/flights_pb2`), serialised, base64-encoded, and passed as the `tfs=` URL parameter (`fast_flights/querying.py` `Query.to_str()` / `Query.url()`).

The **response side** is HTML scraping. `fast_flights/parser.py` parses the page with `selectolax.lexbor`, finds an inline `<script class="ds:1">` tag, strips `data:` prefix / trailing comma, `json.loads()` the result, then walks fixed positional indices:

```python
script = parser.css_first(r"script.ds\:1")
...
for single_flight in flight[2]:
    from_airport = Airport(code=single_flight[3], name=single_flight[4])
    departure_time = single_flight[8]
    ...
    plane_type = single_flight[17]
    duration = single_flight[11]
```

A stray `print(data)` lives on line 32 of `parse_js` on `dev` — visible side-effect output every call. The README admits: _"I have no idea what I wrote but... it worked!"_

There is an optional **Playwright** integration (`fast_flights[local]` extra) and a **BrightData** integration (`fast_flights.integrations.BrightData`) for when the direct fetch is blocked.

---

## 3. Data model per fare offer

### `fli.models.FlightResult` (Pydantic `BaseModel`)
Per-offer fields:
- `legs: list[FlightLeg]` — per-leg `airline`, `flight_number`, `departure_airport`, `arrival_airport`, `departure_datetime`, `arrival_datetime`, `duration`, plus optional `operating_airline`, `operating_flight_number`, `aircraft`, `legroom`, `legroom_short`, `amenities` (wifi/power/usb/video/legroom rating), `overnight`, `co2_emissions_g`.
- `price: NonNegativeFloat | None` (None when Google doesn't surface a price; convenience property `price_unknown`)
- `currency: str | None`
- `duration: PositiveInt` (minutes, total)
- `stops: NonNegativeInt`
- `layovers: list[Layover] | None` (airport, duration, overnight, change_of_airport, city, airport_name)
- `co2_emissions_g`, `co2_emissions_typical_g`, `co2_emissions_delta_pct`, `emissions_tag` ("lower"/"typical"/"higher")
- `self_transfer: bool | None`, `mixed_cabin: bool | None`
- `primary_airline: Airline | None`, `primary_airline_name: str | None`
- `booking_token: str | None`

Plus a separate `BookingOption` model returned from `get_booking_options()` containing `vendor_name`, `is_airline_direct`, `price`, `currency`, `fare_name`, `booking_url`, `google_click_url`.

### `fast_flights.model.Flights` (`@dataclass`)
Per-offer fields:
- `type: str | Literal["multi"]` (e.g. "non-stop" or "multi")
- `price: int` (note: int — fractional currency lost)
- `airlines: list[str]`
- `flights: list[SingleFlight]` — per-segment `from_airport`, `to_airport`, `departure` (date+time tuples), `arrival`, `duration` (int minutes), `plane_type`
- `carbon: CarbonEmission` (`emission`, `typical_on_route` in grams)

**Missing from fast-flights vs fli**: flight number, operating airline, aircraft (only `plane_type` string), layover details (you infer stops from segment count), amenities, legroom, currency string per row (you set it implicitly via the `currency` URL param), booking URL / vendor list, per-row `booking_token`. fast-flights has no equivalent to `get_booking_options()`.

**Note re Trip Planner contract:** the real attributes used by `app/sources/fast_flights_source.py` are `Flights.price`, `Flights.airlines`, `Flights.flights`, `SingleFlight.from_airport`, `SingleFlight.to_airport`, `SingleFlight.duration`, `Airport.code`. `get_flights()` returns a `MetaList(list[Flights])`.

---

## 4. Reliability under Google schema changes

### `fli`
- Typed `SearchParseError` (in `fli/search/flights.py`) raised when the inner shopping response array doesn't have flights at `inner[2]` or `inner[3]`.
- Per-row parse failures collected as samples; if **every** row fails to parse, raises `SearchParseError` with up to 3 distinct failure reasons — explicitly distinguished from network errors.
- Inline comments in `flights.py` literally version-stamp empirical discoveries (e.g. `"Empirically discovered May 2026"`, `"verified May 2026"`).
- HTTP errors are mapped to typed `SearchClientError` / `SearchTimeoutError` / `SearchConnectionError` / `SearchHTTPError` in `fli/search/client.py`.
- Active issue tracker shows the maintainer hunting these (closed `claude/investigate-issue-144` / `claude/investigate-issue-146` branches).

### `fast-flights`
- One generic exception class: `FlightsError` from `fast_flights.parser`. The Trip Planner adapter catches it (`app/sources/fast_flights_source.py:11,56`) but a schema drift typically surfaces as `AttributeError` / `IndexError` / `KeyError` on the positional access, not as `FlightsError`, so most breakages fall through to the bare `except Exception` clause.
- No version-stamped notes about empirical discoveries in source.
- Open issue #146 (`Bug when rail routes are returned - crashes`, 2026-05-08) is exactly this category: a row with a different shape crashes the parser. The issue is unfixed.
- v3.0rc1 has been "release candidate" since 2026-02-16 with no further releases.

---

## 5. Passenger / cabin / multi-city / round-trip support

| Capability | `fli` | `fast-flights` |
|---|---|---|
| Adults | `PassengerInfo.adults` | `Passengers(adults=…)` |
| Children | `children` | `children` |
| Infants in seat | `infants_in_seat` | `infants_in_seat` |
| Infants on lap | `infants_on_lap` | `infants_on_lap` (asserted ≤ adults) |
| Max passengers | not enforced in model (Google's UI cap is 9) | hard `assert sum ≤ 9` |
| Cabin | `SeatType.ECONOMY/PREMIUM_ECONOMY/BUSINESS/FIRST` | `seat="economy"/"premium-economy"/"business"/"first"` |
| One-way | `TripType.ONE_WAY` | `trip="one-way"` |
| Round-trip | `TripType.ROUND_TRIP` (with `top_n` outbound expansion) | `trip="round-trip"` |
| Multi-city | `TripType.MULTI_CITY` + multiple `FlightSegment` | `trip="multi-city"` + multiple `FlightQuery` |
| Stops | `MaxStops.ANY/NON_STOP/ONE_STOP_OR_FEWER/TWO_OR_FEWER_STOPS` | `max_stops: int | None` on each `FlightQuery` |
| Airline include / exclude | yes (`airlines`, `airlines_exclude`) | include only (`FlightQuery.airlines`) |
| Alliance include / exclude | yes (`ONEWORLD`, `SKYTEAM`, `STAR_ALLIANCE`) | no |
| Layover restrictions | `LayoverRestrictions` (airports, min/max duration) | no |
| Max duration | `max_duration` minutes | no |
| Time-of-day window | `TimeRestrictions` per segment | no |
| Price ceiling | `PriceLimit` | no |
| Bags filter (price includes bags) | yes (`BagsFilter`) | no |
| Less-emissions filter | `EmissionsFilter.LESS` | no |
| Sort order | `SortBy.BEST/CHEAPEST/DURATION/DEPARTURE_TIME/ARRIVAL_TIME/EMISSIONS/TOP_FLIGHTS` | no |
| Booking URL fetch | `SearchFlights.get_booking_options()` | no |
| Date-range "cheapest date" search | `SearchDates` | no |

For the Trip Planner's contract (one-way / round-trip economy, 1–6 passengers), both libraries cover the basics; everything else in this table is `fli`-only.

---

## 6. Rate limiting and caching

### `fli` — has both
- `fli/search/client.py` documents and enforces "10 requests per second, *globally* across threads" via `TokenBucketRateLimiter` (`fli/search/_concurrency.py`), with `DEFAULT_CALLS_PER_SECOND = 10`.
- Per-thread `curl_cffi` sessions guarded by `threading.local` because libcurl handles aren't thread-safe.
- Retries: `@retry(stop=stop_after_attempt(3), wait=wait_exponential(), reraise=True)` via `tenacity` on `get` and `post`.
- Configurable timeout via `FLI_TIMEOUT` env var (default 60s).
- Singleton client via `get_client()` with double-checked locking to avoid two `Client` instances doubling the rate budget.
- No response caching baked in.

### `fast-flights` — has neither
- Constructs a fresh `primp.Client` on every `fetch_flights_html` call.
- No retries (relies on `primp`'s defaults).
- No rate limiting.
- No caching.

For the Trip Planner's "shotgun fan-out" of date-range queries, `fli`'s built-in 10-req/s budget removes one whole concern; with fast-flights the orchestrator must add its own throttle.

---

## 7. Type safety / Pydantic friendliness

### `fli`
- Pydantic v2 (`pydantic>=2.10.4`). Every search/filter/result model is a `BaseModel`.
- `pydantic.NonNegativeInt`, `NonNegativeFloat`, `PositiveInt` constraints throughout.
- `field_validator` / `model_validator` enforce e.g. "travel date not in the past", "departure airport ≠ arrival airport", earliest-vs-latest time normalisation.
- Enums for `SeatType`, `TripType`, `MaxStops`, `SortBy`, `EmissionsFilter`, `Alliance`, `Currency` (40+ ISO codes).
- Typed exceptions (`SearchClientError`, `SearchHTTPError`, `SearchTimeoutError`, `SearchConnectionError`, `SearchParseError`).

### `fast-flights`
- Plain `@dataclass`. No validation, no constraints.
- `price` is `int` — would silently truncate fractional currency.
- One untyped catch-all `FlightsError`.
- Ships `fast_flights/py.typed` so static type checkers see the dataclasses.

For a Pydantic-first codebase (Trip Planner uses Pydantic in `app/schemas.py` and the `port-models-to-pydantic-with-alembic` change), `fli` drops in without an adapter layer; fast-flights output has to be hand-converted.

---

## 8. License compatibility

Both libraries are **MIT**. For a private, single-user Trip Planner the MIT terms (preserve copyright notice) are trivial. License compatibility is a wash.

The actually-load-bearing legal question is Google's terms of service for `flights.google.com`: scraping or hitting internal RPC endpoints without permission is plausibly a ToS violation regardless of which library you use, and neither library's MIT license shields the user from that. This is identical risk for both.

---

## 9. Migration path FROM fast-flights TO fli

The Trip Planner already isolates the dependency cleanly:

- `app/sources/base.py` defines `FareSource` Protocol with `name: Source` + `search(query: FareQuery) -> list[FareOffer]`.
- `app/sources/fast_flights_source.py` is the only file that imports `fast_flights`.
- The orchestrator/router calls `FareSource.search()`, not anything fast-flights-specific.

A migration is a single new file `app/sources/fli_source.py` plus an `enum.Source.FLI` member. Sketch:

```python
from fli.models import (
    FlightSearchFilters, FlightSegment, PassengerInfo,
    SeatType, TripType, MaxStops,
)
from fli.models.airport import Airport
from fli.search import SearchFlights, SearchClientError

class FliSource:
    name = Source.FLI

    def __init__(self, currency: str = "USD") -> None:
        self.currency = currency
        self._client = SearchFlights()

    def search(self, query: FareQuery) -> list[FareOffer]:
        segments = [FlightSegment(
            departure_airport=[[Airport[query.origin], 0]],
            arrival_airport=[[Airport[query.destination], 0]],
            travel_date=query.date,
        )]
        if query.is_round_trip:
            segments.append(FlightSegment(
                departure_airport=[[Airport[query.destination], 0]],
                arrival_airport=[[Airport[query.origin], 0]],
                travel_date=query.return_date,
            ))
        filters = FlightSearchFilters(
            trip_type=TripType.ROUND_TRIP if query.is_round_trip else TripType.ONE_WAY,
            passenger_info=PassengerInfo(
                adults=query.adults,
                children=query.children,
                infants_in_seat=query.infants_in_seat,
                infants_on_lap=query.infants_on_lap,
            ),
            flight_segments=segments,
            seat_type=SeatType.ECONOMY,
        )
        try:
            results = self._client.search(filters, currency=self.currency)
        except SearchClientError as e:
            raise SourceError(f"fli transport error: {e}") from e
        if not results:
            return []
        # One-way: list[FlightResult]; round-trip / multi-city: list[tuple[FlightResult, ...]]
        ...
        return offers
```

Notes:
- `Airport[query.origin]` works because `fli.models.airport.Airport` is an `Enum` indexed by IATA code.
- One-way returns `list[FlightResult]`; round-trip / multi-city returns `list[tuple[FlightResult, ...]]` of `(outbound, return)` pairs. The adapter must branch on that shape.
- Total duration = `sum(leg.duration for leg in result.legs)`; stops = `result.stops` (already provided, no need to derive from segment count).
- The Trip Planner's "LEAD" classification (per `design.md decision 1`) still applies — `fli` does not magically know the live bookable fare for a 6-pax party. Use `get_booking_options()` as the optional "promote to VERIFIED" step rather than as the headline search.

**Frictions:**
- The `FlightSegment.departure_airport` shape is awkward (`list[list[Airport | int]]`) — required by Google's underlying wire format. fast-flights' `FlightQuery(from_airport="MYJ", to_airport="TPE")` is more ergonomic but exposes none of the filter knobs.
- `fli` runs a `model_validator` that rejects travel dates in the past. Fine for the Trip Planner's forward-looking use, but pinned dates in unit tests must be future-dated.
- `fli`'s release on PyPI is the package **`flights`** (version `0.10.0`), not `fli`. The CLI script is named `fli`, but `pip install flights` is what you'd add to `pyproject.toml`. Having both installed concurrently during migration is fine because the import paths are different (`from fli ...` vs `from fast_flights ...`).

**Verdict on difficulty**: low — a few hundred lines of adapter code, one new test pinning `fli`'s contract analogous to `tests/test_fast_flights_contract.py`, and a feature flag in the router. The Trip Planner's clean port/adapter shape was designed exactly for this.

---

## Appendix: pinned PyPI / package facts

| | `fli` | `fast-flights` |
|---|---|---|
| PyPI package name | `flights` | `fast-flights` |
| Current version | 0.10.0 | 3.0rc1 |
| Python | `>=3.10` | `>=3.10` |
| Core runtime deps | `babel`, `curl-cffi`, `httpx`, `plotext`, `pydantic>=2.10.4`, `python-dotenv`, `ratelimit`, `tenacity`, `typer` | `primp`, `protobuf>=5.27.0`, `selectolax` |
| Optional extras | `[mcp]` (fastapi, fastmcp), `[all]` | `[local]` (playwright) |
| Includes a CLI | yes (`fli`) | no |
| Includes MCP server | yes (`fli-mcp`, `fli-mcp-http`) | no |

> "unverified" entries: `fli`'s explicit `py.typed` marker location, and whether either library has a published `urllib3` / `httpx` version constraint that would conflict with the Trip Planner's existing deps. Those are best-checked at integration time with `uv pip install --dry-run`.
