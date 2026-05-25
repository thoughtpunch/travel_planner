# fare-search Specification

## Purpose

Multi-source fare retrieval for the Multi-Leg Flight Fare Orchestrator. The
default primary source is the `fli` scraper (Google Flights display fares,
treated as unverified LEADs); the legacy `fast-flights` scraper remains
selectable via `PRIMARY_SOURCE`. SerpAPI Google Flights serves as the
authoritative fallback. Quota and passenger-count fidelity are enforced so the
system never silently produces a wrong "no flights" answer or a
party-incompatible fare.

## Requirements

### Requirement: Primary fare source via configured scraper

The system SHALL query flight fares using the configured primary scraper as the data source, constructing queries by origin airport, destination airport, date, cabin (economy), trip type, and passenger count. The default primary scraper SHALL be `fli` (the `flights` PyPI package, sourced from `https://github.com/punitarani/fli`); the legacy `fast-flights` scraper SHALL remain selectable via the `PRIMARY_SOURCE` configuration setting for at least one release cycle.

#### Scenario: Successful primary-scraper query

- **WHEN** a fare query is issued for a valid airport pair and future date
- **THEN** the system returns a list of fare offers, each with carrier,
  price, currency, departure/arrival times, stop count, and a `source`
  field set to the configured primary scraper's identifier (`fli` or
  `fast-flights`)
- **AND** each offer is recorded with `verification_status = LEAD`

#### Scenario: Primary-scraper returns no results

- **WHEN** the primary scraper returns an empty result set for a query
- **THEN** the system SHALL treat this as a soft failure and trigger the
  fallback source for that query
- **AND** SHALL NOT record the empty result as a confirmed "no flights"
  answer

#### Scenario: Primary scraper raises a typed parse error

- **WHEN** the primary scraper raises a typed parse error indicating
  the upstream response shape changed (e.g. `fli`'s `SearchParseError`)
- **THEN** the system SHALL treat the query as a soft failure and
  trigger the fallback source
- **AND** SHALL surface the parse-error category in run logs so an
  operator can distinguish "scraper schema drift" from network
  failures

#### Scenario: Operator overrides the primary scraper

- **WHEN** the operator sets `PRIMARY_SOURCE=fast-flights` in the
  environment
- **THEN** runs SHALL use the legacy `fast-flights` adapter for the
  sweep step
- **AND** each offer's `source` field SHALL reflect that choice
- **AND** the LEAD/VALIDATED contract SHALL be unchanged

### Requirement: Scraper fares are never treated as bookable

The system SHALL classify every fare returned by `fast-flights` as an
unverified LEAD, because the scraper returns Google Flights display fares
that are not validated against availability at the requested passenger
count.

#### Scenario: Lead fare presented to user

- **WHEN** a `fast-flights` fare is displayed in any UI or report
- **THEN** it SHALL be visually and structurally marked as an unverified
  lead
- **AND** the system SHALL NOT include LEAD-only fares in any "budget met"
  determination

### Requirement: Fallback fare source via SerpAPI

The system SHALL fall back to the SerpAPI Google Flights endpoint when
the primary scraper fails, returns empty, or is explicitly selected
for validation. When fallback is unavailable or also fails, the system
SHALL persist a `FAILED` Fare row capturing the failure so the run's
audit trail records the event instead of silently dropping the query.

#### Scenario: Scraper failure triggers fallback

- **WHEN** a `fast-flights` query raises an exception, times out, or
  returns a malformed/empty response
- **THEN** the system SHALL issue the equivalent query via SerpAPI
- **AND** SHALL record which source ultimately served each result

#### Scenario: SerpAPI key absent

- **WHEN** no SerpAPI API key is configured
- **AND** the primary scraper fails or returns empty
- **THEN** the system SHALL persist exactly one `Fare` row for that
  query with `verification_status = FAILED`,
  `notes.reason = "no_fallback_available"`,
  `price_per_pax = 0`, and `source = fast-flights`
- **AND** the run continues without aborting the whole sweep
- **AND** the run's results payload exposes a `failed_query_count`
  field summarising how many queries failed

#### Scenario: Both primary and fallback fail

- **WHEN** the primary scraper fails AND the SerpAPI fallback also
  raises a `SourceError`
- **THEN** the system SHALL persist exactly one `Fare` row for that
  query with `verification_status = FAILED` and
  `notes.reason = "fallback_failed: <error>"`
- **AND** the run continues without aborting the whole sweep

### Requirement: SerpAPI quota protection

The system SHALL track SerpAPI call count against a configurable monthly
budget and SHALL refuse to exceed it without explicit override.

#### Scenario: Quota ceiling reached mid-run

- **WHEN** a run would cause SerpAPI calls to exceed the configured ceiling
- **THEN** remaining validation queries SHALL be skipped and marked
  `SKIPPED_QUOTA`
- **AND** the run completes and reports how many candidates went
  unvalidated

### Requirement: Passenger count fidelity

All fare queries SHALL carry the configured passenger mix (default: 6
adults, 0 children, 0 infants for this engagement) so that source results
reflect the true party where the source supports it.

#### Scenario: Source ignores passenger count

- **WHEN** a source returns a fare without confirming seat availability at
  the requested count (e.g. display-fare scrapers)
- **THEN** that fare remains a LEAD regardless of price
