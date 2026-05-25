# fare-validation Specification

## Purpose

Re-query top-ranked LEAD candidates against an authoritative source at the
full party size to confirm bookable fares, classify them as VALIDATED or
VALIDATION_FAILED, enforce budget verdicts against VALIDATED-only data, and
expire stale fares via TTL so recommendations are never based on outdated
prices.

## Requirements

### Requirement: Candidate validation pass

After a sweep produces ranked candidate itineraries, the system SHALL
re-query the top N candidates (N configurable, default 5 per structure)
against an authoritative source at the full passenger count to confirm
the fare exists for the whole party.

#### Scenario: Lead validated successfully

- **WHEN** a top-ranked LEAD itinerary is re-queried at full passenger
  count
- **AND** a fare within a configurable tolerance (default ±15%) of the
  lead price is returned with seats for the full party
- **THEN** the itinerary's `verification_status` becomes `VALIDATED`
- **AND** the validated price (not the lead price) is used for budget
  math

#### Scenario: Lead fails validation (the 6-seat collapse)

- **WHEN** a top-ranked LEAD is re-queried and no fare exists for the
  full party at or near the lead price
- **THEN** the itinerary is marked `VALIDATION_FAILED`
- **AND** SHALL be excluded from "budget met" determination
- **AND** the next-best unvalidated candidate SHALL be promoted into the
  validation queue if validation budget remains

### Requirement: Budget determination uses validated fares only

The system SHALL compute whether the per-engagement budget ceiling
(default $1,000/person, USD 6,000 party) is met using ONLY `VALIDATED`
fares.

#### Scenario: Only leads meet budget

- **WHEN** the cheapest itineraries meeting budget are all LEAD or
  VALIDATION_FAILED
- **THEN** the system SHALL report "budget NOT met by any validated
  itinerary" rather than reporting the lead price as a success

### Requirement: Staleness expiry

Fares SHALL carry a `fetched_at` timestamp and a configurable TTL
(default 24h). Fares older than their TTL SHALL be flagged STALE and
excluded from final recommendations until refreshed.

#### Scenario: Stale validated fare

- **WHEN** a VALIDATED fare exceeds its TTL
- **THEN** it is downgraded to STALE and re-validation is required
  before it can be presented as a recommendation
