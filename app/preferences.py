"""Preference + cost-assumption types.

Lives outside `schemas.py` because both the API layer AND the orchestrator
consume these. The `@model_validator` on `Preferences` and `CostAssumptions`
encodes the incoherence guards from the `preference-elicitation` and
`search-config` specs — invalid configs are rejected at the boundary, not
silently absorbed by the runner.

Cost is measured in whole currency units consistent with the rest of the
system (USD by default).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Axis(StrEnum):
    TRANSFER_LENGTH = "transfer_length"
    LAYOVER_LENGTH = "layover_length"
    STOPOVER = "stopover"
    PLANE_CHANGES = "plane_changes"
    RED_EYE = "red_eye"


class ScalePosition(StrEnum):
    HARD_NO = "hard_no"
    STRONGLY_AVOID = "strongly_avoid"
    AVOID = "avoid"
    NEUTRAL = "neutral"
    DESIRE = "desire"
    STRONGLY_DESIRE = "strongly_desire"
    HARD_YES = "hard_yes"


# Axes that admit a meaningful HARD YES. Only `stopover` in v1 — HARD YES on
# layover-length / plane-changes / red-eye / transfer-length is not a thing
# the orchestrator can construct.
HARD_YES_ADMITTED: dict[Axis, bool] = {
    Axis.TRANSFER_LENGTH: False,
    Axis.LAYOVER_LENGTH: False,
    Axis.STOPOVER: True,
    Axis.PLANE_CHANGES: False,
    Axis.RED_EYE: False,
}


# Soft-middle ranking weights in deltas; HARD NO and HARD YES are operations,
# not weights, so they're absent from this map.
SOFT_WEIGHT: dict[ScalePosition, int] = {
    ScalePosition.STRONGLY_AVOID: -2,
    ScalePosition.AVOID: -1,
    ScalePosition.NEUTRAL: 0,
    ScalePosition.DESIRE: +1,
    ScalePosition.STRONGLY_DESIRE: +2,
}


class AxisSetting(BaseModel):
    """One axis's scale position plus optional threshold.

    `threshold` shape depends on the axis: layover_length / transfer_length →
    int minutes; plane_changes → int count; red_eye → {"window_local": [str,
    str]}; stopover with HARD YES → {"city": str} | {"sweep_candidates":
    list[str]} (carried on `Preferences.stopover_target` rather than here).
    """

    model_config = ConfigDict(extra="forbid")

    position: ScalePosition = ScalePosition.NEUTRAL
    threshold: dict[str, Any] | int | None = None


class StopoverTarget(BaseModel):
    """HARD YES stopover target — either a named city or a candidate sweep."""

    model_config = ConfigDict(extra="forbid")

    city: str | None = None
    sweep_candidates: list[str] | None = None

    @model_validator(mode="after")
    def _city_xor_sweep(self) -> StopoverTarget:
        if (self.city is None) == (self.sweep_candidates is None):
            raise ValueError("stopover_target requires exactly one of: city, sweep_candidates")
        if self.sweep_candidates is not None and not self.sweep_candidates:
            raise ValueError("sweep_candidates may not be empty")
        return self


class PerLegOverride(BaseModel):
    model_config = ConfigDict(extra="forbid")

    leg_ordinal: int = Field(ge=1)
    axis: Axis
    position: ScalePosition = ScalePosition.NEUTRAL
    threshold: dict[str, Any] | int | None = None


class Preferences(BaseModel):
    """Global defaults + per-leg overrides + HARD YES stopover target.

    Validation here rejects: HARD YES on non-admitted axes, missing
    stopover_target when stopover is HARD YES, duplicate (leg, axis)
    overrides.
    """

    model_config = ConfigDict(extra="forbid")

    defaults: dict[Axis, AxisSetting] = Field(default_factory=dict)
    per_leg_overrides: list[PerLegOverride] = Field(default_factory=list)
    stopover_target: StopoverTarget | None = None
    # Soft-band % of cheapest VALIDATED landed cost in which soft scoring
    # may reorder. Outside the band, cost wins. Spec default 10.
    soft_band_pct: int = Field(default=10, ge=0, le=100)

    @model_validator(mode="after")
    def _validate(self) -> Preferences:
        # Defaults: HARD YES only on admitted axes; HARD YES stopover needs target.
        for axis, setting in self.defaults.items():
            if setting.position == ScalePosition.HARD_YES and not HARD_YES_ADMITTED.get(axis, False):
                raise ValueError(
                    f"preferences.defaults.{axis.value}: HARD YES is not meaningful for this axis"
                )
        # Per-leg overrides: same rules + no dup (leg, axis).
        seen: set[tuple[int, Axis]] = set()
        for ov in self.per_leg_overrides:
            key = (ov.leg_ordinal, ov.axis)
            if key in seen:
                raise ValueError(f"duplicate per-leg override for leg {ov.leg_ordinal}, axis {ov.axis.value}")
            seen.add(key)
            if ov.position == ScalePosition.HARD_YES and not HARD_YES_ADMITTED.get(ov.axis, False):
                raise ValueError(
                    f"per_leg_overrides[leg={ov.leg_ordinal}].{ov.axis.value}: HARD YES is not meaningful"
                )
        # HARD YES stopover requires stopover_target.
        stopover_default = self.defaults.get(Axis.STOPOVER)
        stopover_hard_yes_global = (
            stopover_default is not None and stopover_default.position == ScalePosition.HARD_YES
        )
        stopover_hard_yes_leg = any(
            ov.axis == Axis.STOPOVER and ov.position == ScalePosition.HARD_YES
            for ov in self.per_leg_overrides
        )
        if (stopover_hard_yes_global or stopover_hard_yes_leg) and self.stopover_target is None:
            raise ValueError("preferences: HARD YES on stopover requires stopover_target")
        return self

    def resolved(self, leg_ordinal: int) -> dict[Axis, AxisSetting]:
        """Return the effective preference set for a specific leg ordinal:
        global defaults overlaid with per-leg overrides."""
        out: dict[Axis, AxisSetting] = {
            axis: AxisSetting(position=ScalePosition.NEUTRAL) for axis in Axis
        }
        for axis, setting in self.defaults.items():
            out[axis] = setting
        for ov in self.per_leg_overrides:
            if ov.leg_ordinal == leg_ordinal:
                out[ov.axis] = AxisSetting(position=ov.position, threshold=ov.threshold)
        return out


class TransferOverride(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gateway: str
    mode: str  # rail | ferry | bus | drive
    per_person_cost: int = Field(ge=0)


class CostAssumptions(BaseModel):
    """User-owned cost assumptions snapshotted into each run.

    `llm_suggested` tracks which fields are unverified LLM pre-fills — anything
    in here is rendered with the `llm_estimate_unverified` data-source tag
    until the user explicitly confirms by editing or re-saving.
    """

    model_config = ConfigDict(extra="forbid")

    stopover_lodging_per_night: int = Field(default=0, ge=0)
    stopover_rooms: int = Field(default=2, ge=1)
    transfer_overrides: list[TransferOverride] = Field(default_factory=list)
    llm_suggested: dict[str, bool] = Field(default_factory=dict)


class DataSource(StrEnum):
    VALIDATED_AIRFARE = "validated_airfare"
    TRANSFER_TABLE = "transfer_table"
    USER_ASSUMPTION = "user_assumption"
    USER_OVERRIDE = "user_override"
    LLM_ESTIMATE_UNVERIFIED = "llm_estimate_unverified"


class CostComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str  # human-readable, e.g. "Airfare (party of 6)"
    per_person_amount: int | None  # None if not per-person (lodging is per-night × rooms)
    party_multiplier: int  # how many we paid for (party size for fare/transfer, rooms × nights for lodging)
    total: int  # per_person × multiplier (or rooms × nights × per_night for lodging)
    currency: str
    data_source: DataSource
    user_overridable: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    # Original table figure when this component was overridden — preserved
    # for display per the landed-cost-model "override per assumption" scenario.
    original_table_value: int | None = None


class LandedCost(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    currency: str
    components: list[CostComponent]
    forces_overnight: bool = False


class FrictionAttributes(BaseModel):
    """Per-itinerary friction attributes, computed during landed-cost.

    These feed both the soft-scoring step (`apply_preferences`) and the UI
    columns. Computed once, used twice; never mutated by scoring.
    """

    model_config = ConfigDict(extra="forbid")

    transfer_minutes: int = 0
    layover_minutes_max: int = 0
    layover_minutes_total: int = 0
    plane_changes: int = 0
    red_eye: bool = False
    has_stopover: bool = False
    stopover_city: str | None = None
    forces_overnight: bool = False


class PreferenceExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    axis: Axis
    direction: Literal[
        "filter_match",  # HARD NO removed it (only on rejected items)
        "construct",  # HARD YES constructed it
        "desire_match",  # soft desire boost
        "avoid_match",  # soft avoid penalty
        "neutral",
    ]
    rank_delta: int  # signed; ignored for filter_match / construct entries
    reason: str


__all__ = [
    "Axis",
    "ScalePosition",
    "HARD_YES_ADMITTED",
    "SOFT_WEIGHT",
    "AxisSetting",
    "StopoverTarget",
    "PerLegOverride",
    "Preferences",
    "TransferOverride",
    "CostAssumptions",
    "DataSource",
    "CostComponent",
    "LandedCost",
    "FrictionAttributes",
    "PreferenceExplanation",
]
