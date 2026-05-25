# Gateway transfers table

Source of truth for ground-transfer cost / duration / viability from European
gateways to Venice. Lives at `app/data/gateway_transfers.py` (Python because
the orchestrator reads it; copy-pasteable to spreadsheet on demand).

## Why a hardcoded table, not a scraper

`landed-cost-model` Decision 5: rail and ferry fares between European
gateways and Venice are stable on the planning horizon (months). Scraping
them is a second adversarial-website rabbit hole (we just landed
`migrate-fare-search-to-fli` precisely because scraper maintenance is a
known pain). A reviewed table with `last_reviewed` dates that surface in
the UI is the better tradeoff.

## Maintainer commitment

**Quarterly review.** Every entry's `last_reviewed` field SHOULD be no
older than 180 days. The unit test in `tests/test_gateway_transfers.py`
emits a warning (not a failure) for any entry past that threshold, so
the review is visible in CI but does not block.

## How to update an entry

1. Open `app/data/gateway_transfers.py`.
2. Edit the relevant `TransferModel(...)` row.
3. Bump `last_reviewed=date(YYYY, MM, DD)` to today.
4. Add a `notes` change if the route changed (new bus operator, new ferry
   season, schedule change that moves `last_viable_onward_local_time`).
5. Run `mise run test` — the seeded-entry test will flag missing fields.

## How `last_viable_onward_local_time` works

This is the local arrival cutoff AT the gateway, after which there is no
viable same-day onward transfer to Venice. The orchestrator derives
`forces_overnight = true` per itinerary when the itinerary's actual
arrival time is past this cutoff; when true, one night of stopover
lodging is added to landed cost.

It is per-mode. If a gateway has both rail and ferry, the runner picks
the cheapest viable mode given the arrival time — if rail's cutoff has
passed and ferry's hasn't, ferry wins even if it's pricier.

## Fields

| Field | Notes |
|---|---|
| `gateway` | IATA code |
| `mode` | `rail` \| `ferry` \| `bus` \| `drive` |
| `per_person_cost` | Whole currency units (USD by default) |
| `duration_minutes` | Door-to-Venezia Santa Lucia |
| `transfers` | Train-to-train (or bus-to-train) changes; 0 = direct |
| `last_viable_onward_local_time` | After this local arrival time, no same-day onward; itinerary's `forces_overnight` flips true |
| `last_reviewed` | ISO date the entry was last verified |
| `notes` | Free-form route detail |
| `arrival_airports` | When set, transfer applies only to itineraries arriving at one of these airports (currently unused; for future "MXP-only / LIN-only" splits) |

## Currency

Whole USD by default. EUR rough-converted at parity for the spine. Users
who want a different conversion can supply per-config
`cost_assumptions.transfer_overrides` to override individual entries
without editing the table.
