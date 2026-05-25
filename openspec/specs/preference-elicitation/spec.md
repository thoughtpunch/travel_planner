# preference-elicitation Specification

## Purpose

Elicit traveler preferences as a single bookended scale per friction axis
(HARD NO → soft middle → HARD YES), with global defaults and per-leg
overrides. The two ends are categorically different operations from the
soft middle: HARD NO filters; HARD YES constructs; the soft middle is
ranking weight only.

## Requirements

### Requirement: Bookended single-scale preference per axis

Each friction axis SHALL be expressed on ONE bookended scale, replacing
any earlier design that separated direction and importance:

```
HARD NO ── strongly avoid ── avoid ── neutral ── desire ── strongly desire ── HARD YES
```

The scale has exactly seven discrete positions. The two ends are
categorically different operations from the soft middle:

- **HARD NO** = hard filter (results lacking the attribute survive; results
  exhibiting it are excluded from the result set).
- **soft middle** (strongly avoid · avoid · neutral · desire · strongly
  desire) = ranking weight only; nothing is excluded and nothing is
  constructed.
- **HARD YES** = leg constructor (the system injects the desired feature
  into the itinerary structure and searches for it; see
  `preference-scoring`). NOT a filter.

#### Scenario: Soft preference reorders without excluding

- **WHEN** an axis is set to "strongly avoid" (a soft-middle position,
  not HARD NO)
- **THEN** itineraries exhibiting that attribute still appear in results,
  ranked lower and flagged with the friction attribute
- **AND** none are excluded from the result set

#### Scenario: HARD NO excludes

- **WHEN** the layover-length axis is set to HARD NO with a threshold
  (e.g. "no layovers > 3h")
- **THEN** itineraries with any segment layover exceeding the threshold
  are removed from the result set
- **AND** the run's results payload includes a `filtered_out_count` field
  summarising how many were removed by HARD NO filters (per axis)

#### Scenario: HARD YES constructs rather than filters

- **WHEN** the stopover axis is set to HARD YES
- **THEN** the system injects a stopover leg into the itinerary structure
  and searches for it (see `preference-scoring` Requirement: The
  no=filter / yes=construct duality)
- **AND** the system does NOT filter out the non-stopover candidate set
  as a side effect of the HARD YES itself

### Requirement: Friction axes (v1 set)

The system SHALL elicit these axes, each on the bookended scale:

1. **Transfer length** — ground leg duration to the true destination
   after landing at the gateway.
2. **Layover length** — gaps within a single travel day at intermediate
   airports.
3. **Stopover (24h+ intentional gap)** — the bidirectional axis that
   motivates the HARD YES / HARD NO distinction.
4. **Number of plane changes** — distinct from layover length; counts
   segments minus 1.
5. **Red-eye / arrival time-of-day** — local arrival time at any leg's
   destination falling within a configurable "red-eye" window (default
   23:00 – 06:00 local).

Each axis SHALL declare whether HARD YES is meaningful for it. Only
`stopover` has a meaningful HARD YES in v1; the others SHALL grey out or
hide the HARD YES tick in the elicitation UI and reject HARD YES values
at the API boundary.

#### Scenario: Axis left unset

- **WHEN** a user does not set an axis
- **THEN** the global default for that axis applies
- **AND** if no global default is set, the axis is `neutral` (ignored in
  scoring)

#### Scenario: HARD YES on a non-constructable axis is rejected

- **WHEN** a user attempts to set the layover-length axis to HARD YES
- **THEN** the elicitation UI greys out the HARD YES tick
- **AND** the API validates the same constraint server-side and returns
  a structured validation error

### Requirement: Global defaults with per-leg overrides

Preferences SHALL have a global default set scoped to the config. Each
leg MAY carry per-leg overrides for any subset of the axes; an axis not
overridden inherits the global default.

#### Scenario: Per-leg override

- **WHEN** the user sets a relaxed global stance ("avoid long layover"
  globally) but overrides the return leg (DC → SJO) to HARD NO long
  layover
- **THEN** the override applies to the return-leg fare queries and
  ranking only
- **AND** the other legs continue to use the global "avoid" weighting

#### Scenario: Override clearing returns to global default

- **WHEN** a per-leg override is cleared
- **THEN** that leg inherits the global default for that axis
- **AND** the UI shows the inheritance ("inheriting global: avoid")

### Requirement: HARD YES stopover requires a location input

A HARD YES on the stopover axis SHALL require either (a) a named stopover
city (IATA or city name resolvable to one or more airports), or (b)
explicit consent to sweep a candidate set of natural waypoint cities on
the path.

#### Scenario: Named stopover city

- **WHEN** the user sets HARD YES stopover and names a city (e.g. Madrid)
- **THEN** the system constructs legs routing through that city (SJO →
  MAD, MAD → [Italy gateway]) and prices them as separate legs with a
  1-night gap
- **AND** the stopover lodging assumption from `landed-cost-model` is
  added to landed cost for the constructed itinerary

#### Scenario: No city named — sweep prompt

- **WHEN** the user sets HARD YES stopover without naming a city
- **THEN** the system prompts (in the UI) to either name one or sweep a
  small candidate set of sensible waypoints on the path (e.g. {MAD, LIS,
  LHR, FRA} for a SJO → Italy transatlantic)
- **AND** if sweeping, each candidate stopover is constructed and priced,
  and the resulting itineraries are ranked against each other and against
  direct options on landed cost
- **AND** the waypoint candidate set is user-editable; an LLM MAY suggest
  the seed set but the user confirms

### Requirement: Incoherent combinations are guarded

The elicitation UI SHALL prevent or warn on incoherent settings,
server-side validation SHALL reject them at the API boundary, and the run
pipeline SHALL refuse to start with incoherent preferences.

#### Scenario: HARD YES on an axis that does not admit it

- **WHEN** the API receives preferences with HARD YES on (e.g.)
  `plane_changes`
- **THEN** the request is rejected with a structured validation error
  naming the offending axis and the reason

#### Scenario: HARD NO on every axis leaves an empty candidate space

- **WHEN** the combination of HARD NOs would mathematically exclude every
  possible itinerary
- **THEN** the run completes with `failed_query_count` summarising what
  was filtered and the UI surfaces an "all candidates filtered by HARD NO
  settings — consider relaxing X" message
- **AND** the run is NOT marked as a system failure; it is a
  configuration outcome
