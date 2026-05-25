# web-ui Specification

## Purpose

Phase-1 server-rendered Jinja UI for operating the orchestrator: list
configs, trigger runs, browse run history, and view ranked results with
clear status badges and a budget verdict derived from VALIDATED fares
only. A Vue 3 + PrimeVue SPA is explicitly out of scope for Phase 1 and
will arrive as a Phase-2 change that MODIFIES or REPLACES this spec.

## Requirements

### Requirement: Phase-1 server-rendered UI

The system SHALL ship a Phase-1 server-rendered UI using Jinja templates
served by the FastAPI process. The UI SHALL cover the operator
workflow: list configs, trigger a run, list recent runs, and view
ranked results for a single run.

A Vue 3 + PrimeVue single-page app is explicitly out of scope for Phase
1 and will be introduced as a Phase-2 change that MODIFIES or REPLACES
this requirement.

#### Scenario: Operator triggers a run

- **WHEN** an operator opens `/` and clicks "Trigger run" on a listed
  config
- **THEN** a POST to `/api/runs?config_id={id}` is issued and the
  resulting run id is reachable at `/runs/{id}`

#### Scenario: Operator reviews results

- **WHEN** an operator opens `/runs/{id}` for a complete run
- **THEN** the page renders ranked itineraries grouped by Structure A
  and B
- **AND** each row shows verification_status as a colour-coded badge
- **AND** blackout, long-gap, and other flags are shown alongside
- **AND** the budget verdict is displayed at the top of the page,
  computed from VALIDATED fares only

### Requirement: Status clarity in the UI

The UI SHALL render every distinct verification status with a visually
distinct badge style, so an operator cannot mistake a LEAD for a
VALIDATED fare at a glance.

#### Scenario: Mixed-status result table

- **WHEN** a result set contains VALIDATED, LEAD, VALIDATION_FAILED,
  STALE, SKIPPED_QUOTA, FAILED, BLACKOUT, and LONG_GAP states
- **THEN** each status has a dedicated CSS badge class (e.g.
  `.b-VALIDATED`, `.b-LEAD`, etc.) with non-overlapping colour palettes
- **AND** the page includes a reminder that LEAD fares are unverified
  display prices

### Requirement: Quota visibility on results page

The UI SHALL show, for each run, the number of SerpAPI calls consumed
and the quota remaining after the run.

#### Scenario: Quota line on the run page

- **WHEN** an operator opens a run results page
- **THEN** the header reports scraper call count, SerpAPI call count,
  and SerpAPI quota remaining
