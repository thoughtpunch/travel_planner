# wizard-copilot Specification

## Purpose

Contract for the LLM copilot embedded in the wizard. The copilot is a
**structured-form-first** suggester: the wizard form is the source of truth,
the copilot can only produce field-targeted `{path, value, confidence,
rationale}` suggestions, and the SPA renders each one with Accept / Edit /
Reject buttons. The copilot SHALL NEVER mutate state directly, SHALL NEVER
contribute to a cost field without an `unverified` label, and SHALL NEVER
target result-set or rank paths.

## Requirements

### Requirement: Structured-form-first copilot

The LLM copilot SHALL operate in a structured-form-first mode: the wizard form is the source of truth, the copilot can ONLY produce field-targeted suggestions (`{path, value, confidence, rationale}`), and the SPA SHALL render every suggestion as an inline `Card` with Accept / Edit / Reject `Button`s. The copilot SHALL NEVER mutate config state directly; only the user's Accept action (or explicit edit) writes the value.

#### Scenario: Drawer suggestion flow

- **WHEN** the operator opens the copilot Drawer and enters natural-language context
- **THEN** the SPA POSTs to `/api/copilot/preferences/suggest`
- **AND** the response renders as a list of inline `Card`s — one per suggested field — each with the suggested value, confidence, rationale, and Accept/Edit/Reject `Button`s
- **AND** clicking Accept writes the value into the form AND marks `llm_suggested.<path> = true`
- **AND** clicking Reject dismisses the suggestion with no state change

### Requirement: Copilot may not contribute to cost numbers without a label

Any copilot suggestion targeting a cost field (any path under `cost_assumptions.*` or `transfer_overrides.*`) SHALL be returned by the API with `unverified: true`. The SPA SHALL render such values with `<DataSourceTag :source="llm_estimate_unverified" />` and a "suggested — verify" label until the operator accepts or edits.

The API gateway SHALL validate the copilot's response: a cost-field suggestion missing `unverified: true` SHALL be rejected with 502 and logged as a contract violation.

#### Scenario: Cost suggestion is labelled and unwritable without confirmation

- **WHEN** the copilot suggests `cost_assumptions.stopover_lodging_per_night = 32000` with `unverified: true`
- **THEN** the SPA renders it with the `llm_estimate_unverified` data-source tag
- **AND** the value does NOT enter any landed-cost computation until the operator confirms

#### Scenario: Missing unverified flag is rejected

- **WHEN** the LLM provider returns a cost-field suggestion without `unverified: true`
- **THEN** the API gateway rejects the response with 502
- **AND** no suggestion is written to the form

### Requirement: Copilot may not produce filtering or ranking decisions

The copilot SHALL NOT return suggestions whose `path` targets the result set, the rank order, or any post-validation pipeline output. Allowed paths are restricted to config inputs: `preferences.*`, `cost_assumptions.*`, `stopover_target.*`, gateway selections, date windows, and party fields.

The API gateway SHALL reject suggestions targeting forbidden paths with 422 and log the attempt.

#### Scenario: Forbidden path rejected

- **WHEN** the copilot attempts to return `{path: "results.exclude_itinerary_ids", value: [...]}`
- **THEN** the API gateway rejects with 422

### Requirement: Copilot prompt-cache discipline (Anthropic SDK)

When the copilot is wired to a real Anthropic SDK call, the SDK call SHALL use the prompt cache (`cache_control: {type: "ephemeral"}`) on the system prompt and any large context payloads (e.g. the gateway-transfer table). This is non-negotiable; the prompt cache materially affects cost.

#### Scenario: System prompt is cached

- **WHEN** the copilot issues an Anthropic call
- **THEN** the system prompt is marked `cache_control: {type: "ephemeral"}` so subsequent calls within the 5-minute TTL hit the cache
