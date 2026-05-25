## ADDED Requirements

### Requirement: Structured-form-first copilot

The LLM copilot SHALL operate in a structured-form-first mode: the wizard form is the source of truth, the copilot can ONLY produce field-targeted suggestions (`{path, value, confidence, rationale}`), and the SPA SHALL render every suggestion as an inline `Card` with Accept / Edit / Reject `Button`s. The copilot SHALL NEVER mutate config state directly; only the user's Accept action (or explicit edit) writes the value.

The copilot SHALL be invocable from:
- The wizard header (a `Drawer` toggle that opens a Drawer with a natural-language input + suggestion list).
- Specific fields with a `Sparkle` icon button (per-field suggest — "What would you suggest for this?").

The copilot SHALL be disable-able in Settings; when disabled the Drawer toggle is hidden and per-field `Sparkle` icons are hidden.

#### Scenario: Drawer suggestion flow

- **WHEN** the operator opens the copilot Drawer and enters "family with two toddlers, dad has a bad back, hate red-eyes"
- **THEN** the SPA POSTs to `/api/copilot/preferences/suggest`
- **AND** the response renders as a list of inline `Card`s — one per suggested field — each with the suggested value, confidence, rationale, and Accept/Edit/Reject `Button`s
- **AND** clicking Accept writes the value into the form AND marks `llm_suggested.<path> = true`
- **AND** clicking Edit opens the field in the wizard with the suggested value pre-filled but un-flagged (the operator's edit clears the suggestion mark)
- **AND** clicking Reject dismisses the suggestion with no state change

#### Scenario: Per-field suggest

- **WHEN** the operator clicks the `Sparkle` icon next to the stopover lodging field
- **THEN** the copilot is invoked with the field path as context
- **AND** the suggestion appears in an `OverlayPanel` anchored to the field
- **AND** all the same Accept/Edit/Reject affordances apply

### Requirement: Copilot may not contribute to cost numbers without a label

Any copilot suggestion targeting a cost field (any path under `cost_assumptions.*` or `transfer_overrides.*`) SHALL be returned by the API with `unverified: true`. The SPA SHALL render such values with `<DataSourceTag :source="llm_estimate_unverified" />` and label "suggested — verify" until the operator accepts or edits.

The API gateway SHALL validate the copilot's response: a cost-field suggestion missing `unverified: true` SHALL be rejected with 502 and logged as a contract violation. This is the dual of `landed-cost-model`'s "Cost components are honest" requirement, enforced at the LLM boundary.

#### Scenario: Cost suggestion is labelled and unwritable without confirmation

- **WHEN** the copilot suggests `cost_assumptions.stopover_lodging_per_night = 32000` with `unverified: true`
- **THEN** the SPA renders it with the `llm_estimate_unverified` data-source tag and a "suggested — verify" `Tag`
- **AND** the value does NOT enter any landed-cost computation until the operator confirms (Accept) or edits

#### Scenario: Missing unverified flag is rejected

- **WHEN** the LLM provider returns a cost-field suggestion without `unverified: true`
- **THEN** the API gateway rejects the response with 502 and a `Toast` surfaces a "copilot contract violation" message to the operator
- **AND** no suggestion is written to the form

### Requirement: Copilot may not produce filtering or ranking decisions

The copilot SHALL NOT return suggestions whose `path` targets the result set, the rank order, or any post-validation pipeline output. Allowed paths are restricted to config inputs: `preferences.*`, `cost_assumptions.*`, `stopover_target.*`, gateway selections, date windows, and party fields.

The API gateway SHALL reject suggestions targeting forbidden paths with 422 and log the attempt.

#### Scenario: Forbidden path rejected

- **WHEN** the copilot attempts to return `{path: "results.exclude_itinerary_ids", value: [...]}`
- **THEN** the API gateway rejects with 422 and a `Toast` surfaces the contract violation to the operator
- **AND** no suggestion is written

### Requirement: Copilot rationales are part of the audit trail

Every accepted copilot suggestion SHALL be persisted with its rationale text and timestamp on the config (or the trip, if the suggestion targets trip-level metadata) as `copilot_history: [{path, value, rationale, accepted_at, accepted_by}]`.

This is so a future operator (or the same operator weeks later) can answer "why was this value here? did I choose it or did the copilot?" without ambiguity.

#### Scenario: Audit trail visibility

- **WHEN** the operator accepts a copilot suggestion
- **THEN** an entry is appended to `copilot_history` on the config
- **AND** the wizard field's hover `Tooltip` surfaces the originating rationale text
- **AND** the operator can view the full `copilot_history` from a Settings → "AI suggestions log" panel

### Requirement: Copilot prompt-cache discipline (Anthropic SDK)

The copilot's Anthropic SDK calls SHALL use the prompt cache (`cache_control: {type: "ephemeral"}`) on the system prompt and any large context payloads (e.g. the gateway-transfer table). This is non-negotiable; the prompt cache materially affects cost.

#### Scenario: System prompt is cached

- **WHEN** the copilot issues an Anthropic call
- **THEN** the system prompt is marked `cache_control: {type: "ephemeral"}` so subsequent calls within the 5-minute TTL hit the cache
- **AND** the gateway-transfer-table context (if included) is similarly cached
