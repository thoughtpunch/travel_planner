# Trip Planner — Multi-Leg Flight Fare Orchestrator (MLFO)

Phase 1: Python backend + SQLite + minimal Jinja UI, no Vue yet.

What it does: sweeps a configurable **leg × gateway × date** matrix with the
`fast-flights` scraper, then re-queries the top N candidates per structure via
SerpAPI Google Flights **at full passenger count** to confirm the fare is
actually available for the party. Fares are classified `LEAD` vs `VALIDATED`,
and the budget verdict uses **validated fares only**.

It also prices two itinerary structures side-by-side:
- **A** — three one-ways (SJO → EU gateway → DC → SJO)
- **B** — nested envelope (SJO⇄DC outer round-trip + DC⇄EU inner round-trip)

…and reports which one wins empirically.

## Why the LEAD/VALIDATED split exists

`fast-flights` scrapes Google Flights' display fare. Google's display fare is
the cheapest fare in the lowest fare bucket, which **frequently is not
available for 6 seats**. Booking against a display fare is the dominant
failure mode for party-of-6 travel. Every scraper fare is therefore a `LEAD`,
and the validation pass re-queries SerpAPI at the configured passenger count
to confirm the fare exists for the whole party before it can be promoted to
`VALIDATED`. Budget verdicts ignore leads.

## Setup

Requires [mise](https://mise.jdx.dev) — it brings in pinned Python 3.12 and
uv automatically. `fast-flights` is pinned to the GitHub fork
(`thoughtpunch/flights`) in `pyproject.toml` so every install pulls the
current head.

```bash
cd trip_planner
cp .env.example .env          # add your SERPAPI_KEY
mise trust                    # one-time, approve mise.toml
mise run dev                  # installs deps, inits DB, seeds, starts server
```

That's it — http://127.0.0.1:8000.

### mise tasks

| Task           | What it does                                                |
|----------------|-------------------------------------------------------------|
| `mise run dev`   | Start dev server with auto-reload (idempotent first-run)   |
| `mise run setup` | Install + init DB + seed engagement configs                |
| `mise run test`  | Run the test suite (39 tests)                              |
| `mise run seed`  | (Re-)seed Structures A and B                               |
| `mise run quota` | Show SerpAPI monthly quota usage                           |
| `mise run run -- 1` | Execute a run for config #1, print top results synchronously |
| `mise run reset` | Delete the local SQLite DB                                 |
| `mise run clean` | Remove DB + venv + caches                                  |

If you'd rather skip mise: `uv sync --extra dev && uv run trip-planner serve`.

## CLI

```
trip-planner init           # create the SQLite DB
trip-planner seed           # seed the two engagement configs
trip-planner configs        # list configs
trip-planner quota          # SerpAPI quota status
trip-planner run <config>   # run synchronously, print top results
trip-planner serve          # start the FastAPI server
```

## HTTP API

| Method | Path                                | Purpose                            |
|--------|-------------------------------------|------------------------------------|
| GET    | `/api/configs`                      | List configs                       |
| POST   | `/api/configs`                      | Create config                      |
| GET    | `/api/configs/{id}`                 | Get config                         |
| PUT    | `/api/configs/{id}`                 | Replace config                     |
| DELETE | `/api/configs/{id}`                 | Delete config                      |
| POST   | `/api/runs?config_id={id}`          | Trigger an async run               |
| GET    | `/api/runs`                         | List runs                          |
| GET    | `/api/runs/{id}`                    | Run status                         |
| GET    | `/api/runs/{id}/results`            | Ranked itineraries + verdict       |
| GET    | `/api/runs/estimate/{config_id}`    | Pre-run SerpAPI call estimate      |
| GET    | `/api/quota`                        | Monthly SerpAPI usage              |

The SerpAPI key is **server-side only**; it never appears in responses or in
the frontend.

## Configuration (`.env`)

| Var                          | Default                          | Notes                                  |
|------------------------------|----------------------------------|----------------------------------------|
| `SERPAPI_KEY`                | (empty)                          | Without this, validation is skipped    |
| `SERPAPI_MONTHLY_CEILING`    | 240                              | Hard cap; calls above this `SKIPPED_QUOTA` |
| `DATABASE_URL`               | `sqlite:///./trip_planner.db`    |                                        |
| `DEFAULT_CURRENCY`           | `USD`                            |                                        |
| `FARE_TTL_SECONDS`           | 86400                            | After this, VALIDATED → STALE         |
| `VALIDATION_TOLERANCE_PCT`   | 15                               | Validated-vs-lead price tolerance      |
| `VALIDATION_TOP_N`           | 5                                | Per structure                          |
| `ENVELOPE_LONG_GAP_DAYS`     | 30                               | Beyond this, inner RT gets LONG_GAP   |

## Failure modes the design defends against

1. **Reporting a lead as bookable** → `LEAD` / `VALIDATED` separation; budget
   verdict uses validated only.
2. **6-seat collapse** → mandatory validation pass at full party.
3. **Scraper outage producing silent wrong answers** → empty/exception →
   SerpAPI fallback; empty is NEVER recorded as confirmed "no flights".
4. **SerpAPI bill surprise** → quota tracker + hard ceiling + pre-run
   estimate.
5. **Stale prices presented as current** → `fetched_at` + TTL + `STALE`
   downgrade.
6. **Envelope assumed cheaper without evidence** → both structures priced;
   `LONG_GAP` flag when the inner round-trip exceeds the configured gap.

## Out of scope (Phase 1)

Booking, payment, seat maps, award/points, hotels, train ticketing, Vue UI.
The Vue 3 + PrimeVue SPA is Phase 2.

## Tests

```bash
uv run pytest -v
```

The `fast_flights` contract test pins the v3.0rc1 schema attributes the
adapter relies on. If the upstream fork's data model drifts, that test fails
loudly rather than producing silent wrong fares downstream.
