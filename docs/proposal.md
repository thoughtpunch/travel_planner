# Change Proposal: Multi-Leg Flight Fare Orchestrator (MLFO)

## Status
Proposed

## Why

A family of 6 (all full-fare seats) needs to book a three-segment international
itinerary (SJO → Northern Italy gateway → Washington DC → SJO) for travel
Sept–Dec, with a hard per-person budget ceiling of $1,000 (USD 6,000 party
total). The booking problem has two properties that defeat manual searching:

1. **Combinatorial search space.** The optimal answer depends on date (±7 days
   per leg), gateway city (~6 European candidates reachable by ≤4hr train to
   Venice; 3 DC-area airports), and *itinerary structure* (three independent
   one-ways vs. a nested round-trip "envelope"). This is hundreds of
   permutations no human checks by hand.

2. **Display-fare vs. bookable-fare divergence at party size.** Google Flights'
   headline fare is the lowest-bucket price and frequently is NOT available for
   6 seats. A party-of-6 search systematically over-trusts display fares unless
   every candidate is re-validated at the true passenger count.

This system orchestrates the search, prices both itinerary structures, and —
most importantly — distinguishes *unverified leads* from *validated fares* so
the user never books against an optimistic number.

## What Changes

- NEW capability: `fare-search` — query flight fares from multiple sources with
  a primary scraper (`fast-flights`) and an authoritative fallback (SerpAPI
  Google Flights).
- NEW capability: `itinerary-orchestration` — sweep a configurable date ×
  gateway × structure matrix; rank results by validated party total.
- NEW capability: `fare-validation` — re-query candidate fares at true
  passenger count; mark fares `VALIDATED` vs `LEAD`.
- NEW capability: `search-config` — persist search definitions (legs, gateways,
  date windows, passenger mix, budget) in SQLite, editable via UI.
- NEW capability: `web-api` — FastAPI service exposing config CRUD, run
  triggering, and result retrieval over SQLite.
- NEW capability: `web-ui` — Vue 3 + PrimeVue SPA for configuring searches,
  running them, and reviewing ranked results. (Phase 2; Phase 1 ships a Jinja UI — see openspec/specs/web-ui/)

## Impact

- Affected specs: all new (greenfield project).
- Affected code: new repository. Python (FastAPI, SQLite, fast-flights,
  SerpAPI client) + Vue 3 / PrimeVue frontend.
- External dependencies & cost: SerpAPI account (paid tier likely required;
  free tier = 100 searches/mo). `fast-flights` is unmaintained-adjacent
  (solo maintainer, v3 release candidate) and WILL break periodically — the
  fallback is load-bearing, not optional.
- Out of scope (explicitly): booking/payment, seat selection, award/points
  redemption (cash fares only), hotels, trains (train legs are decision context
  only, not booked or priced by this system).
