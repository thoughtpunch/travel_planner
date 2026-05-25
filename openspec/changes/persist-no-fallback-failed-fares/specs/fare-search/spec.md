## MODIFIED Requirements

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
