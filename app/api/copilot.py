"""Copilot endpoints with cost-honesty + forbidden-path enforcement.

Per the `wizard-copilot` spec and the design's Decision 5/8:
- Suggestions targeting a cost field path (`cost_assumptions.*` or
  `transfer_overrides.*`) MUST carry `unverified=True`. The gateway rejects
  responses violating this with 502 (upstream contract violation).
- Suggestions targeting result-set or rank paths are forbidden (422).
- Allowed paths: config inputs only — `preferences.*`, `cost_assumptions.*`,
  `stopover_target.*`, gateway selections, date windows, party fields.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ..llm.copilot_client import (
    suggest_cost_assumptions,
    suggest_preferences,
    suggest_stopover_waypoints,
)
from ..schemas import (
    CopilotResponse,
    CostAssumptionSuggestRequest,
    PreferenceSuggestRequest,
    StopoverWaypointSuggestRequest,
)

router = APIRouter(prefix="/api/copilot", tags=["copilot"])
log = logging.getLogger("trip_planner.copilot")

COST_PATH_PREFIXES = ("cost_assumptions.", "preferences.cost_", "transfer_overrides.")
ALLOWED_PATH_PREFIXES = (
    "preferences.",
    "cost_assumptions.",
    "stopover_target.",
    "passengers.",
    "blackout_ranges",
    "structures",
    "currency",
    "name",
    "budget_party_total",
)


def _enforce_contract(resp: CopilotResponse) -> CopilotResponse:
    """Reject responses that:
      (a) target a cost path without unverified=True
      (b) target a path outside the allowed config-input set
    """
    for s in resp.suggestions:
        path = s.path
        is_cost = any(path.startswith(p) for p in COST_PATH_PREFIXES)
        if is_cost and not s.unverified:
            log.warning("copilot contract violation: cost suggestion without unverified flag: %s", path)
            raise HTTPException(
                502,
                f"copilot contract violation: cost field '{path}' suggestion missing unverified=True",
            )
        if not any(path.startswith(p) for p in ALLOWED_PATH_PREFIXES):
            log.warning("copilot contract violation: forbidden path: %s", path)
            raise HTTPException(
                422,
                f"copilot contract violation: forbidden path '{path}'",
            )
    return resp


@router.post("/preferences/suggest", response_model=CopilotResponse)
def preferences_suggest(payload: PreferenceSuggestRequest):
    resp = suggest_preferences(payload.natural_language)
    return _enforce_contract(resp)


@router.post("/cost_assumptions/suggest", response_model=CopilotResponse)
def cost_assumptions_suggest(payload: CostAssumptionSuggestRequest):
    resp = suggest_cost_assumptions(payload.trip_context)
    return _enforce_contract(resp)


@router.post("/stopover_waypoints/suggest")
def stopover_waypoints_suggest(payload: StopoverWaypointSuggestRequest):
    return suggest_stopover_waypoints(payload.origin, payload.destination_gateways)


__all__ = ["router"]
