## Why

The `openspec/specs/` directory is empty and `openspec/config.yaml` is still
the boilerplate from `openspec init`. Meanwhile, the *real* capability specs
live in `docs/*.md` (`fare-search.md`, `fare-validation.md`,
`itinerary-orchestration.md`, `config-api-ui.md`) and were written before
OpenSpec was installed. Future OpenSpec-driven changes (`opsx:propose`,
`opsx:apply`, `opsx:archive`) cannot reference, modify, or delta a capability
spec that doesn't exist — every subsequent change is forced to invent the
baseline, and the docs/specs/ split makes drift inevitable.

This change makes OpenSpec the single source of truth for capability specs
going forward.

## What Changes

- Create one `openspec/specs/<capability>/spec.md` per Phase-1 capability,
  carrying the *current* (built-and-tested) requirements verbatim from
  `docs/*.md` — no requirement changes, just relocation.
- Fill `openspec/config.yaml` with real project context (tech stack, domain
  invariants, per-artifact rules) so future agents have grounding.
- Trim the legacy `docs/*.md` files to match: tick every implemented task
  in `docs/tasks.md`, mark Vue 3 + PrimeVue UI work as Phase 2, document
  the seed's intentional divergence from `docs/design.md`, and replace the
  README's stale "24 tests" claim with the actual count.

The Jinja UI is captured as the Phase-1 truth in `specs/web-ui/spec.md`;
Vue/PrimeVue is recorded as an out-of-scope Phase-2 note, not a requirement.

## Capabilities

### New Capabilities

- `fare-search`: Multi-source fare retrieval (fast-flights scraper + SerpAPI
  fallback) with LEAD-only scraper fares, quota ceiling, and passenger-count
  fidelity.
- `fare-validation`: Top-N candidate re-query at full party size via SerpAPI;
  tolerance check; VALIDATED/VALIDATION_FAILED transitions; STALE expiry.
- `itinerary-orchestration`: Leg × gateway × date matrix expansion; dual
  Structure A/B pricing; blackout flagging; ranking with status separation.
- `search-config`: Persistent search definitions and run history in SQLite,
  with config snapshots so historical runs stay interpretable.
- `web-api`: FastAPI service over SQLite for config CRUD, run triggering,
  result retrieval, quota status — secrets server-side only.
- `web-ui`: Phase-1 Jinja-templated server-rendered UI for configs, run
  history, and ranked results with status colouring and budget verdict.

### Modified Capabilities

None — this is a relocation, not a behavior change.

## Impact

- **Affected code:** none. No runtime code is touched.
- **Affected docs:** `openspec/specs/` populated; `openspec/config.yaml`
  filled; `docs/tasks.md`, `docs/proposal.md`, `docs/config-api-ui.md`,
  `docs/design.md`, and `README.md` reconciled with Phase-1 reality.
- **Affected workflow:** subsequent `opsx:propose` / `opsx:apply` runs can
  now reference existing specs to MODIFY/REMOVE requirements cleanly.
