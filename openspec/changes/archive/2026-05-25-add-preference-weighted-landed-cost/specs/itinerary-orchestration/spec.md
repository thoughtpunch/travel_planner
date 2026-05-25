## MODIFIED Requirements

### Requirement: Ranking

The system SHALL rank itineraries by **validated landed cost** ascending (per `landed-cost-model`), then apply preference scoring (per `preference-scoring`) to reorder within the honestly-priced set. LEAD and VALIDATION_FAILED itineraries remain ranked separately from VALIDATED ones, and only VALIDATED itineraries are eligible to be labeled a recommendation. The previous airfare-only ranking is removed.

#### Scenario: Landed-cost ranking with preferences

- **WHEN** a result set contains VALIDATED itineraries with differing landed costs and friction attributes
- **THEN** they are ordered by landed cost ascending
- **AND** soft preferences reorder within the ±10% landed-cost soft band
- **AND** HARD NO items have already been filtered out of the set before this step
- **AND** HARD YES items have already been constructed and priced; they appear in the set
- **AND** the cheapest VALIDATED landed-cost option that satisfies hard constraints is identifiable as the primary recommendation

#### Scenario: Mixed-status result set

- **WHEN** a result set contains VALIDATED, LEAD, and VALIDATION_FAILED itineraries
- **THEN** VALIDATED itineraries are ranked first (by landed cost, then preference-reordered)
- **AND** LEAD and VALIDATION_FAILED itineraries are ranked separately below
- **AND** only VALIDATED itineraries are eligible for the recommendation label

## ADDED Requirements

### Requirement: Preference-driven stopover construction

The orchestration matrix SHALL support injecting a stopover leg into a structure when the stopover preference axis is HARD YES. The constructor SHALL generate fare queries for the SJO → [stopover] and [stopover] → [gateway] segments with a 1-night gap (or the user-specified gap), and the resulting candidate SHALL be priced through the normal sweep / validate / landed-cost pipeline including the stopover lodging assumption.

#### Scenario: Constructed stopover priced end to end

- **WHEN** HARD YES stopover names Madrid (MAD)
- **THEN** the system prices SJO → MAD and MAD → [Italy gateway] as separate legs with a 1-night gap
- **AND** adds the user-owned per-night lodging assumption from `landed-cost-model` to landed cost (× rooms × nights)
- **AND** ranks the result against other VALIDATED options on landed cost

#### Scenario: Sweep over waypoint candidates

- **WHEN** HARD YES stopover is set with no named city and the user consents to a sweep
- **THEN** each candidate waypoint (e.g. MAD, LIS, LHR) produces a constructed itinerary
- **AND** each is priced through the full pipeline
- **AND** they are ranked together with direct itineraries on landed cost
- **AND** the result presentation labels each constructed itinerary with its stopover city

#### Scenario: Stopover construction respects HARD NO axes

- **WHEN** HARD YES stopover is set AND HARD NO red-eye is also set
- **THEN** any constructed stopover itinerary whose SJO → [stopover] or [stopover] → [gateway] leg arrives in the red-eye window is filtered out
- **AND** constructed candidates that survive both constraints appear in the result set
