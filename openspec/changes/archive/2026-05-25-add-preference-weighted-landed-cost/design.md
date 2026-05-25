## Context

This change layers on `add-flight-orchestrator` (the original Phase-1 design) and the recently archived `migrate-fare-search-to-fli`. It reframes the orchestrator's objective from "cheapest validated party airfare" to "cheapest validated landed cost to the true destination, reordered by elicited traveler preferences."

The reframe is not a feature; it changes what the product *is*. The original orchestrator treated the search as a fare-comparator with party-of-6 fidelity and a SerpAPI honesty pass. That framing has a hard ceiling: even when it is perfectly correct, it answers the wrong question. A user planning to take a family of 6 to Venice does not have a fare problem — they have a *getting to Venice* problem, and fare is one component of the answer. Once we accept that, ranking by fare is obviously broken and the question becomes "how do you encode the rest honestly."

## Goals / Non-Goals

**Goals:**
- Replace the airfare ranking with a landed-cost ranking that includes ground transfer and any forced/intentional overnight lodging.
- Elicit traveler preferences on a single bookended scale per friction axis (HARD NO → soft middle → HARD YES) and apply them to *reorder* — not reprice — the validated result set.
- Establish a hard invariant: cost is computed before scoring, and preferences NEVER mutate cost figures. The cost spine stays interrogable for the entire run lifecycle.
- Make every estimated cost component user-owned and labeled so an LLM (or any model) cannot silently inject a confident-but-wrong number into the cost spine.
- Support the HARD YES stopover case end-to-end: construct the leg, price it, lodge a per-night assumption, and rank the resulting itinerary against direct options on landed cost.

**Non-Goals:**
- Live hotel or rail pricing in v1. Ground transfer is a hardcoded table; lodging is a user-owned per-night number. Scraping either is a second adversarial-website rabbit hole and the value is low — these figures are stable on the timescale of a planning session.
- A blended single "score" column. We do not multiply minutes-of-friction by a fabricated dollar rate. Cost and friction stay individually visible; the user adjudicates.
- Booking, holds, or any transactional surface. We rank and explain.
- Removing the existing fare-search / fare-validation pipeline. Landed cost is computed *on top of* the validated airfare; SerpAPI is still the authoritative validator.
- Discovering the user's true destination automatically. The wizard asks; the LLM may suggest the airport/gateway candidates, but the user names the destination.

## Decisions

### Decision 1: The cost spine is sacred — preferences never mutate cost

Landed cost is computed in a deterministic, pure function from `(itinerary, gateway_transfer_table, cost_assumptions)`. Preferences cannot reach into that function. They run *after*, on the already-priced set, and they can only:
- subtract (HARD NO: remove from the set),
- reorder (soft middle: nudge rank up or down),
- expand the input space (HARD YES: tell the orchestrator to also search a stopover structure, which is then priced through the same honest cost function before ranking).

This separation is the single most important architectural commitment in the change. It is what prevents the failure where a desired feature looks falsely cheap because its desirability earned it a discount, and the failure where an avoided feature looks falsely expensive because its aversiveness earned it a markup. It also makes the ranking debuggable: "this itinerary won because its landed cost is $X and the preference score nudged it up by Y; here is the cost breakdown" is interrogable; "this itinerary scored 0.82" is not.

Implementation consequence: the runner pipeline becomes `sweep → validate → compute landed cost → filter (HARD NO) → score (soft middle) → rank`. Stopover construction (HARD YES) happens *before* sweep — it is a structural addition to the query matrix, not a scoring step.

### Decision 2: One bookended scale per axis (replaces the earlier two-axis design)

Earlier drafts split each axis into "direction (Likert)" and "importance (0-5)". This change collapses both into one OkCupid-style control:

```
HARD NO ── strongly avoid ── avoid ── neutral ── desire ── strongly desire ── HARD YES
```

The information loss is intentional. The user *cannot* express "mild direction, intense importance" in this design. For travel preferences that distinction is essentially academic and the elicitation-burden reduction is large. The harder constraint we gain is that "intensity" stops being a confusable orthogonal axis the user wonders if they got right; the position on the scale IS the intensity.

The scale is **not** a continuous slider — it is exactly seven discrete positions with labels. This matters in the UI: a 0-100 slider invites false precision ("am I a 73 or a 78?"), seven labeled stops invite a categorical choice ("strongly avoid feels right").

### Decision 3: The decisive insight — HARD NO and HARD YES are different operations

Earlier drafts treated both scale-ends as operations on the **result set**, which produced an incoherence: a HARD YES on "stopover" appeared to mean "delete every non-stopover itinerary," which would (rightly) horrify a user who just wanted to lean toward a stopover.

The resolution: separate the operations by *what they act on*.

- **HARD NO** acts on the **result set** → filter (subtractive). "Layover length HARD NO" removes any itinerary with a long layover. The result set is what existed minus the matches.
- **HARD YES** acts on the **itinerary structure** → constructor (additive). "Stopover HARD YES" tells the orchestrator: also build a stopover structure (SJO → [stopover city] → [Italy gateway] with a 1-night gap), price it through the normal pipeline, and include it in the result set. It does NOT delete the non-stopover candidates.
- **Soft middle** acts on the **rank order** → weight (continuous nudge). It cannot exclude and cannot construct.

Once separated, both ends are coherent and the asymmetry that plagued earlier drafts dissolves. A user who hard-yeses a stopover is told "okay, I'll build that into the itinerary structure" and then sees their constructed stopover ranked next to direct options on honest landed cost.

A consequence: HARD YES is only meaningful on axes where there *is* a structural feature to construct. Stopover is the obvious one in v1. HARD YES on "layover length" does not make sense (we are not going to engineer a longer layover for someone — they would just take a direct flight and sit in a café). The elicitation UI must know which axes admit a HARD YES and grey out the HARD YES tick on axes that don't.

### Decision 4: Soft desire and HARD YES are genuinely different controls

"Strongly desire" (soft middle, rightmost position before HARD YES) is an attractor over a mixed set: both stopover and direct itineraries appear; stopover ones rank higher. It is never a requirement. "HARD YES" is the constructor described above.

This makes the top of the soft range and the hard end meaningfully distinct, not just intensities of the same thing. The UI must make this distinction legible — the jump from "strongly desire" to "HARD YES" is a categorical change in what the system will do.

### Decision 5: Ground-transfer data is a hardcoded table for v1, not scraped

Rail/ferry fares between European gateways and Venice are stable on the planning horizon. A maintained table with a `last_reviewed` date is accurate enough and avoids a second adversarial-website rabbit hole. (We just landed `migrate-fare-search-to-fli` precisely because scraper maintenance is a known pain.)

Each entry carries `{mode, per_person_cost, duration_min, transfers, forces_overnight_threshold_local_time, last_reviewed, notes}`. `forces_overnight` is derived per itinerary from the actual arrival time vs. the last viable onward departure, not pre-baked into the table.

Seed scope: `{VCE, MXP, LIN, ZRH, MUC, BLQ, VRN, TRS}` → Venice (rail; ferry where real). FCO is optional. The maintainer commits to a quarterly review.

### Decision 6: Stopover lodging is a user-owned assumption, NEVER a silent model estimate

An LLM estimating hotel cost would inject a confident-but-wrong, date-insensitive number into the cost spine — corrupting the exact thing the spine is supposed to protect. The number must be:
- user-owned (an input field),
- labeled wherever displayed (e.g. "stopover lodging assumption: $320/night family room — your estimate"),
- overridable per itinerary if the user wants to test a different number,
- never silently model-generated.

An LLM MAY pre-fill the input with a labeled suggestion ("rough estimate, verify"), but the suggestion is visibly an estimate and does NOT enter the cost total as if measured. This rule generalises: **no silent model-generated cost components, ever.** It is the dual of Decision 1 — Decision 1 protects cost from preference contamination, this protects cost from model-hallucination contamination.

### Decision 7: Friction is not dollarized

We do not invent a misery-to-money rate. A long layover is shown as "layover: 6h 40m" with a flag if it crosses the user's threshold; it is NOT shown as "+$X equivalent." Two reasons:

1. There is no defensible exchange rate. Different travelers price the same friction wildly differently — that is exactly what preferences are for.
2. Adding a fake dollar value to a real dollar number poisons the spine. The user can no longer interrogate the cost figure they see.

The user adjudicates the money-vs-friction tradeoff with both numbers visible and comparable on their own terms.

### Decision 8: LLM role in this change is elicitation and pre-fill, not pricing or ranking

The LLM may:
- suggest preference defaults from a natural-language description ("traveling with two toddlers" → soft-avoid long layover, soft-avoid red-eye),
- pre-fill cost assumptions as labeled estimates,
- propose stopover waypoint candidates for HARD YES with no named city,
- explain ranking decisions in natural language *after* the deterministic scorer has run.

The LLM may NOT:
- compute or contribute to any cost number that enters the landed-cost total without a label,
- compute or contribute to the rank order,
- filter or construct itineraries — those are the bookended scale's job, driven by the user's setting.

This is what makes the system *LLM-orchestrated* without being LLM-driven. The LLM is in the elicitation and explanation loops; it is not in the cost or ranking loops.

## Failure modes this change prevents

1. **Ranking by fare and picking a "cheap" flight that's expensive to actually use** — the canonical failure of fare comparators. Resolved by Decision 1 (cost is landed cost) + Decision 5 (transfer is priced into the spine).
2. **Double-counting a desired feature (cost + rank boost) so it looks falsely cheap** — resolved by Decision 1 (preferences cannot mutate cost) + the explicit no-double-count requirement in `preference-scoring`.
3. **A "desire" setting silently deleting the cheapest direct option** — resolved by Decision 3 (HARD YES constructs; only HARD NO filters).
4. **A silent LLM hotel estimate corrupting the cost spine** — resolved by Decision 6 + Decision 8.
5. **Blending cost and friction into one opaque score the user cannot interrogate** — resolved by Decision 7 (no dollarization) + the "result presentation is honest about spine vs. preference" requirement.
6. **The orchestrator "knowing better" than the user about their preferences** — resolved by elicitation as the default and the LLM-suggested defaults being editable and labeled as suggestions.

## Open questions deferred to build time

- **Per-gateway transfer numbers and which gateways have real ferry options to Venice** (Trieste / Croatia-adjacent routings) — needs a human pass before seeding. The data model is settled.
- **Waypoint candidate set for unnamed HARD YES stopovers on a transatlantic** — likely MAD, LIS, plus a US-hub set; seed list is user-editable. Open: do we surface the candidate set in the UI before running, or sweep silently and label the results?
- **Per-leg override granularity** — should every axis be per-leg-overridable, or only the commonly-overridden ones (layover length, red-eye)? Lean: full axis set is overridable, UI collapses overrides into a single "leg overrides" accordion to avoid intimidation.
- **Tie-breaking when soft scores are equivalent** — earlier-departure-time? lower-stops? Punt to build; pick whichever produces less perceived randomness in the result list.

## Risks / Trade-offs

- **Risk: stale transfer table.** A rail fare changes between reviews and the user makes a $200 decision on a wrong number. Mitigation: `last_reviewed` is visible inline on every result that uses the figure, and the user can override per assumption.
- **Trade-off: seven discrete preference positions vs. a slider.** We lose the user who wants to express "very mildly avoid" between "neutral" and "avoid." Acceptable; the scale doesn't need that resolution and a slider invites false precision.
- **Trade-off: HARD YES on stopover means more SerpAPI calls.** Each stopover leg adds queries. Mitigation: the user opted in; this is exactly the case where the additional cost is worth it.
- **Risk: the user reads "landed cost" as a guarantee.** It isn't — it's airfare (validated) + transfer (table-priced) + lodging (assumption). Mitigation: the breakdown is always visible and components are labeled by their data source ("validated SerpAPI fare" / "table figure, last reviewed 2026-04" / "your estimate").
- **Risk: scope creep from the UI side back into this change.** The wizard's elicitation flow will surface edge cases that look like backend issues. Mitigation: the contract this change ships is `(config → results)` with `preferences` and `cost_assumptions` as inputs; UI changes go in the companion change, even if they expose new backend gaps. Add to that change's tasks list, don't backflow into this one.
