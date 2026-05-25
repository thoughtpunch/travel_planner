## 1. Frontend scaffolding

- [x] 1.1 Create `web/` directory with Vite + Vue 3 + TypeScript + Pinia + Vue Router + PrimeVue 4 (`@primevue/themes/aura`) + PrimeIcons. Pin PrimeVue to a specific minor version.
- [x] 1.2 Configure Vite to build into `app/static/web-dist/`. FastAPI mounts `app/static/` and adds a catch-all route returning `index.html` for non-`/api/*` paths.
- [x] 1.3 Tailwind (or PrimeFlex) for layout utilities; PrimeVue components own visual atoms. Don't mix utility-CSS with PrimeVue's own theme tokens.
- [x] 1.4 ESLint + Prettier + Vitest + Playwright. Add `mise` tasks: `mise run web:dev`, `mise run web:build`, `mise run web:test`, `mise run web:e2e`.
- [x] 1.5 Single CSS file owning theme tokens — `web/src/theme.css` — so a re-skin is a token swap, not a component edit.

## 2. App shell

- [x] 2.1 Build the shell layout: `Menubar` (logo, dashboard, settings, dark-mode toggle, copilot toggle, live quota badge), `Drawer` (left nav), main content area, `Toast` host, `ConfirmDialog` host, `BlockUI` host.
- [x] 2.2 Dark-mode toggle persists to local storage; theme tokens swap via `prefers-color-scheme` fallback.
- [x] 2.3 Skip-link for keyboard users; full Tab order audit.
- [x] 2.4 Responsive breakpoints: desktop > 1280 (full layout), tablet 768–1280 (Drawer collapses by default), phone < 768 (degraded, single-column).

## 3. Routing & state

- [x] 3.1 Vue Router with routes: `/` (dashboard), `/trips/:id` (workspace), `/trips/:id/runs/:run_id` (run results), `/settings/:tab?`, `/wizard/:config_id?` (standalone wizard or embedded in workspace).
- [x] 3.2 Pinia stores: `useTripsStore`, `useConfigStore` (per-trip), `useRunStore` (per-run with SSE subscription), `useShortlistStore`, `useSettingsStore`, `useCopilotStore`.
- [x] 3.3 API client (`web/src/api/`) with typed methods generated from FastAPI's OpenAPI schema (use `openapi-typescript`).

## 4. Dashboard

- [x] 4.1 Trip cards via `DataView` (grid default, list toggle). Each card: trip name, true destination, party summary, latest-run cost-spine snapshot, latest-run age, incomplete-structure `Tag`, "Open" `Button`.
- [x] 4.2 Empty state with "Create your first trip" `Button` opening the wizard.
- [x] 4.3 "New trip" `Button` in header.

## 5. Trip workspace

- [x] 5.1 Workspace header: trip name (`Inplace` + `InputText`), true destination, party, date windows, "Run now" `Button`.
- [x] 5.2 `TabView` with five tabs: Overview, Wizard, Runs, Shortlist, Notes. Tab state persists per trip in local storage.
- [x] 5.3 Overview tab: latest-run cost-spine summary `Card` + shortlist preview `DataView` (top 3).
- [x] 5.4 Runs tab: `DataTable` of runs (status, top landed cost, scraper/serpapi calls, age, "Open"). Header filter on status.
- [x] 5.5 Notes tab: `Textarea` with autosave (debounce 1s) — PATCH `/api/trips/{id}` with notes only.

## 6. Config wizard

- [x] 6.1 `Stepper` shell with five steps. Each step in its own `Card`. Back/Next `Button`s wired to step navigation; jump-to-step disabled until prior required fields valid.
- [x] 6.2 Step 1 (Trip basics): `InputText` (name), `AutoComplete` (true destination city), `InputNumber` × 4 (adults/children/infants in seat/on lap).
- [x] 6.3 Step 2 (Dates & legs): `Calendar` (outbound anchor, return anchor), `Slider` (window ± days), `SelectButton` (structure A / B / Both), `MultiSelect` (per-leg candidate gateways) with `Chip` previews. Inline `Message` warnings for overlapping windows or empty gateway sets.
- [x] 6.4 Step 3 (Preferences): one `BookendedScale` per axis for global defaults, `Accordion` for per-leg overrides.
- [x] 6.5 Step 4 (Cost assumptions): `InputNumber` (stopover lodging/night with currency prefix), `InputNumber` (rooms), collapsible mini `DataTable` for per-gateway transfer overrides.
- [x] 6.6 Step 5 (Review): assembled config `Card` + dry-run preview `Card` from `GET /api/configs/{id}/preview`. "Run" `Button` POSTs run.
- [x] 6.7 Wizard durability: every field change debounces 500ms then PATCHes `/api/configs/{id}`.
- [x] 6.8 Wizard validation surfaces server 422s as `Message` per field; finalize button disabled until all valid.

## 7. BookendedScale control

- [x] 7.1 Build `<BookendedScale />` component: 7-tick `Slider` (`step=1`, `min=0`, `max=6`) + custom tick labels + two end `Tag`s (HARD NO red, HARD YES green) visually distinct from the soft middle.
- [x] 7.2 Greyed-out HARD YES with `lock` icon + `Tooltip` when `hard_yes_admitted = false`.
- [x] 7.3 HARD NO with threshold reveals secondary `InputNumber`; form invalid until threshold set.
- [x] 7.4 HARD YES on stopover opens `Dialog` ("Name a city or sweep?") with `AutoComplete` + `Button` row.
- [x] 7.5 Full keyboard nav: arrow keys move tick, Enter on HARD YES opens dialog, Esc cancels.
- [x] 7.6 ARIA: `role="slider"` with `aria-valuemin`, `aria-valuemax`, `aria-valuetext`, `aria-labelledby` referencing the axis label.
- [x] 7.7 Min 44px touch targets per tick.
- [x] 7.8 Vitest unit tests: (a) HARD YES unreachable when disabled, (b) HARD NO with threshold blocks form validity, (c) emitted value matches scale position, (d) keyboard nav exits at "strongly desire" when HARD YES disabled.

## 8. Run results page

- [x] 8.1 Cost-spine summary `Card` at top: cheapest VALIDATED landed cost (big number), by-structure verdicts, scraper / SerpAPI call counts, run timestamp.
- [x] 8.2 `Knob` (or `Slider`) for live soft-band ±% client-side rescore. `Message` "Live preview — re-run to persist" beside it.
- [x] 8.3 `Splitter` layout: `DataTable` left ~60%, detail `Sidebar` right ~40%. Splitter drag persists per trip.
- [x] 8.4 `DataTable` config: `sortMode="multiple"`, `filterDisplay="row"`, `reorderableColumns`, frozen columns (Rank left, Landed cost right), `groupRowsBy="structure"` (toggleable), `expandedRows` for breakdown, column-toggle `OverlayPanel`, `exportCSV`. View state to local storage scoped by trip id.
- [x] 8.5 Columns wired with sort + filter + freeze + toggle (Rank, Status `StatusBadge`, Structure, Carrier, Origin → Gateway, Outbound, Return, Landed cost, fare/transfer/lodging components with `DataSourceTag`, friction columns with `FrictionChip`, RankDeltaBadge, Actions).
- [x] 8.6 Row expansion: `Card` cost-breakdown + leg `Timeline` + preference-explanations list. Keyboard Enter toggles expansion.
- [x] 8.7 Detail sidebar mirrors the selected row.
- [x] 8.8 CSV export bound to a `Button` in the table toolbar.
- [x] 8.9 Empty / error states via `Message`.

## 9. Live run streaming (SSE)

- [x] 9.1 `useRunStore` opens an `EventSource` on `GET /api/runs/{id}/stream` when status is RUNNING.
- [x] 9.2 Handle events: `sweep_fare`, `validation_result`, `scoring_complete`, `status`, `error`. Update DataTable rows incrementally; update cost-spine `Card`; advance `ProgressBar` per stage.
- [x] 9.3 Reconnect with exponential backoff up to 30s using `Last-Event-ID`. Fall back to 2s polling after 3 consecutive failures; `Toast` informs the operator.
- [x] 9.4 `Skeleton` placeholders for cost-spine summary until validation completes.
- [x] 9.5 Cleanup: close EventSource on route leave / unmount.

## 10. Shortlist

- [x] 10.1 Shortlist tab `DataView` (list default, grid toggle). Each item card: itinerary summary, landed cost, status, originating run id + age, notes preview, tags, `ContextMenu` (right-click).
- [x] 10.2 `OrderList` for manual reorder; persist order via PATCH per item.
- [x] 10.3 Per-item `Textarea` notes and `Chips` tags input, both with debounced PATCH.
- [x] 10.4 "Save to shortlist" `Button` on every result row → POST `/api/trips/{id}/shortlist` with `{run_id, itinerary_id}`. `Toast` confirms with 5s "Undo".
- [x] 10.5 Delete confirms with `ConfirmPopup`; deletion shows 5s undo `Toast`.
- [x] 10.6 CSV export of shortlist.
- [x] 10.7 ContextMenu "Re-run with these preferences" opens wizard with the saved itinerary's preferences applied as a candidate override (user confirms before save).

## 11. LLM copilot

- [x] 11.1 Copilot `Drawer` on the right; toggle in `Menubar`. Disable-able in Settings.
- [x] 11.2 Drawer body: history of suggestions as `Card`s + a `Textarea` input + a "Suggest" `Button`. Each suggestion `Card`: target field path, suggested value, confidence, rationale, Accept / Edit / Reject `Button`s.
- [x] 11.3 Per-field `Sparkle` icon `Button` (small `Button` with `pi pi-sparkles`) opens an `OverlayPanel` anchored to the field with a per-field copilot call.
- [x] 11.4 Accept writes value AND sets `llm_suggested.<path> = true`; field renders with `DataSourceTag :source="llm_estimate_unverified"` until edited or explicitly confirmed.
- [x] 11.5 Edit opens the field with the suggested value pre-filled; the operator's edit clears the suggestion mark.
- [x] 11.6 Reject dismisses with no state change.
- [x] 11.7 Backend `app/api/copilot.py` proxies to Anthropic SDK using prompt cache discipline (system prompt + gateway-transfer table marked `cache_control: ephemeral`).
- [x] 11.8 Backend validates copilot responses: cost-field suggestions without `unverified: true` are rejected (502 to client + log). Forbidden-path suggestions (anything outside config inputs) are rejected (422).
- [x] 11.9 Persist accepted suggestions to `Config.copilot_history`; Settings → "AI suggestions log" tab renders the history.

## 12. BadgeKit

- [x] 12.1 `<StatusBadge :status />` — colour + icon + label per status. Single source of truth used in DataTable, cards, and detail.
- [x] 12.2 `<FrictionChip :axis :value />` — labelled friction attribute (minutes / count / boolean depending on axis).
- [x] 12.3 `<RankDeltaBadge :delta :reason />` — `+2` / `-1` etc., `Tooltip` shows preference explanation.
- [x] 12.4 `<DataSourceTag :source />` — `validated_quote | table_figure | user_assumption | user_override | llm_estimate_unverified`. Used on every cost component.
- [x] 12.5 Vitest test asserting every cost figure rendered in cost-breakdown components carries a `DataSourceTag`.

## 13. Settings

- [x] 13.1 `TabView` with tabs: General, Default preferences, Default cost assumptions, Gateway-transfer table, LLM provider, Status badge palette, About.
- [x] 13.2 General: dark-mode `InputSwitch`, currency display `Dropdown`.
- [x] 13.3 Default preferences: BookendedScale axes editable; saved to user settings (separate from per-trip config).
- [x] 13.4 Default cost assumptions: lodging/night + rooms; applies to new trips.
- [x] 13.5 Gateway-transfer table: read-only `DataTable` with `last_reviewed` dates; CSV `FileUpload` for per-config overrides (preview before commit).
- [x] 13.6 LLM provider: API key `Password`, model `Dropdown` (Opus 4.7 / Sonnet 4.6 / Haiku 4.5 with defaults per copilot prompt), copilot enable/disable `InputSwitch`.
- [x] 13.7 Status badge palette: per-status `ColorPicker` for users with non-default colour vision needs.
- [x] 13.8 About: app version, quota status, "AI suggestions log".

## 14. Backend API additions

- [x] 14.1 `POST /api/configs`, `GET /api/configs/{id}`, `PATCH /api/configs/{id}` (idempotent merge), `POST /api/configs/{id}/finalize`, `GET /api/configs/{id}/preview`.
- [x] 14.2 `GET/POST/PATCH/DELETE /api/trips` and per-trip routes.
- [x] 14.3 `GET/POST/PATCH/DELETE /api/trips/{id}/shortlist[/{item_id}]`.
- [x] 14.4 `GET /api/runs/{id}/stream` SSE endpoint with Last-Event-ID support.
- [x] 14.5 `POST /api/copilot/*` endpoints with the contract-enforcement gateway (reject cost suggestions without `unverified`, reject forbidden paths).
- [x] 14.6 Catch-all SPA route returning `index.html` for non-`/api/*` paths.
- [x] 14.7 Backend tests: per-endpoint contract; SSE replay-from-Last-Event-ID; copilot contract violations rejected.

## 15. Accessibility & polish

- [x] 15.1 ARIA audit: every interactive control has an accessible name.
- [x] 15.2 Keyboard-only flows: complete wizard → run → save to shortlist using keyboard alone. Add as a Playwright e2e.
- [x] 15.3 Reduced-motion: disable Stepper transitions, hover anims, Skeleton shimmer when `prefers-reduced-motion: reduce`.
- [x] 15.4 Colour-vision audit: status palette is distinguishable under deuteranopia / protanopia; icons supplement colour.
- [x] 15.5 Focus rings: visible on every interactive surface; do not rely on browser defaults alone.

## 16. Cleanup & cutover

- [x] 16.1 Phase-1 Jinja templates remain during SPA buildout for operator continuity.
- [x] 16.2 Parity checklist before Jinja removal: (a) dashboard, (b) config CRUD, (c) run trigger, (d) results table, (e) quota visibility, (f) status badges all in SPA.
- [x] 16.3 After parity, follow-up cleanup commit removes `app/templates/` and the Jinja routes (NOT part of this change).

## 17. Spec sync + validate

- [x] 17.1 Sync deltas into `openspec/specs/web-ui/spec.md`, `openspec/specs/web-api/spec.md`, and new `openspec/specs/wizard-copilot/spec.md`.
- [x] 17.2 `openspec validate add-primevue-trip-wizard --strict` clean.
- [x] 17.3 `openspec validate --all --strict` clean.
- [x] 17.4 Frontend tests (Vitest unit + Playwright e2e) pass.
- [x] 17.5 Backend tests (`mise run test`) pass.
