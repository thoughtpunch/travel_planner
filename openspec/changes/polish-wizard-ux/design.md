## Context

Browser-driven testing of the Phase-2 SPA caught two real bugs:

1. The Preferences step in the wizard rendered five `BookendedScale`s
   side by side with identical visible chrome and *no* axis identifier.
   Root cause: the component took `label` and `axis` as props but only
   surfaced them via `aria-label`. To a sighted operator looking at the
   form, there were no questions — just sliders.

2. The Dates & Legs step on a draft trip showed a single `Message`
   saying leg editing was out of scope for the slice. The "new trip"
   flow (Dashboard → New trip → Wizard) thus has no way to reach a
   runnable config without dropping out to the CLI / seed.

This change is the smallest cut that makes the wizard usable for a
brand-new trip and removes the "go run a script" escape hatch.

## Goals / Non-Goals

**Goals:**
- Every `BookendedScale` instance renders a visible label AND a short
  per-axis question. The two should be the primary visual element of
  the row — not afterthoughts in `aria-label`.
- The wizard's Dates & Legs step has a usable path on a draft config.
  Minimum: pick a leg-template preset; the wizard writes its legs
  into the config and shows a read-only summary of what was written.

**Non-Goals:**
- A full custom leg editor (MultiSelect of origins, MultiSelect of
  destinations, Calendar for anchor date, Slider for window days, per-leg
  sampling-strategy picker). That is the natural follow-up but is twice
  the work of templates and isn't required to unblock the user.
- A template gallery beyond the two engagement-canonical structures.
  More templates can be added without spec change.
- Template editing in the UI. Templates are source-controlled Python.

## Decisions

### Decision 1: BookendedScale's label is a heading, the question is a paragraph

Visible `<h3>` for the axis label, `<p>` underneath for the question.
Both are exposed via `aria-labelledby` so screen readers get the same
hierarchy. Single-line `aria-label` was the original mistake — the
visible UI is what the user actually navigates.

### Decision 2: Templates over in-place editor for the minimum cut

Two observations made the choice:

1. The engagement is a family-of-6 trip to Venice. The matrix structure
   (SJO origin, Italy gateways, DC airports, anchor dates around
   Sept/Nov/Dec) is the same for every trip the operator is going to run
   this year. Asking them to re-construct it leg-by-leg in the UI for
   each trip is busywork.

2. A leg-template is one POST endpoint and one `SelectButton` on the
   wizard step. A full in-place editor is per-leg accordions × five
   form fields × persistence × validation × inline error display. Order
   of magnitude more work for the same end (an operator with a working
   config).

The template path doesn't preclude the editor; it just isn't blocking.

### Decision 3: Templates are Python constants, not seed rows

A template is `{name, structures, legs: [{ordinal, origins,
destinations, date_anchor_offset_days, window_days, sampling_strategy}]}`
where `date_anchor_offset_days` is relative to "today" so the operator
can apply the template and get sensible default dates without editing
seven anchor fields. Lives in `app/data/leg_templates.py` next to the
gateway-transfer table — same "curated tables of stable knowledge"
pattern.

### Decision 4: Template selection mutates the config in place

`POST /api/configs/{id}/apply_template {name, anchor_date?}` creates
the `Leg` rows on the config (replacing any existing legs). Returns
the updated config. The wizard step then renders the leg summary
read-only (same component used by the post-MVP editor when it lands).

The operator can re-apply a different template, which replaces all legs.
A confirm-dialog protects against accidental wipe of a manually-edited
config; in v1 (no editor yet) this isn't strictly needed but the API
should support it from day one.

## Failure modes this change prevents

1. **Wizard preferences step looks like five identical sliders** —
   resolved by Decision 1 (visible h3 + p per axis).
2. **Operator creates a new trip and is stuck** — resolved by Decision 2
   (template preset gets them to a runnable config in two clicks).
3. **Operator picks a template, then can't see what was set** —
   resolved by Decision 4 (read-only summary of the applied legs renders
   below the picker).

## Risks / Trade-offs

- **Risk: template choices feel paternalistic.** The two seeded
  templates encode our specific engagement (Italy / DC / SJO). For a
  hypothetical second user, those would be useless. Acceptable for v1
  — this tool is built for a specific operator on a specific
  engagement; the template gallery becomes more interesting if the
  user base expands.
- **Trade-off: no per-leg granular control in v1.** The operator who
  wants to swap one gateway out of a template has to do it via the
  CLI / API for now. Acceptable as a follow-up.
- **Risk: the read-only summary masks template defaults the operator
  didn't realize were chosen.** Mitigation: render every field
  prominently in the summary card (origins, destinations, dates,
  window days, sampling strategy), with an "apply different template"
  affordance always visible.
