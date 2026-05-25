# Spec Delta: preference-elicitation

## ADDED Requirements

### Requirement: Bookended single-scale preference per axis
Each friction axis SHALL be expressed on ONE bookended scale, replacing separate
direction and importance scales:

```
HARD NO ── strongly avoid ── avoid ── neutral ── desire ── strongly desire ── HARD YES
```

The two ends are categorically different operations from the soft middle:
- **HARD NO** = hard filter (results lacking-the-attribute survive; results with
  it are excluded).
- **soft middle** (strongly avoid … strongly desire) = ranking weight only;
  nothing is excluded or constructed.
- **HARD YES** = leg constructor (the system builds the desired feature into the
  itinerary structure and searches for it); NOT a filter.

#### Scenario: Soft preference reorders without excluding
- **WHEN** an axis is set to "strongly avoid" (soft, not HARD NO)
- **THEN** itineraries with the attribute still appear, ranked lower and flagged
- **AND** none are excluded

#### Scenario: HARD NO excludes
- **WHEN** an axis is set to HARD NO (e.g. layover length)
- **THEN** itineraries exhibiting that attribute are removed from results

#### Scenario: HARD YES constructs rather than filters
- **WHEN** the stopover axis is set to HARD YES
- **THEN** the system injects a stopover leg into the itinerary structure and
  searches it (see preference-scoring)
- **AND** does NOT filter out the non-stopover candidate set as a side effect of
  the hard yes itself

### Requirement: Friction axes (v1 set)
The system SHALL elicit these axes, each on the bookended scale:
1. **Transfer length** — ground leg to the true destination after landing.
2. **Layover length** — gaps within a single travel day.
3. **Stopover (24h+ intentional gap)** — the bidirectional axis; the reason the
   scale ends differ.
4. **Number of plane changes** — distinct from layover length.
5. **Red-eye / arrival time-of-day** — e.g. avoid pre-dawn arrival with children.

#### Scenario: Axis left unset
- **WHEN** a user does not set an axis
- **THEN** the global default applies; if no default, the axis is neutral
  (ignored in scoring)

### Requirement: Global defaults with per-leg overrides
Preferences SHALL have a global default set, with optional per-leg overrides.

#### Scenario: Per-leg override
- **WHEN** the user sets a relaxed global stance but overrides the
  return leg (DC→SJO) to "strongly avoid long layover"
- **THEN** the override applies to that leg only; other legs use global defaults

### Requirement: HARD YES stopover requires a location input
A HARD YES on the stopover axis SHALL require either a named stopover city or
consent to sweep a candidate set of natural waypoint cities.

#### Scenario: Named stopover city
- **WHEN** the user sets HARD YES stopover and names a city (e.g. Madrid)
- **THEN** the system constructs legs routing through that city

#### Scenario: No city named
- **WHEN** the user sets HARD YES stopover without naming a city
- **THEN** the system prompts to either name one or sweep a small candidate set
  of sensible waypoints on the path
- **AND** if sweeping, ranks the resulting stopover itineraries against each
  other

### Requirement: Incoherent combinations guarded
The elicitation UI SHALL prevent or warn on incoherent settings.

#### Scenario: Max importance on a neutral stance
- **WHEN** a user attempts a setting equivalent to "I care intensely that I am
  neutral" (max importance, neutral direction)
- **THEN** the UI warns or prevents it as incoherent
