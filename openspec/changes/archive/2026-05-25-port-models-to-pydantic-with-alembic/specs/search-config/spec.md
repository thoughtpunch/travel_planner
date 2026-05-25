## MODIFIED Requirements

### Requirement: Persistent search definitions

The system SHALL persist search configurations in SQLite, each defining
legs, candidate gateways per leg, date anchors and windows/sampling,
passenger mix, budget ceiling, blackout ranges, and which structures
(A/B) to price. The persistence layer SHALL be implemented as
**SQLAlchemy 2.0 declarative ORM** classes (not the prior SQLModel
hybrid), and IO models SHALL be **pure Pydantic v2** schemas, kept in
a separate module from the ORM. Schema evolution SHALL go through
**Alembic** migrations; the application SHALL NOT issue
`CREATE TABLE` at boot time.

#### Scenario: Create and reuse a config

- **WHEN** a user saves a search configuration
- **THEN** it is retrievable by id and can seed multiple runs over
  time
- **AND** each run snapshots the config used, so historical runs
  remain interpretable after the config is edited

#### Scenario: Schema evolution

- **WHEN** the application source defines a model column not present
  in a running deployment's database
- **THEN** an Alembic migration SHALL be the mechanism that adds the
  column
- **AND** the application SHALL refuse to start against a database
  with no `alembic_version` table, raising a clear error directing
  the operator to run the migration command

#### Scenario: Wire-compatible upgrade from the SQLModel era

- **WHEN** an operator upgrades from a pre-Alembic build using an
  existing `trip_planner.db`
- **THEN** running `alembic stamp head` once SHALL make the database
  compatible with subsequent migrations
- **AND** no rows or columns SHALL need to be rewritten

### Requirement: Run history

Each execution SHALL be persisted as a run record linked to its
config, with status, timestamps, source-call counts (scraper vs
SerpAPI), and all resulting fares/itineraries.

#### Scenario: Compare runs over time

- **WHEN** multiple runs of the same config exist
- **THEN** a user can retrieve each run's best validated party total
  to observe price movement across days
