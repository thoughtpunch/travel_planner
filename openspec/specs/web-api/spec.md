# web-api Specification

## Purpose

Expose the orchestrator over an HTTP surface: configs CRUD, run triggering,
result retrieval, SerpAPI quota status, and a pre-run estimate so operators
can see quota cost before they commit. The SerpAPI key never crosses the
API boundary.

## Requirements

### Requirement: FastAPI service over SQLite

The system SHALL expose a FastAPI service providing CRUD for configs, trips, run triggering, run/result retrieval, run streaming (SSE), source-quota status, wizard state PATCH, shortlist persistence, and an LLM copilot proxy.

#### Scenario: Trigger a run

- **WHEN** a client POSTs to trigger a run for a config id
- **THEN** the API starts the sweep asynchronously and returns a run id
- **AND** run status is pollable (PENDING / RUNNING / COMPLETE / FAILED)
- **AND** the run is streamable via `GET /api/runs/{id}/stream`

#### Scenario: Retrieve results

- **WHEN** a client requests results for a complete run
- **THEN** the API returns ranked itineraries with per-fare source, verification_status, fetched_at, blackout/staleness flags, **and per `add-preference-weighted-landed-cost`: `landed_cost`, `cost_breakdown` (each component with `data_source`), `friction_attributes`, `preference_explanations`, plus run-level `filtered_out_count_by_axis`**

### Requirement: Wizard state endpoints (idempotent PATCH)

The API SHALL expose endpoints for incremental wizard state persistence: `POST /api/configs` (create draft), `GET /api/configs/{id}`, `PATCH /api/configs/{id}` (JSON-merge-patch — partial preferences and cost_assumptions accepted), `POST /api/configs/{id}/finalize` (validate the full schema; reject incoherent preferences with 422), `GET /api/configs/{id}/preview` (dry-run summary: matrix size, planned SerpAPI calls, constructed stopover count).

#### Scenario: Debounced wizard PATCH

- **WHEN** the SPA sends `PATCH /api/configs/{id}` with `{preferences: {defaults: {layover_length: "avoid"}}}`
- **THEN** the server merges only that field; other preferences and cost_assumptions are untouched
- **AND** the response is the full updated config so the client can reconcile

#### Scenario: Finalize rejects incoherent draft

- **WHEN** `POST /api/configs/{id}/finalize` is called on a draft with HARD YES on `layover_length`
- **THEN** the response is 422 naming the offending field

#### Scenario: Preview shows dry run

- **WHEN** `GET /api/configs/{id}/preview` is called
- **THEN** the response includes the planned SerpAPI call count, the constructed-stopover count, and the matrix size

### Requirement: Trip workspace endpoints

The API SHALL expose endpoints for trips, where a trip owns one config, many runs, one shortlist, and notes: `GET /api/trips`, `POST /api/trips` (creates draft config implicitly), `GET /api/trips/{id}`, `PATCH /api/trips/{id}`, `DELETE /api/trips/{id}` (soft-delete with 7-day grace), `GET /api/trips/{id}/runs`, `GET /api/trips/{id}/shortlist`, `POST /api/trips/{id}/shortlist`, `PATCH /api/trips/{id}/shortlist/{item_id}`, `DELETE /api/trips/{id}/shortlist/{item_id}`.

#### Scenario: Save itinerary snapshots immutably

- **WHEN** `POST /api/trips/{id}/shortlist` is called with `{run_id, itinerary_id}`
- **THEN** the server copies the itinerary's full state into the shortlist
- **AND** later edits to the run's config, the gateway-transfer table, or the itinerary row do NOT mutate the shortlist item

#### Scenario: Soft delete

- **WHEN** `DELETE /api/trips/{id}` is called
- **THEN** the trip is marked deleted but remains retrievable via `GET /api/trips?include_deleted=true`

### Requirement: Run streaming endpoint

The API SHALL expose `GET /api/runs/{id}/stream` as a Server-Sent Events endpoint emitting events (`status`, `sweep_fare`, `validation_result`, `scoring_complete`, `error`) with monotonic ids. On reconnect with `Last-Event-ID`, the server SHALL replay events with id > last seen. The endpoint SHALL keep the connection open until terminal status OR the client disconnects.

#### Scenario: SSE delivers events in order

- **WHEN** a client subscribes to `/api/runs/{id}/stream` for a running run
- **THEN** events arrive in the order: status → sweep_fare* → validation_result* → scoring_complete → status(COMPLETE)
- **AND** each event has a unique monotonic `id`

### Requirement: Copilot endpoints with cost-honesty enforcement

The API SHALL expose copilot endpoints that proxy to an LLM provider (or stub) and return field-targeted suggestions: `POST /api/copilot/preferences/suggest`, `POST /api/copilot/cost_assumptions/suggest`, `POST /api/copilot/stopover_waypoints/suggest`.

Every cost-related suggestion SHALL carry `unverified: true`. The gateway SHALL reject responses that target a cost field without `unverified` (with 502, logged as a contract violation) or that target a forbidden path outside the config-input set (with 422). The Anthropic / LLM API key SHALL NEVER cross the API boundary back to the client.

#### Scenario: Cost suggestion is unverified-labelled

- **WHEN** the copilot suggests a value at `cost_assumptions.stopover_lodging_per_night`
- **THEN** the response carries `unverified: true`
- **AND** if missing, the API gateway rejects the response with 502

#### Scenario: Forbidden path rejected

- **WHEN** the copilot attempts to return a suggestion targeting `results.exclude_itinerary_ids`
- **THEN** the API gateway rejects with 422

### Requirement: SPA-served static + catch-all route

The FastAPI process SHALL serve the SPA build output (`app/static/web-dist/`) as static files AND SHALL provide a catch-all route returning `index.html` for any path under `/trips/`, `/settings/`, or `/wizard/` that does not match an `/api/*` route, so SPA client-side routing works on direct URL entry.

#### Scenario: Direct URL entry

- **WHEN** a client opens `https://app/trips/42/runs/7` directly
- **THEN** the server returns `index.html` (200, when SPA is built) and the SPA router resolves the path client-side

### Requirement: Pre-run SerpAPI estimate

The API SHALL expose an endpoint that returns the expected SerpAPI call
count for a run before it is triggered.

#### Scenario: Estimate vs. remaining quota

- **WHEN** a client requests `/api/runs/estimate/{config_id}`
- **THEN** the response includes `planned_calls`, `remaining_before`,
  `remaining_after_if_run`, and `would_exceed`
- **AND** the UI can show the operator the quota cost before they
  commit

### Requirement: No secrets in client

The SerpAPI key SHALL be held server-side only and SHALL NOT be exposed
via any API response or to the frontend.

#### Scenario: Config returned to UI

- **WHEN** a config is returned over the API
- **THEN** no API keys or secrets appear in the payload
