## 1. BookendedScale visible label + question (already in working tree — ratify in tests)

- [ ] 1.1 Confirm `web/src/components/BookendedScale.vue` renders `<h3>` for `props.label` and `<p>` for `props.question` (already implemented).
- [ ] 1.2 Extend `web/src/components/BookendedScale.test.ts` to assert: (a) the `<h3>` is present with the label text, (b) the `<p>` is present when a `question` is supplied, (c) the component throws / warns in dev when `question` is omitted (or document the optionality choice).
- [ ] 1.3 `web/src/pages/TripWizard.vue::AXES` already supplies a per-axis question. No code change here — just a code-comment noting "every axis must have a question per `web-ui` spec."

## 2. Leg templates data

- [ ] 2.1 Create `app/data/leg_templates.py` exposing `LEG_TEMPLATES: dict[str, LegTemplate]`. Define `LegTemplate` dataclass and `LegTemplateLeg` with `ordinal`, `origins`, `destinations`, `date_anchor_offset_days`, `window_days`, `sampling_strategy`.
- [ ] 2.2 Seed `three_one_ways_to_italy` (Structure A) and `nested_envelope_italy` (Structure B). Defaults: outbound ~120 days out, inner ~180, return ~220; window 7; "anchor,+/-3,+/-7".
- [ ] 2.3 Unit test: every seeded template has the required fields; structure values are valid enum members; legs have monotonically increasing ordinals; date offsets are strictly increasing per leg.

## 3. Template apply API

- [ ] 3.1 Add `GET /api/leg_templates` returning the seeded list (name, description, structures, legs preview).
- [ ] 3.2 Add `POST /api/configs/{id}/apply_template {name, anchor_date?}` that:
      - validates the template name (422 on unknown),
      - resolves `anchor_date` (defaults to `date.today()`),
      - deletes existing `Leg` rows on the config,
      - inserts new ones with `date_anchor = anchor_date + offset`,
      - returns the full updated config.
- [ ] 3.3 Backend tests: unknown name → 422, apply replaces legs, anchor offset math correct, returned config has expected leg ordinals.

## 4. Wizard Dates & Legs step rewrite

- [ ] 4.1 In `web/src/pages/TripWizard.vue`, replace the "read-only" placeholder Message with a leg-template picker.
- [ ] 4.2 On mount, GET `/api/leg_templates`; render as a `SelectButton` (small templates) or `Select` (if >3 templates) with the description below.
- [ ] 4.3 If `config.legs.length === 0`, show only the picker + Apply button.
- [ ] 4.4 If `config.legs.length > 0`, render one read-only summary `Card` per leg (origins, destinations, anchor date, window days, sampling strategy) + an "Apply a different template" affordance that re-opens the picker (with `ConfirmPopup` warning about leg replacement).
- [ ] 4.5 The Next button is disabled while `config.legs.length === 0`.
- [ ] 4.6 After successful apply: `Toast` confirmation, summary cards re-render, focus moves to Next button.

## 5. API client + types

- [ ] 5.1 Add `api.listLegTemplates()` and `api.applyTemplate(configId, name, anchorDate?)` to `web/src/api/client.ts`.
- [ ] 5.2 Add `LegTemplate` and `LegTemplatePreview` types to `web/src/api/types.ts`.

## 6. End-to-end smoke test (mock source)

- [ ] 6.1 Backend e2e test driving: create draft trip → apply `three_one_ways_to_italy` → run via mock primary source → assert COMPLETE + non-empty itineraries.
- [ ] 6.2 (Stretch) Playwright e2e covering the same flow in the browser, with `PRIMARY_SOURCE=mock`.

## 7. Spec sync + validate

- [ ] 7.1 Sync the `web-ui` and `search-config` deltas into `openspec/specs/`.
- [ ] 7.2 `openspec validate polish-wizard-ux --strict` clean.
- [ ] 7.3 `openspec validate --all --strict` clean.
- [ ] 7.4 `mise run test` clean. `mise run web:test` clean.

## 8. Non-goals tracking (NOT in this change — captured here for follow-up)

- [ ] 8.1 (deferred) Full in-place per-leg editor: MultiSelect origins / destinations, Calendar anchor picker, Slider window, sampling-strategy `Select`, per-leg add/remove.
- [ ] 8.2 (deferred) LLM-suggested templates / per-trip template overrides.
- [ ] 8.3 (deferred) Template management UI (create / edit / delete).
