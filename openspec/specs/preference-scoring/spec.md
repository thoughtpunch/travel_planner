# preference-scoring Specification

## Purpose

Apply elicited preferences to reorder an honestly-priced result set.
Preferences NEVER mutate any cost figure. HARD NO acts on the result set
(filter); HARD YES acts on the itinerary structure (construct); the soft
middle acts on rank order within a bounded cost band.

## Requirements

### Requirement: Cost spine computed before preference scoring

Landed cost SHALL be computed honestly and completely (airfare + transfer
+ any lodging, per `landed-cost-model`) BEFORE any preference scoring is
applied. Preference scoring SHALL NOT mutate any cost figure. The runner
pipeline order SHALL be: `sweep → validate → compute landed cost →
filter (HARD NO) → score (soft middle) → rank → persist`. Stopover
construction (HARD YES) SHALL run *before* the sweep step as a structural
addition to the query matrix, not as a scoring transform.

#### Scenario: Desired stopover is not double-counted

- **WHEN** an itinerary has a stopover the user desires (stopover axis
  set to "strongly desire" or HARD YES)
- **THEN** its stopover lodging is already included in its landed cost
  via `landed-cost-model`
- **AND** the desire preference only reorders ranking; it does NOT
  discount the lodging or otherwise reduce the cost to favour the
  itinerary
- **AND** the itinerary is never made to "look cheaper" by virtue of its
  desirability

#### Scenario: Pipeline-order invariant test

- **WHEN** the runner test suite executes
- **THEN** an integration test SHALL assert that the landed-cost field on
  every persisted itinerary is identical whether preferences are applied
  or not
- **AND** the only field that changes when preferences are applied is the
  `rank` and the `preference_explanations` payload

### Requirement: The no=filter / yes=construct duality

The two hard ends of the preference scale SHALL be implemented as distinct
operations over distinct objects:

- **HARD NO** operates on the **result set** (subtractive: exclude
  matching itineraries from the ranked output).
- **HARD YES** operates on the **itinerary structure** (additive:
  construct the feature as a leg, then run the entire sweep / validate /
  landed-cost / score pipeline on the constructed itinerary so it is
  comparable to others).

#### Scenario: HARD NO does not construct

- **WHEN** any axis is HARD NO
- **THEN** the system only filters; it never adds legs or modifies the
  query matrix
- **AND** HARD NO on `stopover` simply excludes any constructed-or-organic
  stopover itinerary; it does not exclude direct itineraries

#### Scenario: HARD YES does not filter the base set

- **WHEN** the stopover axis is HARD YES
- **THEN** the system constructs stopover itineraries and searches them
- **AND** does not silently delete the user's other candidate itineraries
  merely because they lack a stopover (the user chose construct, not
  filter)
- **AND** the result set contains both the constructed stopover
  candidates AND the organic direct candidates, ranked together on
  landed cost

### Requirement: Soft scoring is asymmetric and bounded

In the soft middle of the scale, "desire" SHALL act only as an attractor
(rank up) and "avoid" only as a detractor (rank down). The soft-scoring
effect SHALL be bounded so it cannot overcome a meaningful landed-cost
difference unintentionally — a $500 landed-cost gap should not be hidden
by a stack of soft-desire boosts.

The bound SHALL be: soft preferences can reorder itineraries within a
configurable percentage band of landed cost (default ±10% of the cheapest
VALIDATED itinerary's landed cost). Outside that band, landed cost wins.

#### Scenario: Strongly desire vs HARD YES distinction

- **WHEN** stopover is "strongly desire" (the rightmost soft position)
- **THEN** both stopover and non-stopover itineraries appear; stopover
  ones rank higher within the soft-band of landed cost
- **WHEN** stopover is HARD YES
- **THEN** the system constructs stopover routes specifically and prices
  them; they appear alongside direct routes ranked on landed cost

#### Scenario: Soft preferences cannot hide a large cost gap

- **WHEN** itinerary A has landed cost $5,000 and zero friction matches
- **AND** itinerary B has landed cost $6,200 and matches every
  soft-desire axis
- **AND** the cheapest VALIDATED landed cost is $5,000 and the soft band
  is ±10% ($4,500 – $5,500)
- **THEN** B is outside the soft band and SHALL be ranked below A on
  landed cost regardless of its soft-desire matches
- **AND** the UI may surface B as a "preference match outside the cost
  band" so the user can still find it

### Requirement: Ranking output is honest about spine vs. preference

The results payload and any UI presentation SHALL show landed cost (the
spine) as the primary sortable figure, with friction attributes (transfer
length, layover length, plane changes, red-eye, stopover) shown as
labeled columns or flags, and the preference-driven reorder applied on
top — never blended into a single opaque score.

Every ranked itinerary SHALL carry a `preference_explanations` array
describing which preferences nudged it up or down and by how much, so the
user can interrogate the rank decision.

#### Scenario: Mixed result presentation

- **WHEN** results are shown
- **THEN** each itinerary displays its landed cost, its component
  breakdown (fare / transfer / lodging), and its friction attributes
  (each as a labeled column or chip)
- **AND** the preference-driven rank order is applied
- **AND** the underlying cost figure and individual friction attributes
  remain visible per itinerary
- **AND** the user can re-sort by landed cost alone to see the cost-only
  ranking

#### Scenario: Explanation per ranked itinerary

- **WHEN** an itinerary is ranked above another despite higher landed
  cost (because it sits inside the soft band and matches a soft-desire
  axis)
- **THEN** its `preference_explanations` array contains an entry like
  `{axis: "stopover", direction: "desire_match", rank_delta: +2, reason:
  "soft desire honored within ±10% landed-cost band"}`
- **AND** this is renderable in the UI as a tooltip or expandable row
