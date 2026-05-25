## ADDED Requirements

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
