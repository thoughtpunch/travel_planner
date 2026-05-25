## 1. Data model + config schema

- [x] 1.1 Extend `Config` (Pydantic model from `port-models-to-pydantic-with-alembic`) with `preferences: Preferences` and `cost_assumptions: CostAssumptions` blocks. Define both as Pydantic models with field-level validation per the `search-config` spec.
- [x] 1.2 Define `Preferences` model: `defaults: dict[Axis, AxisSetting]`, `per_leg_overrides: list[PerLegOverride]`, optional `stopover_target`. Add a `@model_validator` rejecting HARD YES on non-constructable axes and missing `stopover_target` when stopover is HARD YES.
- [x] 1.3 Define `CostAssumptions` model: `stopover_lodging_per_night`, `stopover_rooms` (default 2), `transfer_overrides`, `llm_suggested`. Reject negatives; require `stopover_lodging_per_night` when stopover is HARD YES.
- [x] 1.4 Extend `Itinerary` model with `landed_cost: int`, `cost_breakdown: CostBreakdown`, `friction_attributes: FrictionAttributes`, `preference_explanations: list[PreferenceExplanation]`.
- [x] 1.5 Alembic migration: add JSON columns for the new fields (or a new normalised table if `port-models-to-pydantic-with-alembic` lands a relational shape). Match its migration style.
- [x] 1.6 `Run.config_snapshot` must include the full preferences + cost_assumptions block AND the `last_reviewed` date of every gateway-transfer table entry consumed, so historical runs remain interpretable after the table is updated.

## 2. Ground-transfer table

- [x] 2.1 Create `app/data/gateway_transfers.py` exposing `GATEWAY_TRANSFERS: dict[str, list[TransferModel]]`. Each `TransferModel`: `mode`, `per_person_cost`, `duration_minutes`, `transfers`, `last_viable_onward_local_time`, `last_reviewed: date`, `notes`.
- [x] 2.2 Seed for `{VCE, MXP, LIN, BLQ, VRN, TRS, ZRH, MUC}` → Venice (rail; ferry for TRS where real). FCO optional.
- [x] 2.3 Unit test: every seeded entry has a `last_reviewed` date and a non-empty `notes` field. Static lint: assert `last_reviewed` is no older than 180 days (warning, not failure).
- [x] 2.4 Document the maintainer's quarterly-review commitment in `docs/gateway-transfers.md` (or extend existing transfer notes).

## 3. Landed-cost calculator

- [x] 3.1 Create `app/orchestrator/landed_cost.py` exposing a pure function `compute_landed_cost(itinerary: ItineraryCandidate, transfer_table, assumptions, party_size, rooms) -> LandedCost` where `LandedCost` carries `total`, `components: list[CostComponent]`, and per-component `data_source` (one of `validated_airfare | transfer_table | user_assumption | llm_estimate_unverified | user_override`).
- [x] 3.2 Derive `forces_overnight` per itinerary from arrival local time vs. the gateway's `last_viable_onward_local_time`. If true, add 1 night of lodging × rooms to landed cost.
- [x] 3.3 Apply per-config `transfer_overrides` from `CostAssumptions` if present, preserving the original table figure in the `CostComponent` for display.
- [x] 3.4 Test parity invariant: landed cost is deterministic; same inputs always produce same output. Property test over a fuzzed input space.
- [x] 3.5 Test: every component on every output has a non-empty `data_source` and is `user_overridable`. This is the integration-test side of `landed-cost-model`'s "Forbidden silent estimate" scenario.

## 4. Preference scorer

- [x] 4.1 Create `app/orchestrator/preferences.py` exposing `apply_preferences(candidates: list[ItineraryCandidate], preferences: Preferences, cheapest_validated_landed_cost: int) -> ScoredResult` where `ScoredResult` carries `ranked: list[ItineraryCandidate]`, `filtered_out: dict[Axis, int]`, and writes `preference_explanations` onto each ranked candidate.
- [x] 4.2 Implement HARD NO as a filter applied BEFORE soft scoring; record counts for each axis in `filtered_out`.
- [x] 4.3 Implement soft scoring as a bounded reorder within ±10% (configurable: `soft_band_pct`, default 10) of `cheapest_validated_landed_cost`. Outside the band, landed cost wins. Each soft preference axis contributes a bounded rank-delta with sign matching `desire`/`avoid`.
- [x] 4.4 Assert in code: this function never mutates a candidate's `landed_cost` or `cost_breakdown`. Add a debug assertion that compares pre/post fingerprints.
- [x] 4.5 Test the no-double-count rule: a HARD-YES-stopover itinerary's landed cost equals its honest landed cost regardless of preference setting; only its rank moves.
- [x] 4.6 Test the soft-band bound: an itinerary 15% above the cheapest cannot be promoted above the cheapest by any stack of soft-desire boosts.

## 5. Stopover constructor

- [x] 5.1 Create `app/orchestrator/stopover.py` exposing `construct_stopover_itineraries(base_structure, stopover_target, gap_nights=1) -> list[StopoverStructure]`. For a named city, returns one structure; for a sweep candidate set, returns one per candidate.
- [x] 5.2 Wire `construct_stopover_itineraries` into `runner.execute_run` BEFORE the sweep step, so constructed structures generate fare queries through the existing query-matrix expansion.
- [x] 5.3 Constructed structures price through the unchanged sweep / validate / landed-cost pipeline; no special-casing in those modules.
- [x] 5.4 Test: constructed stopovers respect HARD NO axes (e.g. HARD NO red-eye filters out a constructed SJO → MAD that arrives at 03:40 MAD local).
- [x] 5.5 Test: a sweep over `{MAD, LIS}` produces two constructed itineraries; each is priced; both rank against direct options on landed cost.

## 6. Runner pipeline integration

- [x] 6.1 In `app/orchestrator/runner.py`, change the pipeline order to: `(if HARD YES stopover) construct → sweep → validate → compute landed cost → filter (HARD NO) → score (soft middle) → rank → persist`.
- [x] 6.2 Replace the existing `rank_candidates(validated)` airfare ranking with the new landed-cost-then-preferences flow.
- [x] 6.3 Persist `landed_cost`, `cost_breakdown`, `friction_attributes`, `preference_explanations` on each `Itinerary` row. Persist `filtered_out_count` per axis on the `Run` row.
- [x] 6.4 The runner's existing `failed_query_count` / FAILED-fare persistence is unchanged; landed-cost computation is skipped for FAILED itineraries and they remain ranked separately.
- [x] 6.5 Integration test: end-to-end run with preferences `{stopover: hard_yes(MAD), layover_length: hard_no(>4h), red_eye: avoid}` produces a result set with (a) at least one constructed MAD stopover, (b) no >4h layover candidates, (c) red-eye candidates ranked below non-red-eye in the soft band.

## 7. API surface

- [x] 7.1 `POST /api/configs` accepts the extended schema (preferences + cost_assumptions). Validation errors return 422 with field paths matching the spec.
- [x] 7.2 `GET /api/runs/{id}/results` payload includes per-itinerary `landed_cost`, `cost_breakdown`, `friction_attributes`, `preference_explanations`, and run-level `filtered_out_count_by_axis`.
- [x] 7.3 `GET /api/configs/{id}/preview` returns a dry-run summary of how the matrix would expand under the current preferences (especially: how many stopover candidates would be constructed) so the user can sanity-check before committing the SerpAPI calls.

## 8. Spec sync + validate

- [x] 8.1 Sync the new + modified specs from `openspec/changes/add-preference-weighted-landed-cost/specs/` into `openspec/specs/`. New caps go to new directories; modified caps merge into existing spec files.
- [x] 8.2 `openspec validate add-preference-weighted-landed-cost --strict` clean.
- [x] 8.3 `openspec validate --all --strict` clean.
- [x] 8.4 `mise run test` clean.

## 9. Seed for this engagement

- [x] 9.1 Seed a Config "Venice family of 6" with: party of 6, true destination Venice, default preferences (avoid long layover, avoid red-eye, neutral on stopover), cost assumptions ($320/night, 2 rooms).
- [x] 9.2 Verify the seeded config runs end-to-end and produces landed-cost-ranked results that demonstrate the cheaper-fare-loses scenario from the `landed-cost-model` spec.
