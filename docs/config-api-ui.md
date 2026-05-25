# Spec Delta: search-config

## ADDED Requirements

### Requirement: Persistent search definitions
The system SHALL persist search configurations in SQLite, each defining legs,
candidate gateways per leg, date anchors and windows/sampling, passenger mix,
budget ceiling, blackout ranges, and which structures (A/B) to price.

#### Scenario: Create and reuse a config
- **WHEN** a user saves a search configuration
- **THEN** it is retrievable by id and can seed multiple runs over time
- **AND** each run snapshots the config used, so historical runs remain
  interpretable after the config is edited

### Requirement: Run history
Each execution SHALL be persisted as a run record linked to its config, with
status, timestamps, source-call counts (scraper vs SerpAPI), and all resulting
fares/itineraries.

#### Scenario: Compare runs over time
- **WHEN** multiple runs of the same config exist
- **THEN** a user can retrieve each run's best validated party total to observe
  price movement across days

---

# Spec Delta: web-api

## ADDED Requirements

### Requirement: FastAPI service over SQLite
The system SHALL expose a FastAPI service providing CRUD for configs, run
triggering, run/result retrieval, and source-quota status.

#### Scenario: Trigger a run
- **WHEN** a client POSTs to trigger a run for a config id
- **THEN** the API starts the sweep asynchronously and returns a run id
- **AND** run status is pollable (PENDING / RUNNING / COMPLETE / FAILED)

#### Scenario: Retrieve results
- **WHEN** a client requests results for a complete run
- **THEN** the API returns ranked itineraries with per-fare source,
  verification_status, fetched_at, and blackout/staleness flags

### Requirement: No secrets in client
The SerpAPI key SHALL be held server-side only and SHALL NOT be exposed via any
API response or to the frontend.

#### Scenario: Config returned to UI
- **WHEN** a config is returned over the API
- **THEN** no API keys or secrets appear in the payload

---

# Spec Delta: web-ui

> **Phase 2 — deferred.** The Vue 3 + PrimeVue SPA described below is not what
> Phase 1 ships. Phase 1 serves a Jinja-templated UI from the FastAPI process;
> the authoritative Phase-1 spec is `openspec/specs/web-ui/spec.md`. A future
> Phase-2 change will MODIFY or REPLACE that spec with the requirements below.

## ADDED Requirements

### Requirement: Vue 3 + PrimeVue configuration UI
The system SHALL provide a Vue 3 SPA using PrimeVue components to create/edit
configs, trigger runs, and review results.

#### Scenario: Configure a search
- **WHEN** a user opens the config editor
- **THEN** they can set legs, candidate gateways, date anchors/windows,
  passenger mix, budget, blackout ranges, and structures to price
- **AND** invalid configs (e.g. past dates, empty gateway list) are rejected
  with a clear message

#### Scenario: Review results with status clarity
- **WHEN** a user views run results
- **THEN** VALIDATED, LEAD, VALIDATION_FAILED, STALE, and BLACKOUT states are
  visually distinct
- **AND** the budget verdict is shown using validated fares only
- **AND** the A-vs-B structure comparison is shown side by side

#### Scenario: Quota visibility
- **WHEN** a user is about to trigger a run
- **THEN** the UI shows estimated SerpAPI calls and remaining monthly quota
  before the run starts
