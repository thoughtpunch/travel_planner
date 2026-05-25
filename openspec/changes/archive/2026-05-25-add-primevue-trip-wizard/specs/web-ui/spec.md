## REMOVED Requirements

### Requirement: Phase-1 server-rendered UI

**Reason:** Superseded by the Phase-2 Vue 3 + PrimeVue SPA defined below. The Phase-1 Jinja shell was always documented as a one-cycle scaffold; the Phase-2 SPA is its replacement.

**Migration:** The Jinja templates under `app/templates/` remain during the SPA buildout for operator continuity. They are removed in a follow-up cleanup commit once the Phase-2 parity checklist clears (see `add-primevue-trip-wizard/tasks.md` §10).

## ADDED Requirements

### Requirement: Vue 3 + PrimeVue SPA app shell

The system SHALL ship a Vue 3 + PrimeVue 4 Single Page Application as the operator UI, built with Vite + TypeScript + Pinia + Vue Router, themed by default with the PrimeVue `Aura` preset, with dark mode and responsive (desktop-first, tablet-friendly) layouts.

The app shell SHALL provide: a `Menubar` (top), a collapsible `Drawer` (left nav), a primary content area, a `Toast` host for notifications, a `ConfirmDialog` host for destructive-action confirmations, and a `BlockUI` host for in-flight blocking operations (run kickoff).

#### Scenario: Shell renders on entry

- **WHEN** an operator opens the SPA root
- **THEN** the app shell renders with the Menubar (logo, dashboard link, settings, dark-mode toggle, copilot toggle, current quota usage), the Drawer (collapsed by default on desktop > 1280px, expanded with persistent state on first visit), and the content area showing the dashboard
- **AND** the shell is keyboard-navigable (Tab order: skip-link → Menubar → Drawer toggle → main content)

#### Scenario: Dark mode toggle

- **WHEN** the operator toggles dark mode in the Menubar
- **THEN** the theme switches immediately without page reload
- **AND** the choice persists in local storage

### Requirement: Dashboard with trip cards

The dashboard SHALL list the operator's trips as a `DataView` of cards (grid mode by default, list-mode toggleable). Each card shows: trip name, true destination, party summary, latest-run cost-spine snapshot (cheapest VALIDATED landed cost or "no runs yet"), latest-run age, and a `Tag` for any incomplete-structure flag. A "New trip" `Button` enters the wizard.

#### Scenario: Empty state

- **WHEN** the operator has no trips
- **THEN** the dashboard renders an empty-state `Card` with a "Create your first trip" `Button` that opens the wizard
- **AND** a brief explanation of what a trip is (config + runs + shortlist)

#### Scenario: Trip card click enters workspace

- **WHEN** the operator clicks a trip card
- **THEN** the SPA navigates to `/trips/{id}` (the trip workspace) with the Overview tab active

### Requirement: Trip workspace with tabs

The trip workspace SHALL persist a trip's full state across sessions, organised in a `TabView` with five tabs: **Overview** (latest-run summary + shortlist preview), **Wizard** (edit the trip's config), **Runs** (history of runs as a `DataTable`), **Shortlist** (saved itineraries as a `DataView` + `OrderList`), **Notes** (free-form `Textarea`).

The workspace header SHALL show: trip name (editable in place via `Inplace` + `InputText`), true destination, party, outbound + return date windows, and a "Run now" `Button` that fires the orchestrator on the current config.

#### Scenario: Tabs preserve state

- **WHEN** the operator switches from Runs to Shortlist and back
- **THEN** the Runs tab restores its prior sort/filter/expanded-row state
- **AND** unsaved Notes edits persist as draft and are not lost

#### Scenario: Run now from header

- **WHEN** the operator clicks "Run now" with a valid config
- **THEN** `POST /api/runs` is fired, a `Toast` confirms run-id, the Runs tab opens with the new run at the top, and a `BlockUI` covers the workspace for ≤2s during kickoff

### Requirement: Config wizard

The wizard SHALL use a PrimeVue `Stepper` with five steps (Trip basics, Dates & legs, Preferences, Cost assumptions, Review & run). Wizard state SHALL be persisted server-side on every change via `PATCH /api/wizard/{config_id}` (debounced 500ms), so the operator can leave and return.

Each step SHALL be reachable in any order once the prior step's required fields are valid; required-field validation SHALL be inline (PrimeVue field-level error rendering with `Message`).

#### Scenario: Trip basics step

- **WHEN** the operator enters the wizard's first step
- **THEN** the step renders fields: trip name (`InputText`), true destination (`InputText` + `AutoComplete` for city), party (`InputNumber` for adults, children, infants in seat, infants on lap)
- **AND** the Next button is disabled until trip name and true destination are non-empty and party total is ≥ 1

#### Scenario: Dates & legs step

- **WHEN** the operator advances to step 2
- **THEN** the step renders: outbound anchor (`Calendar`) + window (`Slider` ±days), return anchor + window, structure selection (`SelectButton` A / B / Both), per-leg candidate gateways (`MultiSelect` with `Chip` previews of selections)
- **AND** an inline `Message` warns if the date windows overlap implausibly or if a chosen structure has no candidate gateways for some leg

#### Scenario: Preferences step

- **WHEN** the operator advances to step 3
- **THEN** the step renders one `BookendedScale` per axis (transfer length, layover length, stopover, plane changes, red-eye) for global defaults
- **AND** a collapsed `Accordion` "Per-leg overrides" reveals the same axis set per leg when expanded, with an "inheriting global" hint per axis until overridden

#### Scenario: Cost assumptions step

- **WHEN** the operator advances to step 4
- **THEN** the step renders: stopover lodging per night (`InputNumber` with currency prefix), rooms (`InputNumber`, default 2), per-gateway transfer overrides (collapsed; opens an editable mini `DataTable`)
- **AND** any LLM-suggested value is rendered with a `Tag` "suggested — verify" until accepted or edited

#### Scenario: Review & run step

- **WHEN** the operator reaches step 5
- **THEN** the step renders a read-only `Card` summary of the assembled config + a `Card` showing dry-run preview (matrix size, estimated SerpAPI call count, number of constructed stopover candidates) from `GET /api/configs/{id}/preview`
- **AND** a "Run" `Button` fires `POST /api/runs` and routes to the run results page

#### Scenario: Wizard durability

- **WHEN** the operator edits a field and closes the tab without explicitly saving
- **THEN** the change has already been PATCHed server-side
- **AND** re-opening the trip's wizard tab restores the exact prior state

### Requirement: Bookended preference scale control

The wizard SHALL use a first-party `BookendedScale` Vue component for every preference axis, built on PrimeVue primitives. The component SHALL:

- Render exactly seven discrete positions (`hard_no`, `strongly_avoid`, `avoid`, `neutral`, `desire`, `strongly_desire`, `hard_yes`).
- Visually distinguish the two ends (HARD NO / HARD YES) from the soft middle via colour + a `Tag` capsule, NOT via slider colour alone.
- Grey out and label-with-tooltip the HARD YES end on axes whose schema declares `hard_yes_admitted = false`.
- Reveal a context input when needed: HARD NO with a threshold axis (e.g. layover length) reveals an `InputNumber` for the threshold; HARD YES on `stopover` opens a `Dialog` ("Name a stopover city or sweep candidates?") with `AutoComplete` and `Button` row.
- Be fully keyboard-operable (arrow keys move position; Enter on HARD YES opens the dialog; Esc closes).
- Have minimum 44px touch targets on each tick.

#### Scenario: HARD YES on a non-admitted axis is unreachable

- **WHEN** the layover-length axis renders
- **THEN** the HARD YES end is greyed out with a `lock` icon and a `Tooltip` "HARD YES is not meaningful for layover length — set a HARD NO threshold instead"
- **AND** keyboard navigation cannot place the position on HARD YES (the right-arrow stops at "strongly desire")

#### Scenario: HARD NO with threshold

- **WHEN** the operator places the layover-length axis at HARD NO
- **THEN** an `InputNumber` "Filter out any layover longer than [hh:mm]" appears beside the scale
- **AND** the form is invalid until the threshold is set

#### Scenario: HARD YES stopover opens dialog

- **WHEN** the operator places the stopover axis at HARD YES
- **THEN** a `Dialog` opens: "Name a stopover city, or let the system sweep candidates?" with an `AutoComplete` (IATA/city resolver), a "Sweep candidates" `Button`, and a "Cancel" `Button`
- **AND** confirming a city writes `{value: 'hard_yes', stopover_target: {city: ...}}`; confirming sweep writes `{value: 'hard_yes', stopover_target: {sweep_candidates: [...]}}`; cancel restores the prior position

### Requirement: Run results page as interrogable spreadsheet

The run results page SHALL render results in a PrimeVue `DataTable` with built-in: column sort (single + multi), header filters per column, column reorder, column freeze (left and right), column show/hide via `OverlayPanel`, row grouping by structure (toggleable), row expansion (cost breakdown + leg `Timeline` + preference explanations), and CSV export. The DataTable view state (column order, visibility, sort, filters) SHALL be persisted in local storage scoped to the trip id.

Above the DataTable SHALL appear: a `Card` cost-spine summary (cheapest VALIDATED landed cost, by-structure verdicts, scraper / SerpAPI call counts, run timestamp), and a `Knob` (or `Slider`) for live tuning of the soft-band ±% (default 10%) that re-applies preference scoring client-side without a re-run.

The table SHALL be laid out inside a `Splitter`, with the table on the left (~60%) and a detail sidebar on the right (~40%) that reflects the currently-selected row. The detail sidebar SHALL show: cost-breakdown `Card`, leg-by-leg `Timeline`, preference-explanations list, "Save to shortlist" `Button`.

Required columns (each with the named built-in behaviours):
- Rank (frozen left, sort: rank)
- Status (`StatusBadge`, filter: `MultiSelect`)
- Structure (filter: `MultiSelect`)
- Carrier
- Origin → Gateway (with stopover `Chip` if constructed)
- Outbound date, Return date
- **Landed cost** (frozen right, sort: numeric, primary visual emphasis)
- Airfare component, Transfer component, Lodging component (each with `DataSourceTag`)
- Friction: layover max minutes (sort: numeric, filter: `Slider` range), stops (count), red-eye (`Tag` if true), forces overnight (`Tag` if true)
- Preference rank-delta (`RankDeltaBadge` with `Tooltip` → explanations)
- Actions: Save (`Button`), View detail (`Button`)

#### Scenario: Sort by landed cost

- **WHEN** the operator clicks the Landed cost column header
- **THEN** rows reorder by landed cost ascending; second click descending; third clears sort
- **AND** the column header shows a sort indicator

#### Scenario: Multi-column sort

- **WHEN** the operator Shift-clicks Structure then Landed cost
- **THEN** rows group sort by Structure first, then Landed cost within structure

#### Scenario: Filter friction columns

- **WHEN** the operator opens the layover column's header filter and sets max 240 minutes
- **THEN** the table hides rows with max layover > 240 min
- **AND** a `Tag` "1 filter active" appears in the table toolbar with a "Clear all filters" `Button`

#### Scenario: Live soft-band re-score

- **WHEN** the operator drags the soft-band `Knob` from 10% to 5%
- **THEN** the rank order updates client-side immediately (no API call) reflecting the tighter band
- **AND** a `Message` "Live preview — re-run to persist this band" hints at the difference between preview and persisted state

#### Scenario: Row expansion shows breakdown

- **WHEN** the operator clicks a row's expansion chevron
- **THEN** the row expands inline showing the cost-breakdown `Card`, leg `Timeline`, and `preference_explanations` list
- **AND** keyboard `Enter` on the focused row toggles the same expansion

#### Scenario: CSV export

- **WHEN** the operator clicks Export CSV
- **THEN** a CSV containing the currently-visible columns and currently-sorted/filtered rows downloads as `trip_<slug>_run_<id>.csv`

#### Scenario: View persistence

- **WHEN** the operator hides a column, reorders columns, and applies filters, then navigates away and back
- **THEN** the prior view state restores from local storage

### Requirement: Live run streaming

The run results page SHALL subscribe to `GET /api/runs/{id}/stream` via SSE and render rows incrementally as they arrive, with `Skeleton` placeholders for the cost-spine summary until the validation stage completes. A `ProgressBar` SHALL show stage progress (Sweep · Validate · Score · Done).

If the SSE connection drops, the client SHALL reconnect with exponential backoff up to 30s. If `EventSource` is unavailable or repeatedly fails, the client SHALL fall back to polling `GET /api/runs/{id}` every 2s until status is COMPLETE or FAILED.

#### Scenario: Live row arrival

- **WHEN** the operator opens a run results page while the run is still RUNNING
- **THEN** rows appear in the DataTable as they are validated, in their then-current rank order
- **AND** the cost-spine `Card` updates as the cheapest VALIDATED landed cost shifts
- **AND** the `ProgressBar` advances through Sweep → Validate → Score → Done

#### Scenario: SSE drop falls back to polling

- **WHEN** the SSE connection drops three times in a row
- **THEN** the client transitions to 2s polling
- **AND** a `Toast` informs the operator of the fallback

### Requirement: Saved-itinerary shortlist with annotations

Each trip SHALL persist a shortlist of saved itineraries. The shortlist tab SHALL render as a `DataView` (list mode default, grid mode toggleable) with `OrderList` for manual reorder, `Textarea` for per-item notes, `Chip` for per-item annotations (user-defined tags), and a `ContextMenu` (right-click) offering Re-order / Annotate / Delete / Re-run with these preferences.

Saving an itinerary SHALL snapshot the full data (fare ids, landed cost, breakdown, friction, originating run id, timestamp); future edits to the originating run's config or the gateway-transfer table SHALL NOT mutate the snapshot.

The shortlist SHALL be exportable as CSV (rows + notes column) for sharing.

#### Scenario: Save from results

- **WHEN** the operator clicks "Save to shortlist" on a result row
- **THEN** the itinerary is snapshotted and added to the trip's shortlist
- **AND** a `Toast` confirms the save with an "Undo" `Button` (5s)

#### Scenario: Annotate shortlist item

- **WHEN** the operator opens a shortlist item
- **THEN** a `Textarea` for notes and a `Chips` input for tags appear
- **AND** changes auto-save (PATCH per-item, debounced)

#### Scenario: Manual reorder via OrderList

- **WHEN** the operator drags a shortlist item to a new position via `OrderList`
- **THEN** the order persists server-side and survives page reload

#### Scenario: Delete with confirmation

- **WHEN** the operator clicks Delete on a shortlist item
- **THEN** a `ConfirmPopup` asks for confirmation before deletion
- **AND** an "Undo" `Toast` appears after deletion for 5s

#### Scenario: Re-run with item's preferences

- **WHEN** the operator selects "Re-run with these preferences" from the `ContextMenu`
- **THEN** the trip's current draft config is opened with the saved itinerary's originating preferences applied as a candidate override (user confirms before save)

### Requirement: Settings page

A Settings page SHALL provide tabs for: General (theme, dark mode, currency display), Default preferences (BookendedScale defaults applied to new trips), Default cost assumptions (lodging per night, rooms), Gateway-transfer table (read-only view of the seeded table with `last_reviewed` dates; CSV import for per-config overrides), LLM provider (Anthropic API key via `Password`, model selector via `Dropdown`, copilot enable/disable via `InputSwitch`), Status badge palette (`ColorPicker` per status for users with non-default colour vision needs), and About / quota status.

#### Scenario: Disable copilot

- **WHEN** the operator toggles "Copilot enabled" off in Settings
- **THEN** the copilot Drawer toggle disappears from the Menubar
- **AND** the wizard no longer offers copilot suggestions
- **AND** existing copilot-flagged fields remain (their `llm_suggested` flag is unchanged)

#### Scenario: Override status colour palette

- **WHEN** the operator opens Status badge palette and adjusts the VALIDATED colour
- **THEN** the new colour applies to every `StatusBadge` across the SPA immediately
- **AND** the choice persists in local storage

### Requirement: Accessibility and theming

The SPA SHALL meet these accessibility requirements:

- Every interactive control has an ARIA label or accessible name.
- Keyboard navigation flows through every interactive surface (wizard, BookendedScale, DataTable rows + headers, Drawer, Dialog, ContextMenu).
- Status colour palettes are distinguishable under monochromacy (red/green is never the only differentiator; icons + shape supplement colour).
- `prefers-reduced-motion: reduce` disables Stepper transitions, hover animations, and Skeleton shimmer.
- Theme tokens live in a single CSS file; the entire palette can be re-skinned by editing tokens, not components.

#### Scenario: Reduced motion respected

- **WHEN** the operator's OS has reduce-motion enabled
- **THEN** the SPA disables non-essential transitions (Stepper, Card hover, Skeleton shimmer)
- **AND** interactive feedback (button press, toast appearance) remains visible but uses instant transitions

#### Scenario: Keyboard-only wizard completion

- **WHEN** an operator completes the wizard using only keyboard
- **THEN** every step's fields and the BookendedScale are reachable via Tab / Shift+Tab
- **AND** the operator can submit the run from the Review step via keyboard alone

### Requirement: Status, friction, and data-source badge system

The SPA SHALL provide a `BadgeKit` of utility components for visually enforcing the data-honesty contract:

- `<StatusBadge :status="..." />` — VALIDATED / LEAD / VALIDATION_FAILED / STALE / SKIPPED_QUOTA / FAILED / BLACKOUT / LONG_GAP / INCOMPLETE — colour + icon + label.
- `<FrictionChip :axis="..." :value="..." />` — labelled friction attribute (e.g. "layover 6h 40m", "2 stops", "red-eye 04:15").
- `<RankDeltaBadge :delta :reason />` — `+2` / `-1` etc., with hover `Tooltip` revealing preference explanation.
- `<DataSourceTag :source="validated_quote | table_figure | user_assumption | user_override | llm_estimate_unverified" />` — appears on every cost-component value.

Every cost figure rendered anywhere in the SPA SHALL carry a `DataSourceTag`. This SHALL be enforced by a Vitest unit test that fails if a cost figure is rendered without one.

#### Scenario: LLM estimate visibly labelled

- **WHEN** the wizard's cost-assumptions step displays an LLM-prefilled lodging value
- **THEN** the value is rendered with `<DataSourceTag :source="llm_estimate_unverified" />` and a label "suggested — verify"
- **AND** editing or explicitly accepting the value swaps the tag to `user_assumption` and clears the unverified label

#### Scenario: Cost component without source is a defect

- **WHEN** the Vitest unit test renders any cost-breakdown component
- **THEN** every cost figure in the rendered output has an accompanying `DataSourceTag`
- **AND** the test asserts this; absence is a build failure
