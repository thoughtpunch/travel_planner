## ADDED Requirements

### Requirement: Landed cost replaces airfare as the cost of an itinerary

The cost of an itinerary SHALL be its **landed cost** — the total cost for the full party to reach the true destination — not airfare alone. Landed cost SHALL be the sum of validated party airfare + per-person ground transfer to the true destination × party size + any forced or intentional stopover lodging. Landed cost SHALL be the ranking key in `itinerary-orchestration`, replacing the previous airfare ranking.

#### Scenario: Cheaper fare loses on landed cost

- **WHEN** itinerary X (validated fare $900 / person to Rome, party of 6) and itinerary Y (validated fare $1,200 / person to Venice, party of 6) are compared
- **AND** X requires a Rome → Venice rail transfer at $50 / person for 6 people ($300)
- **THEN** the system ranks them by landed cost ($5,700 vs $7,200) — X still wins, but only on a number the user can interrogate
- **AND** if Rome's arrival forces an overnight, the lodging assumption is added to X's landed cost before comparison

#### Scenario: Landed cost is shown with component breakdown

- **WHEN** an itinerary's landed cost is reported (in the API payload or UI)
- **THEN** the breakdown lists each component (airfare, ground transfer, lodging) with the per-person figure, the party multiplier, and the data source for each
- **AND** the components sum to the landed-cost total displayed

### Requirement: Ground transfer model per gateway

Each candidate arrival gateway SHALL carry a transfer model to the true destination consisting of: available modes (rail / ferry / bus / drive), per-person cost, duration, number of transfers, a `last_reviewed` date, and the local time-of-day after which onward transfer is no longer viable (the `last_viable_onward_local_time`).

The `forces_overnight` flag for a *specific itinerary* SHALL be derived from that itinerary's arrival time vs. the gateway's `last_viable_onward_local_time`, NOT pre-baked into the transfer table.

#### Scenario: Gateway with viable same-day transfer

- **WHEN** a Northern Italy gateway (e.g. Milan MXP, Verona VRN, Bologna BLQ, Treviso TSF) is evaluated for an itinerary arriving at 14:30 local
- **AND** the gateway's `last_viable_onward_local_time` is 22:00
- **THEN** the transfer model provides a same-day onward option with cost and duration
- **AND** the itinerary's `forces_overnight` flag is `false`

#### Scenario: Gateway whose arrival forces an overnight

- **WHEN** an itinerary arrives at 23:45 local at a gateway whose `last_viable_onward_local_time` is 22:00
- **THEN** `forces_overnight = true` for that itinerary
- **AND** a lodging cost component is added to its landed cost using the user-owned per-night assumption × 1 night × party rooms
- **AND** the breakdown labels the lodging line "forced overnight — arrival after last viable onward transfer"

### Requirement: Ground-transfer data is a hardcoded table for v1

Ground-transfer cost, duration, transfer count, and `last_viable_onward_local_time` figures SHALL be a maintained hardcoded table per gateway (v1), NOT scraped live. Each entry SHALL be labeled with a `last_reviewed` date that propagates to every cost figure derived from it.

#### Scenario: Transfer figure shown with its review date

- **WHEN** a transfer cost contributes to an itinerary's landed cost
- **THEN** it is shown as a labeled assumption with its `last_reviewed` date inline (e.g. "MXP → VCE rail: $42 / person · reviewed 2026-04-12")
- **AND** the user can see that this is table data, not a live quote

#### Scenario: Multiple modes for one gateway

- **WHEN** a gateway has more than one viable transfer mode (e.g. TRS → Venice has rail and ferry)
- **THEN** the table carries both entries
- **AND** the cheapest viable mode for the itinerary's arrival time is selected for landed-cost computation
- **AND** the breakdown names the mode used

### Requirement: Cost components are honest, explicit, and user-overridable

Every component entering landed cost SHALL be (a) user-overridable, (b) visibly labeled with its data source (validated quote / table figure with date / user assumption / LLM-suggested estimate), and (c) NEVER silently model-generated.

An LLM MAY pre-fill a suggested value but the value SHALL be labeled "rough estimate, verify" wherever displayed AND the user SHALL be able to accept, edit, or clear it before it contributes to a ranked landed cost.

#### Scenario: Stopover lodging assumption

- **WHEN** an itinerary includes a stopover requiring lodging
- **THEN** the lodging cost uses a user-owned per-night family-room assumption (stored on the config, snapshotted into the run)
- **AND** the value is displayed wherever landed cost appears (e.g. "stopover lodging assumption: $320 / night · your estimate")
- **AND** if an LLM pre-filled it, the label states it is an unverified estimate until the user confirms or edits

#### Scenario: Forbidden silent estimate

- **WHEN** any cost component is generated by a model without a label, OR is generated by a model in a way that the user cannot override
- **THEN** this SHALL be treated as a defect; the system SHALL NOT enter such a value into landed cost
- **AND** integration tests SHALL assert that every landed-cost component on a result has a non-empty `data_source` field and a `user_overridable: true` flag

#### Scenario: Last-mile override per assumption

- **WHEN** the user wants to test "what if rail is actually $60 / person not $42"
- **THEN** they can override the figure at the assumption level (config or per-run) without editing the underlying table
- **AND** the override is labeled "your override of the table figure" and the original table figure remains visible
