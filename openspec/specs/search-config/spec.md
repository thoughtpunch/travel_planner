# search-config Specification

## Purpose

Persist search definitions and per-run history in SQLite so that
configurations can be reused across runs and so historical results remain
interpretable even after a configuration is edited.

## Requirements

### Requirement: Persistent search definitions

The system SHALL persist search configurations in SQLite, each defining
legs, candidate gateways per leg, date anchors and windows/sampling,
passenger mix, budget ceiling, blackout ranges, which structures
(A/B) to price, **preferences (global defaults + per-leg overrides), and
cost assumptions (per-night stopover lodging, optional per-gateway
transfer overrides)**. The persistence layer SHALL be implemented as
**SQLAlchemy 2.0 declarative ORM** classes (not the prior SQLModel
hybrid), and IO models SHALL be **pure Pydantic v2** schemas, kept in
a separate module from the ORM. Schema evolution SHALL go through
**Alembic** migrations; the application SHALL NOT issue
`CREATE TABLE` at boot time.

#### Scenario: Create and reuse a config with preferences

- **WHEN** a user saves a search configuration including preferences
  (global `avoid` on layover length, per-leg HARD NO on return-leg
  red-eye) and cost assumptions ($320/night family room)
- **THEN** it is retrievable by id and can seed multiple runs over
  time
- **AND** each run snapshots the full config including preferences and
  assumptions, so historical runs remain interpretable after the
  config is edited
- **AND** the snapshot includes the `last_reviewed` date of any
  gateway-transfer table figure used, so a historical run remains
  comparable even after the table is updated

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

Each execution SHALL be persisted as a run record linked to its config,
with status, timestamps, source-call counts (scraper vs SerpAPI), and
all resulting fares/itineraries.

#### Scenario: Compare runs over time

- **WHEN** multiple runs of the same config exist
- **THEN** a user can retrieve each run's best validated party total to
  observe price movement across days

### Requirement: Preferences are part of the config

The config schema SHALL contain a `preferences` block with:

- `defaults`: object keyed by axis (`transfer_length`, `layover_length`,
  `stopover`, `plane_changes`, `red_eye`), each value one of the seven
  scale positions (`hard_no`, `strongly_avoid`, `avoid`, `neutral`,
  `desire`, `strongly_desire`, `hard_yes`) plus an axis-specific
  threshold where relevant (e.g.
  `layover_length.hard_no_above_minutes`,
  `red_eye.window_local = ["23:00", "06:00"]`).
- `per_leg_overrides`: list of `{leg_ordinal: int, axis: string,
  value: position, threshold?: any}` entries.
- For HARD YES on `stopover`: `stopover_target: {city: string} |
  {sweep_candidates: string[]}`.

The config validator SHALL reject:

- HARD YES on axes that do not admit it (anything but `stopover` in v1),
- HARD YES on `stopover` without a `stopover_target`,
- per-leg overrides referencing a leg ordinal that does not exist in
  the config,
- positions that are not one of the seven defined scale values.

#### Scenario: Config validation rejects incoherent preferences

- **WHEN** an API client POSTs a config with
  `preferences.defaults.layover_length = "hard_yes"`
- **THEN** the validator returns 422 with a structured error naming
  `preferences.defaults.layover_length` and explaining that HARD YES
  is not meaningful for that axis

#### Scenario: Snapshot fidelity across config edits

- **WHEN** a run is executed with config v1 (preferences = X), the
  config is then edited (preferences = Y), and the historical run is
  reopened
- **THEN** the historical run displays the preferences as they were at
  run time (X), labeled "snapshot from <date>"
- **AND** the current (live) config edit page shows Y separately

### Requirement: Cost assumptions are part of the config

The config schema SHALL contain a `cost_assumptions` block with:

- `stopover_lodging_per_night`: integer (cents or whole-currency units
  consistent with the rest of the system) — the user-owned per-night
  family-room assumption.
- `stopover_rooms`: integer (default 2 for party of 6).
- `transfer_overrides`: optional object keyed by `{gateway → {mode →
  per_person_cost}}` overriding individual entries in the hardcoded
  gateway-transfer table for this config only.
- `llm_suggested`: optional object marking which fields were
  LLM-prefilled and not yet user-confirmed.

The config validator SHALL reject negative values and SHALL require
`stopover_lodging_per_night` to be set whenever HARD YES on `stopover`
is set OR any `forces_overnight = true` itinerary could plausibly
result.

#### Scenario: LLM pre-fill is labeled

- **WHEN** an LLM has pre-filled
  `stopover_lodging_per_night = 32000` (i.e. $320)
- **AND** the user has not yet confirmed
- **THEN** the config carries
  `llm_suggested.stopover_lodging_per_night = true`
- **AND** the UI shows the value with a "suggested estimate — verify"
  label
- **AND** any run using this config tags itineraries that consumed the
  assumption with the same "unverified estimate" label

#### Scenario: User confirms LLM-suggested value

- **WHEN** the user accepts or edits the LLM-suggested value
- **THEN** `llm_suggested.stopover_lodging_per_night` is set to `false`
- **AND** the label changes to "your estimate"
