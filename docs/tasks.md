# Tasks: Multi-Leg Flight Fare Orchestrator

## 1. Project scaffold
- [x] 1.1 Python project (FastAPI, SQLite via SQLModel/SQLAlchemy, fast-flights, serpapi client)
- [ ] 1.2 Vue 3 + PrimeVue frontend scaffold — **Phase 2 — deferred** (Phase-1 ships a Jinja UI; see `openspec/specs/web-ui/spec.md`)
- [x] 1.3 Config for secrets (SerpAPI key) loaded server-side from env only

## 2. fare-search
- [x] 2.1 fast-flights adapter + contract test (fail loudly on schema drift)
- [x] 2.2 SerpAPI Google Flights adapter
- [x] 2.3 Source router: scraper-first, fallback on empty/exception/timeout
- [x] 2.4 SerpAPI quota tracker + hard ceiling + SKIPPED_QUOTA path
- [x] 2.5 All fares tagged source + verification_status + fetched_at + ttl

## 3. itinerary-orchestration
- [x] 3.1 Matrix expansion (gateway × sampled date) per leg
- [x] 3.2 Structure A (three one-ways) assembly
- [x] 3.3 Structure B (nested envelope) assembly + long-gap flag
- [x] 3.4 Blackout date flagging (Thanksgiving weekend)
- [x] 3.5 Gateway train-to-Venice metadata table + door-to-door ranking
- [x] 3.6 Ranking with status separation

## 4. fare-validation
- [x] 4.1 Top-N validation queue per structure
- [x] 4.2 Re-query at full passenger count via SerpAPI; tolerance check
- [x] 4.3 VALIDATED / VALIDATION_FAILED transitions + candidate promotion
- [x] 4.4 Budget verdict from VALIDATED fares only
- [x] 4.5 TTL/STALE handling

## 5. search-config + persistence
- [x] 5.1 SQLite schema + migrations
- [x] 5.2 Config CRUD with validation (no past dates, non-empty gateways)
- [x] 5.3 Run records + config snapshot + run history

## 6. web-api
- [x] 6.1 Config CRUD endpoints
- [x] 6.2 Run trigger (async) + status polling
- [x] 6.3 Results retrieval with flags/status
- [x] 6.4 Quota status endpoint; assert no secrets in any payload

## 7. web-ui — **Phase 2 — deferred**
Phase-1 Jinja UI is the shipped truth — see `openspec/specs/web-ui/spec.md`.
The Vue 3 + PrimeVue items below describe Phase-2 work and remain unchecked.

- [ ] 7.1 Config editor (legs, gateways, dates, passengers, budget, blackouts, structures)
- [ ] 7.2 Run trigger with pre-run SerpAPI call estimate + remaining quota
- [ ] 7.3 Results view: status colors, budget verdict (validated-only), A-vs-B compare
- [ ] 7.4 Run history view

## 8. Seed for this engagement
- [x] 8.1 Preload config: SJO origin; gateways {VCE,MXP,LIN,ZRH,MUC,BLQ};
      Leg2 {VCE,MXP,BLQ,FCO}→{IAD,DCA,BWI}; Leg3 {IAD,DCA,BWI}→SJO;
      6 adults; $6000 ceiling; Thanksgiving blackout; price A and B
