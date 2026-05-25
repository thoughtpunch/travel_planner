"""Anthropic SDK wrapper for the wizard copilot.

Stubbed for v1 — returns deterministic seeded suggestions so the SPA can be
built and tested without a real API key. When `ANTHROPIC_API_KEY` is set
and the `anthropic` package is installed, swap `_stub_*` for a real call.
The prompt-cache discipline (`cache_control: ephemeral` on the system
prompt and large context payloads) is documented and enforced when real
calls are wired in.
"""

from __future__ import annotations

import os
from typing import Any

from ..schemas import CopilotResponse, CopilotSuggestion


def _stub_preference_suggestions(natural_language: str) -> list[CopilotSuggestion]:
    nl = natural_language.lower()
    out: list[CopilotSuggestion] = []
    if any(k in nl for k in ("red-eye", "red eye", "toddler", "baby", "infant")):
        out.append(CopilotSuggestion(
            path="preferences.defaults.red_eye",
            value={"position": "strongly_avoid"},
            confidence=0.9,
            rationale="Family with young children — avoid pre-dawn arrivals.",
        ))
    if any(k in nl for k in ("layover", "wait", "long stop")):
        out.append(CopilotSuggestion(
            path="preferences.defaults.layover_length",
            value={"position": "avoid", "threshold": 180},
            confidence=0.8,
            rationale="Long layovers compound fatigue; soft-avoid > 3h.",
        ))
    if any(k in nl for k in ("stopover", "break", "rest stop", "two day", "couple days")):
        out.append(CopilotSuggestion(
            path="preferences.defaults.stopover",
            value={"position": "desire"},
            confidence=0.6,
            rationale="You mentioned a rest break — soft-desire stopover (use HARD YES to actually construct one).",
        ))
    if not out:
        out.append(CopilotSuggestion(
            path="preferences.defaults.layover_length",
            value={"position": "neutral"},
            confidence=0.3,
            rationale="No strong signal in description; leaving layover at neutral.",
        ))
    return out


def _stub_cost_assumption_suggestions(trip_context: dict[str, Any]) -> list[CopilotSuggestion]:
    """Cost suggestions ALWAYS carry unverified=True per the wizard-copilot
    spec. The gateway rejects any cost suggestion without it."""
    party = int(trip_context.get("party", 6))
    rooms = max(1, (party + 2) // 3)
    nightly = 320 if rooms <= 2 else 200 * rooms
    return [
        CopilotSuggestion(
            path="cost_assumptions.stopover_lodging_per_night",
            value=nightly,
            confidence=0.5,
            rationale=(
                f"Rough seasonal estimate for {rooms} family rooms in a "
                "transit-city mid-tier hotel — verify against your actual destination."
            ),
            unverified=True,
        ),
        CopilotSuggestion(
            path="cost_assumptions.stopover_rooms",
            value=rooms,
            confidence=0.7,
            rationale=f"{rooms} rooms covers a party of {party}.",
            unverified=True,
        ),
    ]


def _stub_stopover_candidates(origin: str, gateways: list[str]) -> list[str]:
    if origin == "SJO":
        return ["MAD", "LIS", "LHR", "FRA"]
    return ["MAD", "LIS", "LHR"]


def suggest_preferences(natural_language: str) -> CopilotResponse:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return CopilotResponse(suggestions=_stub_preference_suggestions(natural_language))
    # Real Anthropic call path lives here when wired (claude-api skill —
    # prompt-cache: system + gateway-transfer table marked ephemeral).
    return CopilotResponse(suggestions=_stub_preference_suggestions(natural_language))


def suggest_cost_assumptions(trip_context: dict[str, Any]) -> CopilotResponse:
    return CopilotResponse(suggestions=_stub_cost_assumption_suggestions(trip_context))


def suggest_stopover_waypoints(origin: str, gateways: list[str]) -> dict[str, Any]:
    return {
        "candidates": _stub_stopover_candidates(origin, gateways),
        "rationale": "Natural transatlantic waypoints; reorder or replace as you wish.",
    }


__all__ = ["suggest_preferences", "suggest_cost_assumptions", "suggest_stopover_waypoints"]
