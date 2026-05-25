## Context

The project predates OpenSpec adoption. Spec content was authored as flat
markdown in `docs/`, while OpenSpec was scaffolded (config.yaml + empty
`specs/` and `changes/archive/`) but never populated. The code is already
production-shaped, with 6 test files and 24 tests asserting behaviour
described in `docs/*.md`. The risk now is *retroactive* spec drift: any
future change written through OpenSpec has no baseline to reference and
will either invent one or silently bypass spec review.

## Goals / Non-Goals

**Goals:**
- Make OpenSpec the single source of truth for capability specs.
- Preserve every existing requirement verbatim — no behaviour changes
  smuggled in under the heading of a "bootstrap".
- Give future agents enough project context (in `openspec/config.yaml`)
  to write proposals that match the project's domain vocabulary
  (LEAD/VALIDATED, gateway, structure, party total).

**Non-Goals:**
- Rewriting `docs/*.md` (handled separately by `align-docs-with-phase-1`).
- Adding new requirements, scenarios, or capabilities.
- Changing the Phase 1 / Phase 2 boundary.

## Decisions

### Decision 1: Capability granularity
`docs/config-api-ui.md` bundles three logical capabilities
(search-config, web-api, web-ui). OpenSpec is one-spec-per-capability, so
we split into three spec files. This keeps the modify/remove deltas in
future changes scoped tightly — e.g. a web-api auth change shouldn't have
to delta the UI spec.

### Decision 2: Web UI is Jinja today
Phase 1 ships a Jinja UI (templates live in `app/templates/`). The
proposal and `docs/config-api-ui.md` mention Vue 3 + PrimeVue, but that's
explicitly Phase 2 per `README.md`. The seeded `specs/web-ui/spec.md`
documents the *implemented* Jinja UI, not the aspirational Vue one. A
Phase-2 OpenSpec change will MODIFY/REPLACE these requirements when Vue
arrives. This avoids writing specs for software that doesn't exist.

### Decision 3: Verbatim relocation, not rewrite
Scenarios are copied through with the same wording (lightly normalised to
match the template's `### Requirement: <name>` / `#### Scenario: <name>`
headings). This change must be reviewable as a no-op semantically. Any
wording improvements are intentionally deferred to follow-up changes
where the diff is meaningful.

### Decision 4: `docs/*.md` stays for one cycle
We don't delete `docs/fare-search.md` et al. in this change. The
follow-up `align-docs-with-phase-1` trims them after this lands so reviewers
can diff old-doc vs new-spec side-by-side during this PR.

## Risks / Trade-offs

- **Risk:** silent wording drift between verbatim relocation and the
  original. **Mitigation:** keep `docs/*.md` in place so `git diff` /
  manual review can catch it. The follow-up change deletes docs only
  after this lands.
- **Trade-off:** two copies of the spec content during the transition.
  Acceptable for one PR cycle; cheaper than risking accidental edits
  during a big relocation.
- **Trade-off:** splitting `config-api-ui.md` into three specs creates
  three smaller files. Net positive for OpenSpec workflows (deltas
  target one capability), small navigation cost for humans.
