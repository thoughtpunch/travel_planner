## Context

The Phase-1 Jinja UI is a developer-tier shell over a FastAPI process. It works for the operator (the person running the orchestrator on their own machine) but does not surface the planning model: a *trip* the user shapes over time, with preferences they iterate on, runs they compare, and a shortlist they curate. The Phase-1 spec explicitly anticipated this and reserved the Phase-2 SPA as a separate change. That change is this one, layered on `add-preference-weighted-landed-cost`'s new data contracts.

The design problem is not "render an itinerary list nicely." It is: **build a workspace where the user can shape the search, trust the numbers, and end up with a defensible decision.** Three product invariants drive every UI decision below:

1. **Cost is the honest spine.** Landed cost and its component breakdown are first-class everywhere they appear. Never collapsed into a single blended score, never relegated to a tooltip.
2. **Preferences are bookended.** The HARD NO / HARD YES distinction is categorical (different operations), and the UI must make that legible at a glance — not as labels on a slider, but as visually distinct controls.
3. **The LLM is a copilot, never an oracle.** Anything the copilot writes is visibly marked unverified until the user accepts it; the copilot can never silently inject a cost number.

## Goals / Non-Goals

**Goals:**
- A Vue 3 + PrimeVue SPA covering: dashboard / trip cards, trip workspace (multiple runs of one config), config wizard, run results spreadsheet, preference elicitation (global + per-leg), saved-itinerary shortlist with annotations, settings (defaults, gateway-transfer table, theme, LLM provider), and an LLM copilot embedded in the wizard.
- Full use of the PrimeVue component palette where it earns its place — DataTable for the results spreadsheet (sort, filter, freeze, group, expand, column-reorder, CSV export), Stepper for the wizard, Drawer for navigation, Splitter for table-plus-detail layouts, etc.
- Production-grade keyboard navigation, accessibility (ARIA + reduced motion + dark mode), and a single themable palette (Aura preset by default).
- A run-stream endpoint (SSE) so the user sees results populate live during the sweep+validate, not as a single delayed dump.

**Non-Goals:**
- Mobile-first. Tablet-friendly, phone-degraded — this is a planner's desk tool.
- Multi-tenant auth, signup flow, password reset. Single-operator boundary.
- Booking, holds, payment, vendor handoff. We rank.
- i18n. English-only v1.
- A consumer-style "search box → results" one-shot UX. The flow is wizard → run → results → save → iterate; that's the product.

## Information architecture

```
┌─ Dashboard ──────────────────────────────────────────────────────────────┐
│ Recent trips · New trip ── Settings ── LLM provider status                │
└──────────────────────────────────────────────────────────────────────────┘

Dashboard
├── Trip card grid (DataView in grid mode, switchable to list)
│   └── Trip card → Trip workspace
└── "New trip" → Wizard

Trip workspace ── trip = a Config + multiple Runs + a Shortlist
├── Header: trip name, true destination, party, date windows
├── Tabs: [Overview] [Wizard] [Runs] [Shortlist] [Notes]
│   ├── Overview: latest-run cost-spine summary + shortlist preview
│   ├── Wizard: edit the trip's config (same Stepper as new trip)
│   ├── Runs: DataTable of runs (status, top landed cost, scraper/serpapi calls, age) — row click → Run results
│   ├── Shortlist: DataView of saved itineraries (with notes, manual reorder via OrderList)
│   └── Notes: free-form Textarea per trip
└── Run results page (linked from Runs tab)
    ├── Header: cost-spine summary Card (cheapest VALIDATED landed cost), structure verdicts
    ├── Filters bar: status, structure, soft band slider, friction filters
    ├── Splitter: DataTable (left, ~60%) | Detail sidebar (right, ~40%)
    │   ├── DataTable: ranked itineraries; columns sortable/filterable/freezable
    │   └── Detail: cost breakdown + leg Timeline + preference explanations + Save-to-shortlist
    └── Bottom: quota / call counts, run timestamp, "Re-run with adjusted preferences"

Settings
├── General (theme, dark mode, units)
├── Default preferences (the BookendedScale axes the user wants pre-populated on new trips)
├── Default cost assumptions (lodging/night, rooms)
├── Gateway-transfer table (read-only; CSV import for overrides)
├── LLM provider (Anthropic key, model selection, copilot enable/disable)
└── About / version / quota status
```

## Decisions

### Decision 1: The wizard is a `Stepper`, not a single long form

PrimeVue `Stepper` with the following steps:
1. **Trip basics** — name, true destination (`InputText` + `AutoComplete` for city), party size (`InputNumber` with breakdown into adults/children/infants_in_seat/infants_on_lap).
2. **Dates & legs** — outbound anchor + window (`Calendar` range + `Slider` for ± days), return anchor + window, structure selection (`SelectButton`: A / B / Both), per-leg gateway candidates (`MultiSelect` with `Chip` preview).
3. **Preferences** — global defaults via `BookendedScale` per axis (transfer length, layover length, stopover, plane changes, red-eye). Below: an `Accordion` "Per-leg overrides" (collapsed by default) that, when expanded, shows the same BookendedScale set per leg with an "inheriting global" hint when un-overridden.
4. **Cost assumptions** — stopover lodging per night (`InputNumber` with currency), rooms (`InputNumber`, default 2), per-gateway transfer overrides (collapsed by default; opens a small editable `DataTable` over the gateway-transfer rows).
5. **Review & run** — read-only summary card showing the assembled config, a dry-run preview (matrix size, estimated SerpAPI call count, constructed-stopover count), and a "Run" button that fires `POST /api/runs`.

Step state is persisted server-side via `PATCH /api/wizard/{config_id}` on every change (debounced 500ms). The user can close the tab and come back; the wizard is durable. New trips start with a draft config id created on step 1.

Each step's `Card` has a header with the step title, an inline `Tag` if any field was LLM-suggested, and a footer with `Back` / `Next` `Button`s and a `Tooltip`-equipped help icon.

### Decision 2: The `BookendedScale` is a first-party component, not a `Slider` with labels

This is the load-bearing UX bet of the change. A raw `Slider` is wrong because:
- A 0-100 slider invites false precision.
- The HARD NO / HARD YES ends are categorically different from the soft middle; they need visual emphasis.
- HARD YES on a non-constructable axis must be greyed out — a slider does not have first-class disabled regions.

The component is composed of:
- A 7-tick horizontal `Slider` (`step=1`, `min=0`, `max=6`) with custom tick labels.
- A `Tag` at each end: `[ HARD NO ]` and `[ HARD YES ]` (each visually distinct from the soft-middle range).
- The current position's label below (live-updated).
- Where the axis declares `hard_yes_admitted = false`, the HARD YES end is rendered with reduced opacity, a `lock` icon, and a `Tooltip` ("HARD YES is not meaningful for layover length — set a HARD NO threshold instead").
- For HARD NO with a threshold (e.g. layover length), a secondary `InputNumber` appears when HARD NO is selected ("Filter out any layover longer than [3:00] hours").
- For HARD YES stopover, selecting that tick opens a `Dialog` asking "Name a stopover city or sweep candidates?" with an `AutoComplete` and a `Button` row.

The component emits `{position: 'hard_no'|...|'hard_yes', threshold?: any}` and is fully accessible via keyboard (arrow keys move the tick; Enter on HARD YES opens the dialog; Escape cancels).

A dedicated Vitest unit test asserts: (a) HARD YES is unreachable when `hard_yes_admitted = false`, (b) HARD NO with a layover axis requires a threshold before the form is valid, (c) the emitted value matches the underlying scale position.

### Decision 3: The results view is a spreadsheet, not a carousel

PrimeVue `DataTable` with `lazy=false` (the result set is small enough — tens to low hundreds of rows — to client-paginate) and the following:

- **Columns** (with sort, filter, reorder, freeze, toggle):
  - Rank (frozen left)
  - Status (`Tag` — VALIDATED green, LEAD amber, etc.)
  - Structure (A / B)
  - Carrier + flight count
  - Origin → Gateway (with `Chip` for stopover if constructed)
  - Outbound date
  - Return date (if applicable)
  - Landed cost (primary sort; sortable numerically) — frozen right
  - Airfare component
  - Transfer component
  - Lodging component (with "—" if none)
  - Friction: layover (max minutes, sortable), stops (count), red-eye (`Tag` if true), forces overnight (`Tag` if true)
  - Preference rank-delta (`Badge` with `+2` / `-1` etc., tooltip → preference_explanations)
  - Actions: Save to shortlist (`Button` icon), View detail (`Button` icon)

- **Header filters** (PrimeVue `DataTable` filter row):
  - Status `MultiSelect`
  - Structure `MultiSelect`
  - Landed cost `Slider` range
  - Friction axes: per-axis `MultiSelect` over `{none, mild, severe}` or a numeric range slider where applicable

- **Row grouping**: by Structure (A above B), toggleable.
- **Row expansion**: click the chevron to expand; the expanded row shows the cost-breakdown Card + leg Timeline + preference explanations list.
- **Column toggle**: a `OverlayPanel` triggered from a `Button` lets the user hide / show columns; persisted to local storage per trip.
- **CSV export**: built-in `DataTable` exportCSV; one click; downloads `trip_<name>_run_<id>.csv`.
- **Top of page** (above the table): a `Card` "cost spine summary" — cheapest VALIDATED landed cost, by-structure verdicts, scraper / SerpAPI call counts, run timestamp. Beneath: a `Knob` for the soft-band ± percentage (default 10%) that re-applies preference scoring client-side without a re-run, so the user can see how the rank order shifts.
- **Splitter**: the table is on the left of a `Splitter` (default 60%) with a detail sidebar on the right (40%) that mirrors whatever row is selected. The user can drag the splitter or collapse the detail pane.
- **Empty / error states**: `Message` components with the actual orchestrator error text (the user is the operator; they want the truth, not a friendly euphemism).

### Decision 4: The trip workspace is the persistent unit, not the run

A "trip" is the persistent object the user works in. It owns one Config, many Runs, one Shortlist, and free-form Notes. The dashboard is a grid of trip `Card`s; clicking one enters the trip workspace.

Inside the trip workspace, tabs (`TabView`) separate Overview / Wizard / Runs / Shortlist / Notes. The Wizard edits the trip's config in place; saving creates a new draft revision. Running fires the orchestrator with the current config and produces a Run, which appears in the Runs tab. The Shortlist is a DataView of saved itineraries (each carrying the originating run id) with `OrderList` for manual reorder, `Textarea` notes, and `Chip` annotations.

This is the central UX bet that distinguishes this tool from a comparator. The user is not running a one-shot search; they are iterating on a trip.

### Decision 5: The LLM copilot is a structured-form-first sidebar, not a chat

A `Drawer` opens from the right (toggle in the header) and contains a `Chatbot`-style interface — but the conversation is *constrained* to writing into the form. The copilot:

- May suggest values into specific form fields (e.g. "Based on 'family with toddlers', I'd suggest avoid red-eye, avoid long layovers. Apply?"). Each suggestion appears as an inline `Card` with `Accept` / `Edit` / `Reject` `Button`s.
- Each suggestion is bound to a form field. Accepting writes the value AND records that it was copilot-suggested (sets `llm_suggested.<field> = true` per `search-config`).
- The field shows a `Tag` "suggested — verify" until the user edits or explicitly confirms it. Editing the value clears the suggestion flag.
- The copilot CANNOT contribute to any cost figure without a label (enforced at the API boundary, per `wizard-copilot`).

This is the structured-form-first pattern: the form is the source of truth and is always editable directly; the copilot is one of several ways to populate it. Users who do not want the copilot disable it in Settings and the Drawer toggle hides.

### Decision 6: Live run via Server-Sent Events

`POST /api/runs` returns immediately with a run id. The results page opens with `Skeleton` placeholders and subscribes to `GET /api/runs/{id}/stream` (SSE). Each event delivers either:
- A new fare row (sweep stage),
- A validation result (validation stage),
- A landed-cost+preference scoring update (final stage),
- A status transition (PENDING → RUNNING → COMPLETE | FAILED).

`ProgressBar` at the top updates per-stage. The DataTable populates rows incrementally. The user sees the orchestrator working, not a 30-second blank page.

SSE chosen over WebSocket because the data flow is one-direction (server → client), HTTP-friendly, automatically reconnects, and PrimeVue / Vue handle it via the native `EventSource` API without extra infrastructure.

### Decision 7: Saving and shortlists are first-class

Every result row has a "Save to shortlist" action. Saving snapshots the itinerary (immutable copy: all fare ids, landed cost, breakdown, friction attributes) into the trip's shortlist with the originating run id and timestamp. The shortlist survives the run; the user can compare items added across multiple runs (e.g. "the cheap Madrid stopover from run 3 vs. the direct from run 7"). Items in the shortlist can be:
- Re-ordered (drag via `OrderList`),
- Annotated (`Textarea` per item; `Chip` tags),
- Deleted (with `ConfirmPopup`),
- Exported (CSV of the shortlist + notes — useful for emailing the family).

A `ContextMenu` on right-click offers the same actions plus "Re-run with this itinerary's preferences applied" — pulling the preferences from the originating run's snapshot and applying them as overrides to the current draft config.

### Decision 8: Sort, filter, save, export are all built-in `DataTable` behaviours

We do not reinvent any of: multi-column sort, header filters, column reorder, column freeze (left/right), row grouping, row expansion, column toggle, virtual scrolling, lazy loading, CSV export, selection (single / multiple / range). PrimeVue ships all of these; the spec requirements name them so they are visibly committed to.

Per-trip local-storage persistence (column order, visibility, sort, filters) lets the user shape their view once and have it remembered next visit.

### Decision 9: Status, friction, and preference badges share a single design system

A small `BadgeKit` set of utility components (built on `Tag`, `Chip`, `Badge`):
- `<StatusBadge :status="VALIDATED" />` — colour + icon + label, consistent everywhere status appears.
- `<FrictionChip :axis="layover" :value="380" />` — minutes / count / boolean depending on axis.
- `<RankDeltaBadge :delta="+2" :reason="..." />` — preference-driven rank shift with hover tooltip.
- `<DataSourceTag :source="user_assumption | table_figure | validated_quote | llm_estimate_unverified" />` — the data-source pill that appears on every cost component.

This guarantees the cost-honesty contract from `landed-cost-model` is enforced *visually*: the user can always see whether a number is validated, table data, their own assumption, or an unverified LLM estimate.

### Decision 10: Theming and accessibility are non-negotiable

- PrimeVue `Aura` preset by default; dark mode toggle in the app `Menubar`. Theme tokens live in a single CSS file so a re-skin is a token swap, not a rewrite.
- Every interactive control has an ARIA label.
- Keyboard navigation through the wizard, the BookendedScale, the DataTable, and the Drawer copilot.
- Reduced motion respected (`prefers-reduced-motion`) — disables Stepper transitions, Card hover animations, Skeleton shimmer.
- Colour palette for status badges chosen for distinguishability under monochromacy (red/green not the only difference); a Settings panel exposes per-status colour customisation backed by `ColorPicker`.
- Minimum touch target 44px for the BookendedScale ticks; the seven positions need to be clickable, not just keyboard-navigable.

## Decisions deferred to build time

- Whether shortlist export emits CSV only or also a markdown brief for emailing.
- Whether the trip workspace's Overview tab should embed a small map (`vue-leaflet` or similar) showing the gateways and the true-destination pin. Lean yes for spatial intuition; deferred to avoid adding a mapping dep to v1.
- Per-column persistence granularity (per-trip vs. global). Lean per-trip; verify in user testing.

## Risks / Trade-offs

- **Risk: PrimeVue version churn during build.** PrimeVue is on v4; APIs are stabilising but theme tokens have shifted between releases. Mitigation: pin to a specific minor version; bump deliberately in a follow-up change.
- **Trade-off: SPA bundle size.** Vue + PrimeVue + Pinia + Vue Router lands ~150–200KB gzipped before app code. Acceptable for a desktop planning tool; we are not optimising for first-paint on a 3G phone.
- **Risk: SSE behind a corporate proxy.** Some proxies kill long-lived HTTP connections. Mitigation: client-side reconnect logic (built into `EventSource`) plus a fallback "poll every 2s" mode if `EventSource` is unavailable or repeatedly disconnects.
- **Risk: copilot drifts from the structured-form-first contract.** A future maintainer could let the copilot DM raw recommendations the user accepts wholesale. Mitigation: `wizard-copilot` spec encodes the contract and the API gateway enforces it (rejecting any copilot output that contains an unlabeled cost field).
- **Trade-off: building our own `BookendedScale` instead of a vanilla `Slider`.** More code. Pays for itself because the categorical HARD NO / HARD YES vs. soft middle distinction is a load-bearing UX invariant, and Tooltip / lock state for non-admitted HARD YES axes cannot be expressed with a stock slider.
- **Risk: removing Jinja UI before SPA reaches parity.** Mitigation: Jinja stays during the SPA buildout; the removal is a follow-up commit after a parity checklist clears, NOT part of this change.
