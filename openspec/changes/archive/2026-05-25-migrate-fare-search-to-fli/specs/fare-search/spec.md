## MODIFIED Requirements

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
