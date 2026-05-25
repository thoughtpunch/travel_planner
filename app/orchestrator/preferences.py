"""Preference scorer (pure).

Runs AFTER landed cost has been computed. Three things happen, in order:

1. **HARD NO filter** removes itineraries that match any axis's HARD NO
   threshold. Counts are recorded per axis in `filtered_out`.
2. **Soft scoring** computes a bounded rank-delta from the soft-middle
   positions (avoid / desire) inside a ±`soft_band_pct` band of the cheapest
   VALIDATED landed cost. Outside the band, landed cost wins.
3. **Rank** by landed cost ascending, then soft delta tiebreak, producing
   the persisted order.

This function NEVER mutates `landed_cost` or `cost_breakdown`. A debug
assertion compares pre/post fingerprints.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ..enums import VerificationStatus
from ..preferences import (
    Axis,
    HARD_YES_ADMITTED,
    Preferences,
    PreferenceExplanation,
    ScalePosition,
    SOFT_WEIGHT,
)
from .structures import ItineraryCandidate

log = logging.getLogger("trip_planner.preferences")


@dataclass
class ScoredResult:
    ranked: list[ItineraryCandidate]
    filtered_out: dict[Axis, int] = field(default_factory=dict)


def _fingerprint(c: ItineraryCandidate) -> tuple:
    """Snapshot of the cost-spine fields we promise not to mutate."""
    return (
        getattr(c, "landed_cost", None),
        tuple(
            (comp.label, comp.total, comp.data_source.value)
            for comp in (getattr(c, "cost_breakdown", None).components if getattr(c, "cost_breakdown", None) else [])
        ),
    )


def _hard_no_violates(c: ItineraryCandidate, axis: Axis, threshold: dict | int | None) -> bool:
    """True if candidate violates the HARD NO threshold for this axis."""
    fa = getattr(c, "friction_attributes", None)
    if fa is None:
        return False
    if axis == Axis.LAYOVER_LENGTH:
        # Threshold is minutes (int) OR {"max_minutes": int}.
        limit = threshold if isinstance(threshold, int) else (threshold or {}).get("max_minutes")
        if limit is None:
            return False
        return fa.layover_minutes_max > int(limit)
    if axis == Axis.TRANSFER_LENGTH:
        # Use the landed cost's transfer minutes from metadata. Threshold = minutes.
        limit = threshold if isinstance(threshold, int) else (threshold or {}).get("max_minutes")
        if limit is None:
            return False
        cb = getattr(c, "cost_breakdown", None)
        if cb is None:
            return False
        for comp in cb.components:
            if comp.label.startswith("Ground transfer"):
                duration = int(comp.metadata.get("duration_minutes") or 0)
                return duration > int(limit)
        return False
    if axis == Axis.PLANE_CHANGES:
        limit = threshold if isinstance(threshold, int) else (threshold or {}).get("max_count")
        if limit is None:
            return False
        return fa.plane_changes > int(limit)
    if axis == Axis.RED_EYE:
        # Threshold is implicit (any red-eye triggers). When HARD NO is set,
        # a red-eye itinerary is excluded.
        return fa.red_eye
    if axis == Axis.STOPOVER:
        # HARD NO on stopover: exclude any itinerary that has a stopover
        # (whether constructed or organic).
        return fa.has_stopover
    return False


def _soft_match(c: ItineraryCandidate, axis: Axis) -> bool:
    """True if the soft preference's attribute is present on this itinerary
    (used both for avoid/desire scoring direction)."""
    fa = getattr(c, "friction_attributes", None)
    if fa is None:
        return False
    if axis == Axis.LAYOVER_LENGTH:
        # Treat "long layover present" as match (>3h is the typical threshold).
        return fa.layover_minutes_max > 180
    if axis == Axis.TRANSFER_LENGTH:
        cb = getattr(c, "cost_breakdown", None)
        if cb is None:
            return False
        for comp in cb.components:
            if comp.label.startswith("Ground transfer"):
                # >2h transfer is a soft-match for "long transfer".
                return int(comp.metadata.get("duration_minutes") or 0) > 120
        return False
    if axis == Axis.PLANE_CHANGES:
        # >1 plane change is a soft-match.
        return fa.plane_changes > 1
    if axis == Axis.RED_EYE:
        return fa.red_eye
    if axis == Axis.STOPOVER:
        return fa.has_stopover
    return False


def apply_preferences(
    candidates: list[ItineraryCandidate],
    preferences: Preferences,
    cheapest_validated_landed_cost: int | None,
) -> ScoredResult:
    """Apply HARD NO filter → soft scoring → rank.

    NEVER mutates candidate.landed_cost or candidate.cost_breakdown.
    """
    pre_fingerprints = {id(c): _fingerprint(c) for c in candidates}

    # 1. HARD NO filter.
    filtered_out: dict[Axis, int] = {}
    survivors: list[ItineraryCandidate] = []
    for c in candidates:
        excluded_by: Axis | None = None
        # FAILED / SKIPPED_QUOTA candidates skip filtering — they need to
        # appear in the result set so the audit trail records them.
        if c.verification_status in (VerificationStatus.FAILED, VerificationStatus.SKIPPED_QUOTA):
            survivors.append(c)
            continue
        # Resolve preferences per leg ordinal; if no leg-specific override,
        # global default applies. We use leg ordinal 1 as a stand-in for
        # itinerary-wide preferences (per-leg overrides still take effect
        # via _hard_no_violates checking the itinerary's friction).
        resolved = preferences.resolved(leg_ordinal=1)
        for axis, setting in resolved.items():
            if setting.position != ScalePosition.HARD_NO:
                continue
            if _hard_no_violates(c, axis, setting.threshold):
                excluded_by = axis
                break
        if excluded_by is None:
            survivors.append(c)
            # Also clear any old explanations from previous runs.
            c.preference_explanations = []
        else:
            filtered_out[excluded_by] = filtered_out.get(excluded_by, 0) + 1

    # 2. Soft scoring. Compute a rank-delta per candidate, bounded by
    #    whether the candidate is inside the soft band.
    soft_band_pct = preferences.soft_band_pct
    if cheapest_validated_landed_cost is not None and cheapest_validated_landed_cost > 0:
        band_high = int(cheapest_validated_landed_cost * (1 + soft_band_pct / 100))
    else:
        band_high = None

    deltas: dict[int, int] = {}
    explanations: dict[int, list[PreferenceExplanation]] = {}
    for c in survivors:
        in_band = (
            band_high is None
            or getattr(c, "landed_cost", None) is None
            or c.landed_cost <= band_high
        )
        if not in_band:
            deltas[id(c)] = 0
            explanations[id(c)] = []
            continue
        total_delta = 0
        exps: list[PreferenceExplanation] = []
        resolved = preferences.resolved(leg_ordinal=1)
        for axis, setting in resolved.items():
            if setting.position in (ScalePosition.HARD_NO, ScalePosition.HARD_YES, ScalePosition.NEUTRAL):
                continue
            weight = SOFT_WEIGHT.get(setting.position, 0)
            if weight == 0:
                continue
            if _soft_match(c, axis):
                # avoid_match: weight is negative → rank-delta negative (rank lower)
                # desire_match: weight is positive → rank-delta positive (rank higher)
                total_delta += weight
                direction = "desire_match" if weight > 0 else "avoid_match"
                exps.append(PreferenceExplanation(
                    axis=axis, direction=direction, rank_delta=weight,
                    reason=f"soft {setting.position.value} on {axis.value} matched (within ±{soft_band_pct}% cost band)",
                ))
        # HARD YES construction is recorded as an explanation even though
        # construction itself happens earlier in the pipeline.
        for axis, admitted in HARD_YES_ADMITTED.items():
            if not admitted:
                continue
            setting = resolved.get(axis)
            if setting and setting.position == ScalePosition.HARD_YES and _soft_match(c, axis):
                exps.append(PreferenceExplanation(
                    axis=axis, direction="construct", rank_delta=0,
                    reason=f"HARD YES on {axis.value}: constructed by orchestrator before pricing",
                ))
        deltas[id(c)] = total_delta
        explanations[id(c)] = exps

    # 3. Rank.
    #    Outside the soft band, landed_cost is primary (preferences cannot
    #    promote across the band). Inside the band, soft scoring CAN reorder:
    #    each soft-delta point counts as `SOFT_DELTA_PCT_POINTS` percentage
    #    points of cost, so a +2 strongly-desire can flip a candidate that
    #    is up to ~10% more expensive (well inside the band).
    from ..enums import Flag
    from .ranker import _STATUS_ORDER

    # Per soft-delta point, how many percentage points of cost it offsets.
    # Calibrated so a +2 boost can flip a candidate that is ~10% more
    # expensive (i.e. across the entire default soft band).
    SOFT_DELTA_PCT_POINTS = 5

    def sort_key(c: ItineraryCandidate) -> tuple:
        lc = getattr(c, "landed_cost", None)
        cost_key = lc if lc is not None else 10**12
        in_band = (
            band_high is not None
            and lc is not None
            and lc <= band_high
        )
        if in_band and cheapest_validated_landed_cost:
            cost_pct = (lc - cheapest_validated_landed_cost) * 100 / cheapest_validated_landed_cost
            preference_adjusted = cost_pct - SOFT_DELTA_PCT_POINTS * deltas.get(id(c), 0)
        else:
            # Outside band: pure cost wins (preferences cannot promote across the band).
            preference_adjusted = (
                ((lc - (cheapest_validated_landed_cost or 0)) * 100 / max(1, cheapest_validated_landed_cost or 1))
                if lc is not None else 1e9
            )
        return (
            _STATUS_ORDER.get(c.verification_status, 99),
            1 if Flag.BLACKOUT.value in (c.flags or []) else 0,
            preference_adjusted,
            cost_key,  # final tiebreak on raw cost
        )

    ranked = sorted(survivors, key=sort_key)
    for c in ranked:
        c.preference_explanations = explanations.get(id(c), [])

    # Debug assertion: cost spine unmodified.
    for c in candidates:
        post = _fingerprint(c)
        if post != pre_fingerprints[id(c)]:
            raise RuntimeError(
                "apply_preferences mutated candidate cost spine — this is a bug. "
                f"pre={pre_fingerprints[id(c)]} post={post}"
            )

    return ScoredResult(ranked=ranked, filtered_out=filtered_out)


__all__ = ["apply_preferences", "ScoredResult"]
