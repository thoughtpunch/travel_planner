## ADDED Requirements

### Requirement: Persistent search definitions

The system SHALL persist search configurations in SQLite, each defining
legs, candidate gateways per leg, date anchors and windows/sampling,
passenger mix, budget ceiling, blackout ranges, and which structures
(A/B) to price.

#### Scenario: Create and reuse a config

- **WHEN** a user saves a search configuration
- **THEN** it is retrievable by id and can seed multiple runs over time
- **AND** each run snapshots the config used, so historical runs remain
  interpretable after the config is edited

### Requirement: Run history

Each execution SHALL be persisted as a run record linked to its config,
with status, timestamps, source-call counts (scraper vs SerpAPI), and
all resulting fares/itineraries.

#### Scenario: Compare runs over time

- **WHEN** multiple runs of the same config exist
- **THEN** a user can retrieve each run's best validated party total to
  observe price movement across days
