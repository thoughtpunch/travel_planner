## ADDED Requirements

### Requirement: Primary fare source via fast-flights scraper

The system SHALL query flight fares using the `fast-flights` library as the
primary data source, constructing queries by origin airport, destination
airport, date, cabin (economy), trip type, and passenger count.

#### Scenario: Successful scraper query

- **WHEN** a fare query is issued for a valid airport pair and future date
- **THEN** the system returns a list of fare offers, each with carrier,
  price, currency, departure/arrival times, stop count, and a `source`
  field set to `fast-flights`
- **AND** each offer is recorded with `verification_status = LEAD`

#### Scenario: Scraper returns no results

- **WHEN** the scraper returns an empty result set for a query
- **THEN** the system SHALL treat this as a soft failure and trigger the
  fallback source for that query
- **AND** SHALL NOT record the empty result as a confirmed "no flights"
  answer

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

The system SHALL fall back to the SerpAPI Google Flights endpoint when the
primary scraper fails, returns empty, or is explicitly selected for
validation.

#### Scenario: Scraper failure triggers fallback

- **WHEN** a `fast-flights` query raises an exception, times out, or
  returns a malformed/empty response
- **THEN** the system SHALL issue the equivalent query via SerpAPI
- **AND** SHALL record which source ultimately served each result

#### Scenario: SerpAPI key absent

- **WHEN** no SerpAPI API key is configured
- **AND** the primary scraper fails
- **THEN** the system SHALL record the query as `FAILED` with reason
  `no_fallback_available` and continue the run without aborting the whole
  sweep

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
