# web-ui Specification

## Purpose

Phase-2 Vue 3 + PrimeVue SPA: an LLM-orchestrated trip-planning workspace.
A trip = one Config + many Runs + a Shortlist + Notes. The UI surfaces the
orchestration model honestly — landed cost as a sortable spine, friction as
labelled columns, bookended preferences with categorical HARD NO / HARD YES
ends, and a structured-form-first LLM copilot that can never silently inject
a cost number. Phase-1 Jinja templates remain during the SPA buildout for
operator continuity and are removed in a follow-up after parity.

## Requirements

### Requirement: Vue 3 + PrimeVue SPA app shell

The system SHALL ship a Vue 3 + PrimeVue 4 Single Page Application as the operator UI, built with Vite + TypeScript + Pinia + Vue Router, themed by default with the PrimeVue `Aura` preset, with dark mode and responsive (desktop-first, tablet-friendly) layouts.

The app shell SHALL provide: a `Menubar` (top), a primary content area, a `Toast` host for notifications, a `ConfirmDialog` host for destructive-action confirmations, and a copilot Drawer toggle.

#### Scenario: Shell renders on entry

- **WHEN** an operator opens the SPA root
- **THEN** the app shell renders with the Menubar (logo, dashboard link, settings, dark-mode toggle, copilot toggle), and the content area showing the dashboard
- **AND** the shell is keyboard-navigable (Tab order: skip-link → Menubar → main content)

#### Scenario: Dark mode toggle

- **WHEN** the operator toggles dark mode in the Menubar
- **THEN** the theme switches immediately without page reload
- **AND** the choice persists in local storage

### Requirement: Dashboard with trip cards

The dashboard SHALL list the operator's trips as a `DataView` of cards (grid mode by default, list-mode toggleable). Each card shows the trip name, creation date, and notes preview. A "New trip" `Button` opens a create dialog and routes into the wizard.

#### Scenario: Empty state

- **WHEN** the operator has no trips
- **THEN** the dashboard renders an empty-state message explaining what a trip is
- **AND** a "New trip" button is visible

#### Scenario: Trip card click enters workspace

- **WHEN** the operator clicks a trip card
- **THEN** the SPA navigates to `/trips/{id}` (the trip workspace) with the Overview tab active

### Requirement: Trip workspace with tabs

The trip workspace SHALL persist a trip's full state across sessions, organised in a `TabMenu` with five tabs: Overview (latest-run summary + shortlist preview), Wizard (edit the trip's config), Runs (history of runs as a `DataTable`), Shortlist (saved itineraries), Notes (free-form `Textarea`).

The workspace header SHALL show the trip name (editable in place via `Inplace` + `InputText`), the config id, and a "Run now" `Button`.

#### Scenario: Run now from header

- **WHEN** the operator clicks "Run now" with a valid config
- **THEN** `POST /api/runs?config_id=...` is fired and the SPA navigates to the run results page

### Requirement: Config wizard

The wizard SHALL use a PrimeVue `Stepper` with five steps (Trip basics, Dates & legs, Preferences, Cost assumptions, Review & run). Wizard state SHALL be persisted server-side on every change via `PATCH /api/configs/{id}` (debounced 500ms), so the operator can leave and return without losing edits.

Each step SHALL surface inline validation errors as PrimeVue `Message` components.

#### Scenario: Preferences step renders one BookendedScale per axis

- **WHEN** the operator advances to the Preferences step
- **THEN** the step renders one `BookendedScale` per axis (transfer length, layover length, stopover, plane changes, red-eye) for global defaults
- **AND** an `Accordion` placeholder for per-leg overrides

#### Scenario: Cost assumptions step shows LLM-prefilled values with a verify tag

- **WHEN** the operator advances to the Cost assumptions step and a value was LLM-prefilled
- **THEN** the value is rendered with a `<DataSourceTag source="llm_estimate_unverified">` tag and a "verify" label until accepted or edited

#### Scenario: Review step shows dry-run preview

- **WHEN** the operator reaches the Review step
- **THEN** the SPA calls `GET /api/configs/{id}/preview` and renders the matrix size, the planned SerpAPI call floor, and the constructed-stopover count

### Requirement: Bookended preference scale control

The wizard SHALL use a first-party `BookendedScale` Vue component for every preference axis, built on PrimeVue primitives. The component SHALL:

- Render exactly seven discrete positions (`hard_no`, `strongly_avoid`, `avoid`, `neutral`, `desire`, `strongly_desire`, `hard_yes`).
- Visually distinguish the two ends (HARD NO / HARD YES) from the soft middle via colour + a `Tag` capsule.
- Grey out and label-with-tooltip the HARD YES end on axes whose schema declares `hard_yes_admitted = false`.
- Reveal a context input when needed: HARD NO with a threshold axis (e.g. layover length) reveals an `InputNumber` for the threshold; HARD YES on `stopover` opens a `Dialog` ("Name a stopover city or sweep candidates?") with an `AutoComplete` and a `Button` row.
- Be fully keyboard-operable via the underlying PrimeVue `Slider`.

#### Scenario: HARD YES on a non-admitted axis is unreachable

- **WHEN** the layover-length axis renders
- **THEN** the HARD YES end is greyed out with a `lock` icon and a tooltip explaining it is not meaningful for layover length

#### Scenario: HARD YES stopover opens dialog

- **WHEN** the operator places the stopover axis at HARD YES
- **THEN** a `Dialog` opens asking to name a city or sweep candidates, and the choice writes into `preferences.stopover_target` on the config

### Requirement: Run results page as interrogable spreadsheet

The run results page SHALL render results in a PrimeVue `DataTable` with: column sort, removable sort, scrollable rows, frozen columns (rank left, landed cost right), and per-row expansion via a Splitter detail sidebar that mirrors the selected row.

A cost-spine summary `Card` appears above the table with: cheapest VALIDATED landed cost, scraper call count, SerpAPI call count, and a soft-band `Knob` that re-applies preference scoring client-side without a re-run.

Required columns: rank (frozen), status (`StatusBadge`), structure, gateway (with stopover annotation), landed cost (frozen right), cost components (each with `DataSourceTag`), friction chips, rank-delta badge, save-to-shortlist action.

A CSV export `Button` exports the currently-visible rows.

#### Scenario: Sort by landed cost

- **WHEN** the operator clicks the Landed cost column header
- **THEN** rows reorder by landed cost ascending; second click descending; third clears sort

#### Scenario: Live soft-band re-score

- **WHEN** the operator drags the soft-band `Knob` from 10% to 5%
- **THEN** the rank order updates client-side immediately reflecting the tighter band
- **AND** a `Message` informs that this is a live preview, re-run to persist

#### Scenario: Save to shortlist

- **WHEN** the operator clicks "Save to shortlist" on a result row
- **THEN** `POST /api/trips/{id}/shortlist` is called and a `Toast` confirms

### Requirement: Live run streaming

The run results page SHALL subscribe to `GET /api/runs/{id}/stream` via SSE while the run is RUNNING. On status COMPLETE/FAILED it refetches the results payload. If SSE drops three times, the SPA falls back to polling `GET /api/runs/{id}/results` every 2s and surfaces a `Toast` describing the fallback.

#### Scenario: SSE drop falls back to polling

- **WHEN** the SSE connection drops three times in a row
- **THEN** the client transitions to 2s polling
- **AND** a `Toast` informs the operator of the fallback

### Requirement: Saved-itinerary shortlist with annotations

Each trip SHALL persist a shortlist of saved itineraries as a `DataView`. Each item shows the structure, gateway, landed cost, originating run id, and an editable `Textarea` for notes. Items can be removed; deletion confirms via `ConfirmPopup` is a future polish — minimum-viable in v1 is a direct delete with a `Toast` undo opportunity surfaced.

Saving an itinerary SHALL snapshot the full data immutably; future edits to the originating run or table SHALL NOT mutate the snapshot.

#### Scenario: Save from results

- **WHEN** the operator clicks "Save to shortlist" on a result row
- **THEN** the itinerary is snapshotted and added to the trip's shortlist
- **AND** a `Toast` confirms the save

#### Scenario: Annotate shortlist item

- **WHEN** the operator opens a shortlist item
- **THEN** a `Textarea` for notes appears and auto-saves on blur

### Requirement: Settings page

A Settings page SHALL provide tabs for: General (dark mode, currency display), LLM provider (copilot enable/disable), and About.

#### Scenario: Disable copilot

- **WHEN** the operator toggles "Copilot enabled" off in Settings
- **THEN** the copilot Drawer toggle disappears from the Menubar

### Requirement: Accessibility and theming

The SPA SHALL meet these accessibility requirements:

- Every interactive control has an ARIA label or accessible name.
- Keyboard navigation flows through the wizard, the BookendedScale (slider arrow keys), the DataTable rows, and the Drawer.
- `prefers-reduced-motion: reduce` disables non-essential transitions.
- Theme tokens live in a single CSS file (`src/theme.css`) so the entire palette can be re-skinned by editing tokens, not components.

#### Scenario: Reduced motion respected

- **WHEN** the operator's OS has reduce-motion enabled
- **THEN** the SPA disables non-essential transitions

### Requirement: Status, friction, and data-source badge system

The SPA SHALL provide a `BadgeKit` of utility components for visually enforcing the data-honesty contract:

- `<StatusBadge :status>` — VALIDATED / LEAD / etc. — colour + icon + label, consistent everywhere.
- `<FrictionChip :axis :value>` — labelled friction attribute (e.g. "layover 6h 40m").
- `<RankDeltaBadge :delta :reason>` — `+2` / `-1` etc., with hover tooltip.
- `<DataSourceTag :source>` — appears on every cost-component value.

Every cost figure rendered anywhere in the SPA SHALL carry a `DataSourceTag`.

#### Scenario: LLM estimate visibly labelled

- **WHEN** the wizard's cost-assumptions step displays an LLM-prefilled lodging value
- **THEN** the value is rendered with `<DataSourceTag source="llm_estimate_unverified">` and a "verify" label
