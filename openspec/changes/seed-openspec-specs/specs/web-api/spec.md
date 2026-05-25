## ADDED Requirements

### Requirement: FastAPI service over SQLite

The system SHALL expose a FastAPI service providing CRUD for configs,
run triggering, run/result retrieval, and source-quota status.

#### Scenario: Trigger a run

- **WHEN** a client POSTs to trigger a run for a config id
- **THEN** the API starts the sweep asynchronously and returns a run id
- **AND** run status is pollable (PENDING / RUNNING / COMPLETE / FAILED)

#### Scenario: Retrieve results

- **WHEN** a client requests results for a complete run
- **THEN** the API returns ranked itineraries with per-fare source,
  verification_status, fetched_at, and blackout/staleness flags

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
