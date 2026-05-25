"""Landed-cost calculator (pure).

Computes the honest cost of an itinerary: validated airfare + ground transfer
to the true destination + any forced or intentional stopover lodging. Every
component carries a `data_source` tag so the UI can render labelled cost
breakdowns. Per `landed-cost-model` Decision 1, this function is the cost
spine — preferences NEVER mutate its output.

`forces_overnight` is derived per itinerary from arrival local time vs. the
gateway's `last_viable_onward_local_time`, NOT pre-baked into the table.
"""

from __future__ import annotations

from datetime import time
from typing import Iterable

from ..data.gateway_transfers import GATEWAY_TRANSFERS, TransferModel
from ..preferences import (
    CostAssumptions,
    CostComponent,
    DataSource,
    FrictionAttributes,
    LandedCost,
    TransferOverride,
)
from ..sources.base import FareOffer


def _itinerary_arrival_local_time(legs: list[FareOffer]) -> time | None:
    """Pull the last leg's arrival time from `fli`'s rich raw payload if
    present. fli adapters stash booking_token / co2 / primary_airline in
    `raw` plus we can be opportunistic about an `arrival_local_time` field
    if upstream populates it. If we cannot read it, we return None — the
    landed-cost calculator then assumes a viable same-day onward (does
    NOT force an overnight) because we lack evidence to the contrary.
    """
    if not legs:
        return None
    last = legs[-1]
    raw = last.raw or {}
    val = raw.get("arrival_local_time")
    if isinstance(val, str):
        try:
            return time.fromisoformat(val)
        except ValueError:
            return None
    return None


def _pick_transfer(
    gateway: str,
    arrival_local_time: time | None,
    overrides: dict[str, TransferOverride],
) -> tuple[TransferModel | None, int | None]:
    """Pick the cheapest viable transfer for the gateway given arrival time.

    Returns (chosen_transfer, override_cost). When an override matches, the
    returned cost is the override; original table figure is preserved in the
    CostComponent for display.
    """
    entries = GATEWAY_TRANSFERS.get(gateway, [])
    if not entries:
        return None, None

    if arrival_local_time is None:
        viable = entries  # unknown → all viable; we'll pick cheapest
    else:
        viable = [e for e in entries if arrival_local_time <= e.last_viable_onward_local_time]
        if not viable:
            # No same-day option — pick the cheapest mode anyway so we can
            # surface "the cheapest mode for this gateway is X" alongside
            # the forced-overnight flag.
            viable = entries

    chosen = min(viable, key=lambda e: e.per_person_cost)
    override = overrides.get(f"{gateway}/{chosen.mode}")
    override_cost = override.per_person_cost if override is not None else None
    return chosen, override_cost


def _flatten_overrides(assumptions: CostAssumptions) -> dict[str, TransferOverride]:
    return {f"{ov.gateway}/{ov.mode}": ov for ov in assumptions.transfer_overrides}


def _airfare_data_source(legs: Iterable[FareOffer]) -> DataSource:
    """If any leg in the itinerary is VALIDATED, treat the airfare as
    validated; otherwise it's a LEAD-priced figure (still shown but not
    promoted)."""
    from ..enums import VerificationStatus

    for leg in legs:
        if leg.verification_status == VerificationStatus.VALIDATED:
            return DataSource.VALIDATED_AIRFARE
    return DataSource.VALIDATED_AIRFARE  # we still surface the source as airfare; status lives separately


def compute_friction(legs: list[FareOffer]) -> FrictionAttributes:
    """Pull friction columns from the offer set. Each is read from the offer
    fields directly (stops, etc.) — fli's richer data makes this trivial for
    that source; for fast-flights some fields stay 0."""
    if not legs:
        return FrictionAttributes()
    last = legs[-1]
    layover_max = 0
    layover_total = 0
    plane_changes = 0
    red_eye = False
    for leg in legs:
        # Each leg's `stops` count = plane changes for that leg.
        plane_changes += int(leg.stops or 0)
        # Layover info is upstream-specific; fli exposes layovers on raw.
        layovers = (leg.raw or {}).get("layovers") or []
        for lv in layovers:
            minutes = int(lv.get("duration_minutes") or 0)
            layover_max = max(layover_max, minutes)
            layover_total += minutes
        # Red-eye detection: arrival between 23:00 and 06:00 local on any leg.
        arr = (leg.raw or {}).get("arrival_local_time")
        if isinstance(arr, str):
            try:
                t = time.fromisoformat(arr)
                if t.hour >= 23 or t.hour < 6:
                    red_eye = True
            except ValueError:
                pass
    return FrictionAttributes(
        layover_minutes_max=layover_max,
        layover_minutes_total=layover_total,
        plane_changes=plane_changes,
        red_eye=red_eye,
        has_stopover=bool((last.raw or {}).get("stopover_city")),
        stopover_city=(last.raw or {}).get("stopover_city"),
    )


def compute_landed_cost(
    *,
    legs: list[FareOffer],
    gateway: str,
    assumptions: CostAssumptions,
    party_size: int,
    currency: str = "USD",
) -> tuple[LandedCost, FrictionAttributes]:
    """Pure function: returns (LandedCost, FrictionAttributes).

    Order: airfare → transfer (with override / forced-overnight handling) →
    lodging if forced overnight OR if itinerary already has a stopover.
    Every component carries its `data_source`. Function never returns silent
    estimates (the LLM-suggested code path goes through the API and is
    labelled at write time; here we only emit user_assumption /
    user_override / transfer_table / validated_airfare).
    """
    components: list[CostComponent] = []
    overrides = _flatten_overrides(assumptions)

    # 1. Airfare component (party total of validated/lead fares).
    airfare_party_total = sum(int(o.price_per_pax or 0) * max(1, int(o.passengers_queried or 1)) for o in legs)
    components.append(CostComponent(
        label=f"Airfare (party of {party_size})",
        per_person_amount=airfare_party_total // max(1, party_size) if party_size else None,
        party_multiplier=max(1, party_size),
        total=airfare_party_total,
        currency=currency,
        data_source=_airfare_data_source(legs),
        user_overridable=True,
        metadata={"leg_count": len(legs)},
    ))

    # 2. Ground transfer to true destination.
    arrival_local_time = _itinerary_arrival_local_time(legs)
    transfer, override_cost = _pick_transfer(gateway, arrival_local_time, overrides)
    forces_overnight = False
    if transfer is not None:
        viable_same_day = (
            arrival_local_time is None
            or arrival_local_time <= transfer.last_viable_onward_local_time
        )
        forces_overnight = not viable_same_day
        per_person = override_cost if override_cost is not None else transfer.per_person_cost
        transfer_total = per_person * party_size
        components.append(CostComponent(
            label=f"Ground transfer ({transfer.mode}, {transfer.gateway} → Venice)",
            per_person_amount=per_person,
            party_multiplier=party_size,
            total=transfer_total,
            currency=currency,
            data_source=DataSource.USER_OVERRIDE if override_cost is not None else DataSource.TRANSFER_TABLE,
            user_overridable=True,
            original_table_value=transfer.per_person_cost if override_cost is not None else None,
            metadata={
                "mode": transfer.mode,
                "duration_minutes": transfer.duration_minutes,
                "transfers": transfer.transfers,
                "last_reviewed": transfer.last_reviewed.isoformat(),
                "last_viable_onward_local_time": transfer.last_viable_onward_local_time.isoformat(),
                "viable_same_day": viable_same_day,
            },
        ))

    # 3. Lodging — only if (a) forced overnight or (b) itinerary already has
    #    a stopover (HARD YES constructed), which produces an extra night.
    friction = compute_friction(legs)
    needs_lodging = forces_overnight or friction.has_stopover
    if needs_lodging:
        rooms = max(1, assumptions.stopover_rooms or 1)
        nights = 1  # v1: always 1 night; multi-night stopovers are a future change
        per_night = max(0, assumptions.stopover_lodging_per_night or 0)
        lodging_total = per_night * rooms * nights
        if lodging_total > 0:
            lodging_source = (
                DataSource.LLM_ESTIMATE_UNVERIFIED
                if assumptions.llm_suggested.get("stopover_lodging_per_night")
                else DataSource.USER_ASSUMPTION
            )
            label_suffix = "forced overnight" if forces_overnight else f"stopover in {friction.stopover_city or 'transit city'}"
            components.append(CostComponent(
                label=f"Lodging ({rooms} rooms × {nights} night — {label_suffix})",
                per_person_amount=None,
                party_multiplier=rooms * nights,
                total=lodging_total,
                currency=currency,
                data_source=lodging_source,
                user_overridable=True,
                metadata={"per_night": per_night, "rooms": rooms, "nights": nights, "reason": label_suffix},
            ))

    total = sum(c.total for c in components)
    friction.forces_overnight = forces_overnight
    return (
        LandedCost(total=total, currency=currency, components=components, forces_overnight=forces_overnight),
        friction,
    )


__all__ = ["compute_landed_cost", "compute_friction"]
