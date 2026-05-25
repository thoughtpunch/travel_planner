# Design: Multi-Leg Flight Fare Orchestrator

## Context

Greenfield. Python backend (FastAPI + SQLite), Vue 3 / PrimeVue frontend.
Primary fare source `fast-flights` (Google Flights scraper), fallback SerpAPI
Google Flights. Single-user, runs locally or on a small VPS. Cash fares only;
no booking.

## Key decisions

### Decision 1: Scraper fares are LEADs, never bookable truth
`fast-flights` decodes Google Flights' Base64/Protobuf `tfs` param and scrapes
the results page. It returns **display fares** and does not confirm availability
at passenger count. For a party of 6 this is the dominant failure mode. Every
scraper fare is therefore a LEAD; budget verdicts use VALIDATED fares only.
This is the central architectural constraint, not an edge case.

### Decision 2: SerpAPI is co-primary, not a rare fallback
`fast-flights` is a solo-maintained v3 release candidate that breaks when Google
changes its internal schema (documented in the repo's issues). Treat scraper
breakage as expected. The validation pass routes through SerpAPI regardless of
scraper health, so the system degrades to "slower + costs SerpAPI quota" rather
than "produces wrong answers" when the scraper is down.

### Decision 3: Two-phase search (sweep → validate)
Phase 1 sweeps cheaply (scraper-first) to find candidates. Phase 2 validates
only the top N per structure via SerpAPI at full passenger count. This bounds
SerpAPI spend while keeping the final numbers trustworthy. Lean preset targets
~120–150 SerpAPI calls/run (≈ one cheap paid month); full sweep is configurable.

### Decision 4: Price both structures, let data decide
The user's prior "nested envelope" win is one data point under different
conditions (shorter gap). For an 8-week stay the long inner-RT gap likely erodes
the round-trip advantage, and forcing the Sept transatlantic through DC adds a
routing tax. The system prices A and B and reports the winner empirically rather
than assuming either.

## Data model (SQLite)

> Phase-1 seed creates one Config per structure (A and B as separate configs) so each leg's RT-vs-OW semantics stay unambiguous per run; see `app/seed.py`.

```
config(id, name, budget_party_total, passengers_json, structures_json,
       blackout_ranges_json, created_at, updated_at)

leg(id, config_id, ordinal, origin, gateways_json, date_anchor,
    window_days, sampling_strategy)

run(id, config_id, config_snapshot_json, status, started_at, finished_at,
    scraper_calls, serpapi_calls, serpapi_quota_remaining)

fare(id, run_id, leg_ordinal, structure, origin, destination, date,
     carrier, price, currency, stops, source, verification_status,
     fetched_at, ttl_seconds, flags_json)
     -- source: fast-flights | serpapi
     -- verification_status: LEAD | VALIDATED | VALIDATION_FAILED
     --                      | STALE | SKIPPED_QUOTA | FAILED
     -- flags: [BLACKOUT, LONG_GAP, ...]

itinerary(id, run_id, structure, total_party_price, currency,
          verification_status, fare_ids_json, gateway, train_to_venice_json,
          flags_json, rank)
```

## Failure modes the spec is built to prevent

1. **Reporting a lead as bookable** → LEAD/VALIDATED separation; budget verdict
   uses VALIDATED only.
2. **6-seat collapse** → mandatory validation pass at full passenger count.
3. **Scraper outage producing silent wrong answers** → empty/exception ⇒
   fallback; never recorded as authoritative "no flights".
4. **SerpAPI bill surprise** → quota tracking + pre-run estimate + hard ceiling.
5. **Stale prices presented as current** → TTL + STALE downgrade.
6. **Envelope assumed cheaper without evidence** → both structures priced;
   long-gap warning.

## Open questions for the user / Claude Code at build time

- SerpAPI tier: free (100/mo, one lean run) or paid (~$75/mo)? Determines
  whether full sweep is even runnable.
- Does `fast-flights` v3.0rc1's actual return shape match what the validation
  mapper expects? Must be verified against a live call at build time — the
  README is thin and the format is unstable. Build a thin adapter + contract
  test around it so a scraper schema change fails loudly, not silently.
- Train cost/duration data for gateways: hardcoded table (fine for 6 cities) or
  looked up? Recommend hardcoded for v1.

## Out of scope
Booking, payment, seat maps, award/points, hotels, train ticketing. Train data
is decision context only.
