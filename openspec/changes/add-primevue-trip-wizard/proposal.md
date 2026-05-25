## Why

The Phase-1 web UI is a server-rendered Jinja shell — enough to list configs, trigger a run, and read a results table. It does not surface the new objects that `add-preference-weighted-landed-cost` puts in front of the user: the bookended preference scale, the per-leg overrides, the HARD YES stopover prompt, the cost spine with component breakdown, the friction columns, the LLM elicitation copilot, and the per-trip workspace where the user iterates across runs of the same config to converge on a decision.

This change replaces the Phase-1 Jinja UI with a Vue 3 + PrimeVue Single Page Application that is built around the orchestration model — not around chrome borrowed from consumer fare comparators. The product framing is **an LLM-orchestrated trip-planning workspace**: the user pours in their constraints, an LLM helps elicit and pre-fill them, the orchestrator runs honestly-priced searches, and the user reorders and saves variants in pursuit of a defensible decision. We are not building Kayak or Kiwi; the goal is not a magic search box that ranks 200 airfares. The goal is a tool where a careful planner can interrogate every number the system shows them and shape the search around real preferences.

Three things this UI must do better than any comparator we are aware of:

1. **Elicit preferences honestly** with the OkCupid-style bookended scale, including per-leg overrides and the HARD YES / HARD NO categorical distinction, without making the user feel they are filing a tax return.
2. **Present results as a spreadsheet a planner can interrogate**, not as a horizontal carousel of cards. Cost spine and component breakdown are first-class columns; friction attributes are sortable and filterable; nothing is collapsed behind a single opaque score.
3. **Persist work as trips, not as one-shot queries.** A user comparing "fly to Venice direct" vs "stopover in Madrid" needs a workspace that keeps both alive, lets them save preferred itineraries to a shortlist, annotate them, and re-run with adjusted preferences without losing prior context.

PrimeVue is the right framework for this for three reasons: it ships the full component palette this UI needs out of the box (Stepper, DataTable with sort/filter/freeze/grouping, Slider, Accordion, AutoComplete, Dialog, Toast, Tag, Splitter, OverlayPanel, ConfirmDialog, DataView, Timeline, Tree, Card, Drawer, ContextMenu, etc.), it is themable (Aura preset by default; switchable), and its DataTable in particular has the production-grade sort / filter / column-reorder / column-freeze / row-grouping behaviour that a results spreadsheet requires.

## What Changes

The Phase-1 server-rendered UI is replaced by a Vue 3 + PrimeVue SPA. The Phase-1 Jinja templates are removed; the FastAPI process gains a small `/api/*` surface tuned for an SPA (incremental wizard state, run streaming, trip workspace persistence, LLM copilot calls).

**MODIFIED capabilities:**
- **`web-ui`** — the Phase-1 server-rendered UI requirement is REMOVED and replaced with a Phase-2 PrimeVue SPA requirement set covering: app shell + theming, dashboard, trip workspace, config wizard, run results, preference elicitation control, saved-itinerary shortlist, settings, and accessibility.
- **`web-api`** — the API gains wizard-state endpoints (idempotent partial PATCH), trip-workspace endpoints (CRUD for trips and shortlists), a run-stream endpoint (Server-Sent Events for in-progress runs), and copilot endpoints (preference suggestion, cost-assumption pre-fill, stopover waypoint suggestion).

**NEW capability:**
- **`wizard-copilot`** — the contract for the LLM copilot inside the wizard. Structured-form-first (UI is the source of truth; copilot only writes into form fields the user then accepts), labeled (every copilot-written value is visibly marked unverified until confirmed), and forbidden from contributing to cost numbers without a label per `landed-cost-model`'s honesty rules.

**Component coverage (PrimeVue palette used end-to-end):**
- App shell: `Menubar`, `Drawer` (sidebar), `Avatar`, `Breadcrumb`, `Toast`, `ConfirmDialog`, `BlockUI` (during run kickoff), `ProgressBar` (with `Skeleton` placeholders), `ScrollPanel`, `Tooltip`.
- Wizard: `Stepper` (steps), `Card` (per step), `InputText`, `InputNumber`, `Calendar`, `MultiSelect` (gateways), `Chip` (selected gateways), `Slider` (date window), `RadioButton` / `SelectButton` (structures A / B / both), custom `BookendedScale` (built on `Slider` + labels — preference axis control), `Accordion` (per-leg overrides), `AutoComplete` (stopover city / IATA lookup), `Dialog` (HARD YES "name or sweep" prompt), `Message` (incoherent-combination warnings), `Inplace` (cost assumption editing), `Tag` (LLM-suggested label).
- Results: `DataTable` with column sort, multi-column filter, column reorder, column freeze, row grouping (by structure), row expansion (cost breakdown + preference explanations), column toggle, CSV export; `Tag` for status badges; `Chip` for friction attributes; `Badge` for counts; `Sidebar` for in-place itinerary detail; `Splitter` for table + detail layouts; `Galleria` (gateway photos? optional); `Timeline` for itinerary leg sequence; `Card` for the cost spine summary at the top; `Knob` for live "soft band ±%" tuning.
- Trip workspace: `DataView` (saved-itinerary shortlist with grid/list toggle), `Tag` / `Chip` for annotations, `Textarea` for notes, `OrderList` (manual reorder within shortlist), `ContextMenu` (right-click actions), `ConfirmPopup` (delete confirmation).
- Saving & history: `Card` grid for trip cards (with `Avatar` for trip-thumb), `DataTable` for run history per trip with status filter; `Timeline` for "preference changes across runs"; `Diff` (custom built on `Panel` + diff colours) for "what changed between runs".
- Settings & admin: `TabView` (general / preferences defaults / cost assumptions / gateway-transfer table / theme / LLM provider), `InputSwitch`, `ColorPicker` (custom badge palette), `Password` (API keys), `FileUpload` (CSV import for gateway-transfer overrides).
- Cross-cutting: dark mode + Aura theme preset; responsive breakpoints; keyboard navigation; ARIA labels on every interactive control; reduced-motion respect.

## Impact

- **Affected specs:** MOD `web-ui` (replace Phase-1 server-rendered req with Phase-2 SPA reqs), MOD `web-api` (new endpoints), NEW `wizard-copilot` (LLM copilot contract).
- **Affected code:**
  - NEW `web/` directory (Vue 3 + Vite + PrimeVue 4 + Pinia + Vue Router + TypeScript). Built into `app/static/web-dist/` and served by FastAPI as static plus a catch-all SPA route.
  - REMOVE `app/templates/` (Jinja) once the SPA covers the operator workflow. Phase-out is one cycle: Jinja stays during the SPA buildout; remove in a follow-up cleanup commit after parity.
  - NEW endpoints under `app/api/`: `app/api/wizard.py` (wizard state PATCH), `app/api/trips.py` (trip workspace), `app/api/runs.py` extended with SSE stream, `app/api/copilot.py` (LLM elicitation).
  - NEW `app/llm/` module: thin Anthropic SDK wrapper for the copilot. Caching via prompt cache (default on).
- **Affected tests:**
  - Backend: contract tests for new endpoints, including the copilot endpoint's "never returns an unlabeled cost" assertion.
  - Frontend: Vitest unit tests for the `BookendedScale` control and the cost-breakdown component (the two components that encode product invariants in UI form); Playwright e2e for the happy-path wizard → run → results → save-to-trip flow.
- **Depends on:** `add-preference-weighted-landed-cost`. Without that change's contracts (preferences, cost assumptions, landed-cost components, friction attributes, preference explanations), the SPA has nothing to render.
- **Out of scope:**
  - Multi-tenant auth. This is a single-operator tool; an auth shim (single shared password or local-only) is the v1 boundary. A real auth design is a separate change.
  - Mobile-first responsive design as a primary target. The tool is desktop-first (it is a planning workspace); the SPA degrades gracefully to tablet but does not optimise for phone.
  - Booking / payment integration. We still rank and explain; we do not transact.
  - i18n. English-only v1. The component palette can be re-themed later without rework of the data flow.
- **Phase:** Phase 2.
