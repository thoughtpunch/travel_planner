## MODIFIED Requirements

### Requirement: Bookended preference scale control

The wizard SHALL use a first-party `BookendedScale` Vue component for every preference axis. Each rendered scale SHALL include:

- A **visible axis label** rendered as an `<h3>` heading (e.g. "Layover length"). The `aria-labelledby` of the scale points to this heading.
- A **visible per-axis question** rendered as a `<p>` paragraph underneath the heading, in muted body text (e.g. "How long are you willing to sit in an airport between flights?"). This question is non-optional in v1 — every axis MUST supply one. A missing question is a defect.
- The seven-position scale itself: a PrimeVue `Slider` with `step=1`, `min=0`, `max=6`, with two end `Tag`s (HARD NO red, HARD YES green) visually distinct from the soft middle.
- A greyed-out HARD YES end with `pi-lock` icon and explanatory `Tooltip` when the axis declares `hard_yes_admitted = false`.
- Context inputs revealed conditionally: HARD NO with a threshold axis reveals an `InputNumber` for the threshold; HARD YES on `stopover` opens a `Dialog` ("Name a stopover city, or sweep candidates?").
- Full keyboard operability via the underlying `Slider`.

The component SHALL be exercised by Vitest unit tests that assert the `<h3>` and `<p>` are present in the rendered output, the HARD YES end is locked when not admitted, and the HARD NO threshold input appears on demand.

#### Scenario: Every axis shows a visible label and question

- **WHEN** the wizard's Preferences step renders
- **THEN** each `BookendedScale` row has a visible `<h3>` axis label (e.g. "Layover length", "Stopover (24h+ rest break in another city)")
- **AND** each row has a visible `<p>` question describing what the axis asks
- **AND** an axis rendered without a question fails a Vitest unit assertion

#### Scenario: HARD YES on a non-admitted axis is unreachable

- **WHEN** the layover-length axis renders
- **THEN** the HARD YES end is greyed out with a `lock` icon and a tooltip explaining it is not meaningful for layover length

#### Scenario: HARD YES stopover opens dialog

- **WHEN** the operator places the stopover axis at HARD YES
- **THEN** a `Dialog` opens asking to name a city or sweep candidates, and the choice writes into `preferences.stopover_target` on the config

### Requirement: Config wizard

The wizard SHALL use a PrimeVue `Stepper` with five steps (Trip basics, Dates & legs, Preferences, Cost assumptions, Review & run). Wizard state SHALL be persisted server-side on every change via `PATCH /api/configs/{id}` (debounced 500ms). The Dates & legs step SHALL be operable on a draft config — the operator MUST be able to advance from it to a runnable config without dropping out of the SPA.

The v1-minimum implementation of Dates & legs SHALL be a leg-template picker: a `SelectButton` (or `Select`) over the seeded `leg_templates` from `search-config`, with an "Apply template" action that calls `POST /api/configs/{id}/apply_template`. After application, the step SHALL render a read-only summary card per leg (origins, destinations, anchor date, window days, sampling strategy) and an "Apply a different template" affordance.

Full in-place leg editing is explicitly NOT required for v1 and lands as a follow-up.

#### Scenario: Draft trip has a leg template picker on Dates & legs

- **WHEN** the operator advances to the Dates & legs step on a draft trip with `config.legs` empty
- **THEN** the step renders a `SelectButton` (or `Select`) of the seeded leg templates with a short description each
- **AND** an "Apply template" `Button` is disabled until a template is selected
- **AND** there is no "leg editing is read-only" dead-end Message

#### Scenario: Template application creates legs and renders summary

- **WHEN** the operator picks `three_one_ways_to_italy` and clicks "Apply template"
- **THEN** `POST /api/configs/{id}/apply_template {name: "three_one_ways_to_italy"}` is fired
- **AND** the response includes a config with three `Leg` rows matching the template
- **AND** the step re-renders with one read-only summary card per leg showing origins, destinations, anchor date, window days, sampling strategy
- **AND** the Next button is now enabled

#### Scenario: Re-applying a different template replaces existing legs

- **WHEN** the operator has previously applied a template and selects a different one
- **THEN** clicking "Apply template" replaces all `Leg` rows on the config
- **AND** the summary re-renders with the new template's legs
- **AND** a `Toast` confirms the replacement
