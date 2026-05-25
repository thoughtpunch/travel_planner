# itinerary-orchestration Specification

## Purpose

Expand a search configuration into a concrete (leg × gateway × date) query
matrix, price both itinerary structures (A: three one-ways; B: nested
envelope), flag blackout and long-gap conditions, and rank results with
clear separation between validated and unvalidated party totals.

## Requirements

### Requirement: Leg and gateway matrix expansion

The system SHALL expand a search configuration into a set of concrete
fare queries spanning the configured date windows and candidate gateways
for each leg.

#### Scenario: Leg 1 gateway sweep

- **WHEN** Leg 1 is configured as SJO → {VCE, MXP, LIN, ZRH, MUC, BLQ}
  with a date anchor and a ±window
- **THEN** the system generates one query per (gateway × sampled date)
  pair
- **AND** each European gateway carries metadata (train duration & rough
  cost to Venice) so ranking can surface the true door-to-door cost

#### Scenario: Date sampling to control cost

- **WHEN** a date window is configured with a sampling strategy (e.g.
  anchor, ±3, ±5, ±7 rather than every day)
- **THEN** only the sampled dates generate queries
- **AND** the strategy is recorded so a user understands the
  coverage/cost tradeoff

### Requirement: Dual structure pricing

The system SHALL price BOTH itinerary structures and compare them:

- **Structure A — Three one-ways:** SJO→[IT gateway], [IT]→[DC], [DC]→SJO
- **Structure B — Nested envelope:** SJO⇄DC round-trip (outer) +
  DC⇄[EU gateway] round-trip (inner, nested one day inside each end)

#### Scenario: Structure comparison

- **WHEN** a run completes with validated fares for both structures
- **THEN** the system reports the cheapest validated party total for
  each structure side by side
- **AND** identifies the winning structure
- **AND** if a structure cannot be fully validated, reports it as
  "incomplete — cannot compare" rather than silently dropping it

#### Scenario: Envelope long-gap warning

- **WHEN** Structure B's inner round-trip has an outbound-to-return gap
  exceeding a configurable threshold (default 30 days)
- **THEN** the system SHALL flag that round-trip fare advantage may not
  apply and the envelope may price worse than expected

### Requirement: Thanksgiving / blackout date avoidance

The system SHALL support configurable blackout/penalty date ranges and
SHALL flag any candidate itinerary whose segments fall on them.

#### Scenario: Return leg on Thanksgiving weekend

- **WHEN** a Leg 3 (DC→SJO) candidate departs on a configured blackout
  date (US Thanksgiving weekend)
- **THEN** the itinerary is flagged `BLACKOUT` and de-prioritized in
  ranking (not hard-excluded, since the user may still choose it)

### Requirement: Ranking

The system SHALL rank itineraries by validated party total ascending,
with LEAD and VALIDATION_FAILED itineraries ranked separately and
clearly distinguished from VALIDATED ones.

#### Scenario: Mixed-status result set

- **WHEN** a result set contains VALIDATED, LEAD, and VALIDATION_FAILED
  itineraries
- **THEN** VALIDATED itineraries are ranked first and are the only ones
  eligible to be labeled a recommendation

### Requirement: Incomplete-structure flagging

The system SHALL flag every candidate of an incomplete structure with `INCOMPLETE` and SHALL surface each priced structure's completeness in the run results payload, so the UI can render "incomplete — cannot compare" instead of silently dropping that structure from the comparison.

A structure is considered:

- **complete** if it has at least one VALIDATED candidate.
- **incomplete** if it produced candidates but none reached VALIDATED.
- **absent** if it was not requested in the run's config.

#### Scenario: Only LEAD candidates for one structure

- **WHEN** Structure A has at least one VALIDATED candidate AND
  Structure B has only LEAD or VALIDATION_FAILED candidates
- **THEN** every Structure B candidate's `flags` array SHALL contain
  `"INCOMPLETE"`
- **AND** no Structure A candidate's `flags` array shall contain
  `"INCOMPLETE"`
- **AND** the run results payload SHALL include
  `structures: {"A": "complete", "B": "incomplete"}`

#### Scenario: Both structures fully validated

- **WHEN** Structure A and Structure B both have at least one VALIDATED
  candidate
- **THEN** no candidate's `flags` array contains `"INCOMPLETE"`
- **AND** the run results payload SHALL include
  `structures: {"A": "complete", "B": "complete"}`

#### Scenario: Structure not priced in this run

- **WHEN** the run's config requests only Structure A
- **THEN** the run results payload SHALL include
  `structures: {"A": <state>, "B": "absent"}`

#### Scenario: UI displays incomplete-structure notice

- **WHEN** an operator views a run results page where
  `structures.B == "incomplete"`
- **THEN** the page renders a visible "Structure B — incomplete;
  cannot compare" message in place of the empty results table
- **AND** the budget verdict (computed from VALIDATED only) is
  unaffected
