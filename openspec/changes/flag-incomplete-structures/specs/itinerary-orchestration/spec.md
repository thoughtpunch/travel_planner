## ADDED Requirements

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
