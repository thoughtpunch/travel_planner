# Spec Delta: preference-scoring

## ADDED Requirements

### Requirement: Cost spine computed before preference scoring
Landed cost SHALL be computed honestly and completely (airfare + transfer +
any lodging) BEFORE any preference scoring is applied. Preference scoring SHALL
NOT mutate any cost figure.

#### Scenario: Desired stopover is not double-counted
- **WHEN** an itinerary has a stopover the user desires
- **THEN** its stopover lodging is already included in its landed cost
- **AND** the desire preference only reorders ranking; it does NOT discount the
  lodging or otherwise reduce the cost to favor the itinerary
- **AND** the itinerary is never made to "look cheaper" by its desirability

### Requirement: The no=filter / yes=construct duality
The two hard ends of the preference scale SHALL be implemented as distinct
operations over distinct objects:
- **HARD NO** operates on the **result set** (subtractive: exclude matching
  itineraries).
- **HARD YES** operates on the **itinerary structure** (additive: construct the
  feature as a leg, then search).

#### Scenario: HARD NO does not construct
- **WHEN** an axis is HARD NO
- **THEN** the system only filters; it never adds legs

#### Scenario: HARD YES does not filter the base set
- **WHEN** the stopover axis is HARD YES
- **THEN** the system constructs stopover itineraries and searches them
- **AND** does not silently delete the user's other candidate itineraries merely
  because they lack a stopover (the user chose construct, not filter)

### Requirement: Soft scoring asymmetry preserved
In the soft middle of the scale, "desire" SHALL act only as an attractor
(rank up) and "avoid" only as a detractor (rank down). At maximum *soft* desire
("strongly desire"), the effect SHALL remain a ranking boost over a mixed set
and SHALL NOT become a requirement; only HARD YES constructs.

#### Scenario: Strongly desire vs HARD YES distinction
- **WHEN** stopover is "strongly desire" (soft)
- **THEN** both stopover and non-stopover itineraries appear; stopover ones rank
  higher
- **WHEN** stopover is HARD YES
- **THEN** the system constructs stopover routes specifically

### Requirement: Ranking output is honest about spine vs. preference
Result presentation SHALL show landed cost (the spine) as the primary sortable
figure, with friction attributes (transfer length, layover length, plane
changes, red-eye, stopover) shown as labeled columns/flags, so the user can see
the money-vs-friction tradeoff directly rather than trusting a single blended
score.

#### Scenario: Mixed result presentation
- **WHEN** results are shown
- **THEN** each itinerary displays its landed cost, its component breakdown
  (fare / transfer / lodging), and its friction attributes
- **AND** the preference-driven rank order is applied but the underlying cost
  and attributes remain individually visible

---

# Spec Delta: itinerary-orchestration

## MODIFIED Requirements

### Requirement: Ranking
The system SHALL rank itineraries by **validated landed cost** ascending (NOT
airfare), then apply preference scoring to reorder within the honestly-priced
set. LEAD and VALIDATION_FAILED itineraries remain ranked separately from
VALIDATED ones and only VALIDATED itineraries are eligible to be labeled a
recommendation.

#### Scenario: Landed-cost ranking with preferences
- **WHEN** a result set contains VALIDATED itineraries with differing landed
  costs and friction attributes
- **THEN** they are ordered by landed cost, then nudged by soft preferences,
  with HARD NO items already filtered and HARD YES items constructed
- **AND** the cheapest VALIDATED landed-cost option that satisfies hard
  constraints is identifiable

### Requirement: Preference-driven stopover construction
The orchestration matrix SHALL support injecting a stopover leg into a structure
when the stopover axis is HARD YES, generating fare queries for the
SJO→[stopover] and [stopover]→[gateway] segments and pricing the stopover
lodging into landed cost.

#### Scenario: Constructed stopover priced end to end
- **WHEN** HARD YES stopover names Madrid
- **THEN** the system prices SJO→MAD and MAD→[Italy gateway] as separate legs
  with a 1-night gap
- **AND** adds the user-owned lodging assumption to landed cost
- **AND** ranks the result against other VALIDATED options on landed cost
