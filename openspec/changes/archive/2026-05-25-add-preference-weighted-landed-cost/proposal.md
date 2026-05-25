## Why

The orchestrator today ranks by validated party **airfare**. That is the wrong objective for a system whose user does not care about fare — they care about the **total landed cost of arriving at the true destination (Venice)**, where airfare is one term among several. A $1,200 fare straight to Venice can beat a $900 fare to Rome once the Rome option's 6-person rail transfer, possible forced overnight, and luggage handling are added in. Today's product would silently recommend the wrong option.

There are also no preferences in the loop. The user's tolerance for a long ground transfer, a long layover, a plane change, a red-eye, or a 24-hour stopover is *not* a constant the system can guess. And for stopovers specifically the preference is genuinely bidirectional — the same feature is a disqualifier for one traveler and a desired rest-break for another. Pretending the system can intuit this is what produces the "the algorithm picked something useless" failure mode of consumer fare comparators.

The reframe this change makes is twofold:

1. **Cost is the honest spine** — landed cost (airfare + ground transfer + any forced lodging) is computed completely and visibly *before* any reordering, and preferences NEVER mutate cost.
2. **Preferences bend the ranking around the spine**, expressed on a single bookended scale (HARD NO → soft middle → HARD YES) where the two ends are categorically different operations: HARD NO filters; HARD YES *constructs the desired itinerary structure and prices it*.

This is the difference between a fare-comparison tool and an **LLM-orchestrated trip planner**. We are not rebuilding Kayak or Kiwi. The competitive surface is not "show every airline a tenth of a cent cheaper"; it is "be honest about what arriving costs and what the user actually wants, and let the user adjudicate the money-vs-friction tradeoff against numbers they can trust." An LLM is a copilot for elicitation and assumption pre-fill, *never* a cost generator.

## What Changes

Three new capabilities and two modified capabilities, all hanging off the existing fare-search / fare-validation / itinerary-orchestration spine.

**New capabilities:**
- **`landed-cost-model`** — extends itinerary cost beyond airfare to include ground transfer to the true destination and stopover lodging, with explicit, user-owned, labeled assumptions and a per-gateway transfer table.
- **`preference-elicitation`** — a single bookended preference scale per friction axis with global defaults and per-leg overrides; defines the v1 axis set (transfer length, layover length, stopover, plane changes, red-eye / arrival time-of-day).
- **`preference-scoring`** — applies preferences to reorder the honestly-priced result set; encodes the HARD NO → filter / HARD YES → construct duality; enforces the "scoring never mutates cost" invariant.

**Modified capabilities:**
- **`itinerary-orchestration`** — ranking switches from airfare to validated landed cost; orchestration matrix gains stopover-leg construction; ranking is followed by preference-scoring reordering.
- **`search-config`** — config schema gains a `preferences` block (global defaults + per-leg overrides) and a `cost_assumptions` block (per-night lodging estimate, optional last-mile transfer override) that snapshots into each run.

**Non-goals (explicitly out of scope for this change):**
- Live hotel or rail pricing. Ground transfer is a hardcoded per-gateway table for v1; lodging is a user-owned per-night assumption.
- Booking. We rank; we don't transact.
- Dollarizing friction. We never multiply "minutes of layover" by a fabricated misery-to-money rate. Friction is preference; cost is dollars; the user adjudicates.
- A blended single "score" column. Cost and friction stay individually visible.
- An LLM that fills in cost numbers without labeling them as unverified estimates. (This is a *forbidden* pattern, not just out of scope — see `landed-cost-model` Requirement: Cost components are honest, explicit, and user-overridable.)

The UI work that surfaces these concepts in a Vue 3 + PrimeVue SPA — the wizard for elicitation, the results view that shows the cost spine alongside friction columns, the HARD YES stopover prompt — is scoped into a companion change **`add-primevue-trip-wizard`**, which depends on this one's contracts.

## Impact

- **Affected specs:**
  - NEW `landed-cost-model` (4 requirements)
  - NEW `preference-elicitation` (5 requirements)
  - NEW `preference-scoring` (4 requirements)
  - MOD `itinerary-orchestration` (Ranking requirement rewritten; new "Preference-driven stopover construction" requirement)
  - MOD `search-config` (config schema gains preferences + cost_assumptions)
- **Affected code:**
  - `app/models.py` (or its successor under the Pydantic/Alembic port) — `Config.preferences`, `Config.cost_assumptions`, `Itinerary.landed_cost`, `Itinerary.cost_breakdown`, `Itinerary.friction_attributes`, `Run.config_snapshot` enriched.
  - `app/orchestrator/runner.py` — call the landed-cost calculator and preference scorer *after* validation, *before* persistence of ranks.
  - NEW `app/orchestrator/landed_cost.py` — pure function: `(itinerary, gateway_transfer_table, cost_assumptions) → LandedCost(total, components)`.
  - NEW `app/orchestrator/preferences.py` — pure scorer over the validated, landed-cost-priced set: `(candidates, preferences) → (filtered_and_reordered, applied_explanations)`.
  - NEW `app/orchestrator/stopover.py` — leg-injection module for HARD YES stopover: takes a base structure and a named/sweep-set stopover, returns expanded queries.
  - NEW `app/data/gateway_transfers.py` — hardcoded table seeded for `{VCE, MXP, LIN, ZRH, MUC, BLQ, VRN, TRS, FCO}` → Venice (rail + ferry where real), each with `last_reviewed`.
  - `app/api/runs.py` — results payload exposes `landed_cost`, `cost_breakdown`, `friction_attributes`, `preference_explanations`.
- **Affected tests:** new test files for landed-cost calculator, preference scorer (parametrised over the bookended scale), stopover constructor, and an end-to-end runner test that produces a landed-cost-ranked result set with preferences applied.
- **SerpAPI quota cost:** unchanged for v1. Stopover construction adds one extra fare query per stopover leg per sampled date, which the user has opted into by setting HARD YES.
- **Depends on:** the in-flight `port-models-to-pydantic-with-alembic` change (which gives us a clean place to land the new `Config.preferences` and `Itinerary.landed_cost` columns) and the just-archived `migrate-fare-search-to-fli` (the richer `fli` per-fare data feeds friction attributes like `red_eye`, `plane_changes`, `layover_minutes` directly without re-scraping).
- **Blocks:** `add-primevue-trip-wizard` (the UI change has nothing to render without these contracts).
- **Phase:** Phase 2 of the project. This is the change that makes the orchestrator useful as a *trip* planner rather than a fare report.
