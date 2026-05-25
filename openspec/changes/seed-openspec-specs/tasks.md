## 1. Fill OpenSpec project context

- [x] 1.1 Replace `openspec/config.yaml` boilerplate with real `context:` block
      (tech stack: Python 3.12 / FastAPI / SQLModel / SQLite / Jinja / mise / uv;
      domain: LEAD vs VALIDATED, party-of-6 collapse, structure A vs B,
      SerpAPI quota ceiling).
- [x] 1.2 Add `rules:` for `proposal` and `tasks` artifacts capturing
      project-specific guidance (Phase labelling, failure-mode mapping).

## 2. Seed capability specs

- [x] 2.1 Create `openspec/specs/fare-search/spec.md` from
      `docs/fare-search.md` — all five requirements, verbatim wording.
- [x] 2.2 Create `openspec/specs/fare-validation/spec.md` from
      `docs/fare-validation.md` — all three requirements.
- [x] 2.3 Create `openspec/specs/itinerary-orchestration/spec.md` from
      `docs/itinerary-orchestration.md` — all four requirements.
- [x] 2.4 Create `openspec/specs/search-config/spec.md` by splitting the
      `search-config` block out of `docs/config-api-ui.md` — both requirements.
- [x] 2.5 Create `openspec/specs/web-api/spec.md` by splitting the `web-api`
      block out of `docs/config-api-ui.md` — both requirements.
- [x] 2.6 Create `openspec/specs/web-ui/spec.md` reflecting the *Phase-1
      Jinja* UI that actually ships (configs list, run trigger, results view
      with status badges and budget verdict). Vue/PrimeVue is recorded only
      as a Phase-2 non-goal in the file's preamble.

## 3. Verify no behaviour change

- [x] 3.1 Run `openspec validate --strict` — all specs pass structure check.
- [x] 3.2 Diff each seeded spec against its `docs/*.md` source manually;
      confirm requirements and scenarios match 1:1 (only heading style differs).
- [x] 3.3 Run the test suite (`mise run test`) and confirm 24 tests still pass.
      (Suite now has 39 tests; all green — see task 4.6.)

## 4. Align legacy `docs/*.md` with the seeded specs

- [x] 4.1 In `docs/tasks.md`, tick boxes for every implemented item:
      §1.1, §1.3; all of §2.1–§2.5; all of §3.1–§3.6; all of §4.1–§4.5;
      all of §5.1–§5.3; all of §6.1–§6.4; and §8.1.
- [x] 4.2 Mark §1.2 and §7.1–§7.4 (Vue 3 + PrimeVue scaffold + UI) as
      `**Phase 2 — deferred**`; do not check them. Add a pointer to
      `openspec/specs/web-ui/spec.md` for the Phase-1 Jinja spec.
- [x] 4.3 In `docs/proposal.md`, suffix the `web-ui` bullet under
      "What Changes" with `(Phase 2; Phase 1 ships a Jinja UI — see
      openspec/specs/web-ui/)`.
- [x] 4.4 In `docs/config-api-ui.md`, prepend a one-block note to the
      `web-ui` section stating Vue/PrimeVue is Phase 2 and pointing to
      `openspec/specs/web-ui/spec.md` as the authoritative Phase-1
      spec.
- [x] 4.5 In `docs/design.md`, add a one-line aside under "Data model":
      *"Phase-1 seed creates one Config per structure (A and B as
      separate configs) so each leg's RT-vs-OW semantics stay
      unambiguous per run; see app/seed.py."*
- [x] 4.6 In `README.md`, replace `(24 tests)` with the actual count
      captured from `mise run test`.

## 5. Sanity check

- [x] 5.1 Run `mise run test` — all tests still pass (no behaviour
      change).
- [x] 5.2 Confirm `openspec validate seed-openspec-specs --strict`
      passes.
- [x] 5.3 Confirm `openspec list` shows the change with non-zero task
      progress as work proceeds.
