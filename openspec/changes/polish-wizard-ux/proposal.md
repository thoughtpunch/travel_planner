## Why

Chrome-driven testing of `add-primevue-trip-wizard` surfaced two
load-bearing UX failures that make the SPA non-functional for the
exact case the operator is most likely to hit — creating a NEW trip
from scratch via the dashboard:

1. **The Dates & Legs step is a dead end on draft trips.** A draft
   trip's config has no legs. The wizard step shows only a `Message`
   ("Leg editing is read-only in this slice — modify legs via the
   seed/CLI for now"). There is no path forward without dropping into
   the CLI. This was an explicit MVP calibration in the previous
   change's verify report (task 6.3), but it kills the central flow:
   "click New trip → fill in the wizard → run". The user CANNOT
   complete that flow today.

2. **The Preferences step rendered as five unlabelled sliders.** The
   `BookendedScale` component received `label` and `axis` props but
   only wired them through `aria-label`; the visible text was empty.
   The operator sees five identical `HARD NO … neutral … HARD YES`
   rows with no indication of what each one asks. This bug was fixed
   in-session before this change was written — but the fix shipped
   without a spec, and the spec must record it so the wizard's
   "every axis has a visible question" contract is part of the
   capability, not a fix-and-forget.

A third pain point surfaced during the same chrome test session: the
results-page DataTable's Components and Friction columns are too
narrow at default widths, vertically wrapping text that should fit on
one line. Out of scope for this change (cosmetic; will be folded into
a separate `polish-results-spreadsheet` change with the deferred
DataTable polish items from the previous verify report).

## What Changes

**MODIFIED capabilities:**

- **`web-ui`** — the "Bookended preference scale control" requirement
  is tightened to mandate a *visible* axis label AND a short
  user-facing question per axis. The "Config wizard" requirement
  gains a "Dates & Legs step must be operable on draft configs"
  scenario set, with two acceptable implementations: (a) leg-template
  presets ("3 one-ways SJO → Italy → DC → SJO") that drop a working
  multi-leg config into the wizard, or (b) full in-place leg editor.
  The preset path is the v1 minimum; the full editor lands as a
  follow-up.

- **`search-config`** — adds a `leg_templates` concept: a named,
  curated set of pre-canned leg arrangements (origin / destination
  options, default anchor windows, sampling strategies) that the
  wizard can offer the operator. v1 ships two templates:
  `three_one_ways_to_italy` (Structure A) and
  `nested_envelope_italy` (Structure B).

**Non-goals:**
- Full in-place editor for individual legs (per-origin / per-destination
  multi-selects, calendar pickers, window sliders). That is a follow-up.
- LLM-suggested templates. Templates ship as plain Python constants for v1.

## Impact

- **Affected specs:** `web-ui` (MODIFIED — BookendedScale visible label
  requirement + Dates & Legs draft-config operability), `search-config`
  (MODIFIED — leg_templates concept).
- **Affected code:**
  - `web/src/components/BookendedScale.vue` — gains a `question` prop +
    renders `<h3>` axis label + `<p>` question (already landed
    in-session; this change ratifies the spec).
  - `web/src/pages/TripWizard.vue` — Step 2 (Dates & Legs) gains a
    template-picker (`SelectButton` for the two presets) when the config
    has no legs; renders the chosen template's legs as read-only summary
    cards after selection, and PATCHes them into the config.
  - NEW `app/data/leg_templates.py` — the two seeded templates.
  - `app/api/configs.py` — new endpoint `POST /api/configs/{id}/apply_template`
    that takes a template name + optional anchor-date overrides and creates
    the corresponding `Leg` rows.
- **Affected tests:**
  - Backend contract test for the new endpoint.
  - Vitest extension on `BookendedScale.test.ts` asserting the
    `<h3>` label and question render.
  - A playwright (or vitest-with-jsdom) e2e step exercising
    "create trip → pick template → set preferences → review → run"
    using `PRIMARY_SOURCE=mock` so no fares are touched.
- **Depends on:** `add-primevue-trip-wizard` (archived).
- **Phase:** Phase 2.5 — polish that turns the SPA from
  "scaffolded but stuck" into "actually usable for a new trip."
