## ADDED Requirements

### Requirement: Leg templates

The system SHALL ship a curated set of **leg templates** — named, pre-canned leg arrangements that a wizard can apply to a config to skip per-leg manual setup. Each template SHALL declare: `name`, `description`, `structures` (which Structure values it produces), and a `legs` list where each leg carries `ordinal`, `origins`, `destinations`, `date_anchor_offset_days` (relative to the application date), `window_days`, and `sampling_strategy`.

v1 SHALL seed these two templates:

- `three_one_ways_to_italy` — Structure A; SJO → {VCE, MXP, LIN, BLQ, VRN, TRS, ZRH, MUC} → {IAD, DCA, BWI} → SJO; default outbound ~+120 days, mid-leg ~+180 days, return ~+220 days; window 7 days; anchor,+/-3,+/-7 sampling.
- `nested_envelope_italy` — Structure B; SJO ⇄ DC outer round-trip + DC ⇄ Italy inner round-trip; tight 5-day windows; anchor sampling.

Templates SHALL live in `app/data/leg_templates.py` as plain Python constants — same "curated tables of stable knowledge" pattern as the gateway-transfer table.

#### Scenario: Template is retrievable from the API

- **WHEN** a client requests `GET /api/leg_templates`
- **THEN** the response lists every seeded template with `name`, `description`, `structures`, and a preview of the legs (origins / destinations only; dates are computed at apply-time)

#### Scenario: Applying a template writes legs to the config

- **WHEN** a client POSTs `/api/configs/{id}/apply_template` with `{name: "three_one_ways_to_italy"}` and an optional `anchor_date` (defaults to today)
- **THEN** the server replaces the config's `Leg` rows with the template's legs, computing each leg's `date_anchor` as `anchor_date + offset_days`
- **AND** the response is the full updated config (same shape as `GET /api/configs/{id}`)
- **AND** any prior legs on the config are deleted in the same transaction

#### Scenario: Unknown template name is rejected

- **WHEN** a client POSTs `/api/configs/{id}/apply_template` with `{name: "does_not_exist"}`
- **THEN** the response is 422 with a structured error naming the unknown template
- **AND** the config's legs are not modified
