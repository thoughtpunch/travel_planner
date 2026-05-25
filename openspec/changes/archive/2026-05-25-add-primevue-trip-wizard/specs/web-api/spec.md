## ADDED Requirements

### Requirement: Wizard state endpoints (idempotent PATCH)

The API SHALL expose endpoints for incremental wizard state persistence:

- `POST /api/configs` — create a draft config (returns `{id, status: "draft"}`).
- `GET /api/configs/{id}` — retrieve current config (drafts and persisted).
- `PATCH /api/configs/{id}` — idempotent partial update of any subset of fields. The body is a JSON-merge-patch; the response is the full updated config. The endpoint SHALL accept partial preferences and partial cost_assumptions (e.g. updating only one axis or one assumption field).
- `POST /api/configs/{id}/finalize` — promote a draft to a persisted config (validates the full schema; rejects incoherent preferences per `preference-elicitation`).
- `GET /api/configs/{id}/preview` — dry-run preview returning `{matrix_size, planned_serpapi_calls, constructed_stopover_count, would_filter_count_by_axis}` so the wizard's Review step can show the operator what the run will cost before commit.

#### Scenario: Debounced wizard PATCH

- **WHEN** the SPA debounces field changes and sends `PATCH /api/configs/{id}` with `{preferences: {defaults: {layover_length: "avoid"}}}`
- **THEN** the server merges only that field; other preferences and cost_assumptions are untouched
- **AND** the response is the full updated config so the client can reconcile

#### Scenario: Finalize rejects incoherent draft

- **WHEN** `POST /api/configs/{id}/finalize` is called on a draft with HARD YES on `layover_length`
- **THEN** the response is 422 with `{errors: [{path: "preferences.defaults.layover_length", code: "hard_yes_not_admitted", message: "..."}]}`

#### Scenario: Preview shows dry run

- **WHEN** `GET /api/configs/{id}/preview` is called
- **THEN** the response includes the planned SerpAPI call count, the constructed-stopover count (zero if no HARD YES stopover), and the per-axis would-filter counts so the operator can adjust before committing

### Requirement: Trip workspace endpoints

The API SHALL expose endpoints for trips, where a trip owns one config, many runs, one shortlist, and notes:

- `GET /api/trips` — list trips with summary (latest run cost-spine, age).
- `POST /api/trips` — create a trip (creates a draft config implicitly).
- `GET /api/trips/{id}` — full trip detail.
- `PATCH /api/trips/{id}` — update trip metadata (name, notes).
- `DELETE /api/trips/{id}` — soft-delete (recoverable for 7 days).
- `GET /api/trips/{id}/runs` — paginated run history for the trip.
- `GET /api/trips/{id}/shortlist` — saved itinerary snapshots.
- `POST /api/trips/{id}/shortlist` — save an itinerary from a run (body: `{run_id, itinerary_id}`; snapshots immutably).
- `PATCH /api/trips/{id}/shortlist/{item_id}` — update notes / tags / order.
- `DELETE /api/trips/{id}/shortlist/{item_id}` — remove from shortlist.

#### Scenario: Save itinerary snapshots immutably

- **WHEN** `POST /api/trips/{id}/shortlist` is called with `{run_id: 42, itinerary_id: 7}`
- **THEN** the server copies the itinerary's full state (fare ids, landed cost, cost breakdown, friction attributes, originating run id, snapshot timestamp) into the shortlist
- **AND** later edits to run 42's config or the gateway-transfer table do NOT mutate the shortlist item

#### Scenario: Soft delete

- **WHEN** `DELETE /api/trips/{id}` is called
- **THEN** the trip is marked deleted but remains retrievable for 7 days via `GET /api/trips?include_deleted=true`
- **AND** after 7 days a daily cleanup hard-deletes

### Requirement: Run streaming endpoint

The API SHALL expose `GET /api/runs/{id}/stream` as a Server-Sent Events endpoint emitting events for the lifetime of a run:

- `event: sweep_fare` — `data: {leg_ordinal, fare_id, source, price_per_pax, fetched_at}`
- `event: validation_result` — `data: {itinerary_id, status, landed_cost?}`
- `event: scoring_complete` — `data: {ranked_itinerary_ids: [...], filtered_out_count_by_axis}`
- `event: status` — `data: {status: "PENDING"|"RUNNING"|"COMPLETE"|"FAILED", stage: "sweep"|"validate"|"score"|"done"}`
- `event: error` — `data: {message, fatal: bool}`

The endpoint SHALL keep the connection open until the run reaches a terminal status (COMPLETE or FAILED) OR the client disconnects. On reconnect with `Last-Event-ID`, the server SHALL replay events from that id forward (or from run start if the id is unknown).

#### Scenario: SSE delivers events in order

- **WHEN** a client subscribes to `/api/runs/{id}/stream` for a running run
- **THEN** events arrive in the order: status(RUNNING) → sweep_fare* → validation_result* → scoring_complete → status(COMPLETE)
- **AND** each event has a unique monotonic `id` so clients can resume

#### Scenario: Reconnect with Last-Event-ID

- **WHEN** a client reconnects with `Last-Event-ID: 42`
- **THEN** the server replays events 43+ (or sends a fresh stream if the id is no longer cached)

### Requirement: Copilot endpoints with cost-honesty enforcement

The API SHALL expose copilot endpoints that proxy to an LLM provider (Anthropic) and return suggestions for specific config fields:

- `POST /api/copilot/preferences/suggest` — body: `{natural_language: "family with toddlers, hate red-eyes"}`; response: `{suggestions: [{path: "preferences.defaults.red_eye", value: "strongly_avoid", confidence: 0.92, rationale: "..."}, ...]}`.
- `POST /api/copilot/cost_assumptions/suggest` — body: `{trip_context: {destination, party, dates}}`; response: `{suggestions: [{path: "cost_assumptions.stopover_lodging_per_night", value: 32000, confidence: 0.5, rationale: "..."}]}`.
- `POST /api/copilot/stopover_waypoints/suggest` — body: `{origin: "SJO", destination_gateways: ["VCE", "MXP"]}`; response: `{candidates: ["MAD", "LIS", "LHR", "FRA"], rationale: "..."}`.

Every cost-related suggestion SHALL carry an `unverified: true` flag AND the response SHALL be validated at the API gateway: a copilot response that would write into a cost field without `unverified: true` SHALL be rejected and logged as a contract violation.

The SerpAPI key and the Anthropic API key SHALL NEVER cross the API boundary back to the client.

#### Scenario: Preference suggestion is structured

- **WHEN** the SPA POSTs `/api/copilot/preferences/suggest` with `{natural_language: "elderly parents, two toddlers, hate red-eyes"}`
- **THEN** the response contains one or more `{path, value, confidence, rationale}` suggestions targeting specific preference axes
- **AND** the SPA renders each as an inline `Card` with Accept/Edit/Reject buttons; nothing is auto-applied

#### Scenario: Cost suggestion is unverified-labelled

- **WHEN** the copilot suggests `{path: "cost_assumptions.stopover_lodging_per_night", value: 32000}`
- **THEN** the response carries `unverified: true`
- **AND** if a future LLM provider returned a cost suggestion without `unverified: true`, the API gateway rejects the response with a 502 (upstream contract violation) and surfaces a `Toast` to the SPA

#### Scenario: Copilot can be disabled

- **WHEN** the operator disables the copilot in Settings
- **THEN** the SPA stops calling `/api/copilot/*` endpoints
- **AND** the server enforces no behaviour change (the endpoints remain operable for other clients but are not invoked)

### Requirement: SPA-served static + catch-all route

The FastAPI process SHALL serve the SPA build output (`app/static/web-dist/`) as static files AND SHALL provide a catch-all route returning `index.html` for any path that does not match a `/api/*` route, so SPA client-side routing works on direct URL entry (e.g. an emailed `/trips/42/runs/7` link).

#### Scenario: Direct URL entry

- **WHEN** a client opens `https://app/trips/42/runs/7` directly
- **THEN** the server returns `index.html` (200) and the SPA router resolves the path client-side to the run results page

## MODIFIED Requirements

### Requirement: FastAPI service over SQLite

The system SHALL expose a FastAPI service providing CRUD for configs, trips, run triggering, run/result retrieval, run streaming (SSE), source-quota status, wizard state PATCH, shortlist persistence, and an LLM copilot proxy. The previous one-shot "configs CRUD + run trigger + result retrieval" surface is extended with the wizard-state, trips, shortlist, streaming, and copilot endpoints above.

#### Scenario: Trigger a run

- **WHEN** a client POSTs to trigger a run for a config id
- **THEN** the API starts the sweep asynchronously and returns a run id
- **AND** run status is pollable (PENDING / RUNNING / COMPLETE / FAILED)
- **AND** the run is streamable via `GET /api/runs/{id}/stream`

#### Scenario: Retrieve results

- **WHEN** a client requests results for a complete run
- **THEN** the API returns ranked itineraries with per-fare source, verification_status, fetched_at, blackout/staleness flags, **and per `add-preference-weighted-landed-cost`: `landed_cost`, `cost_breakdown` (each component with `data_source`), `friction_attributes`, `preference_explanations`, plus run-level `filtered_out_count_by_axis`**
