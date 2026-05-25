"""Assemble itineraries from per-leg fare offers.

Structure A — Three one-ways: best (cheapest) offer per leg, gateway-aligned.
Structure B — Nested envelope: SJO⇄DC round-trip outer + DC⇄EU round-trip inner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from ..enums import Flag, Structure, VerificationStatus
from ..gateways import venice_metadata
from ..preferences import FrictionAttributes, LandedCost, PreferenceExplanation
from ..sources.base import FareOffer
from .blackout import is_blackout
from .dates import parse_date


@dataclass
class ItineraryCandidate:
    structure: Structure
    legs: list[FareOffer]
    gateway: str
    total_party_price: int
    currency: str
    flags: list[str] = field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.LEAD
    # Landed-cost + scoring fields (populated by the orchestrator after
    # validation; preferences.apply_preferences sets explanations).
    landed_cost: int | None = None
    cost_breakdown: LandedCost | None = None
    friction_attributes: FrictionAttributes | None = None
    preference_explanations: list[PreferenceExplanation] = field(default_factory=list)


def _party_total(offers: list[FareOffer]) -> int:
    return sum(o.price_per_pax * max(1, o.passengers_queried) for o in offers)


def _worst_status(offers: list[FareOffer]) -> VerificationStatus:
    """Composite status — itinerary is only as validated as its weakest leg."""
    statuses = {o.verification_status for o in offers}
    if VerificationStatus.FAILED in statuses:
        return VerificationStatus.FAILED
    if VerificationStatus.SKIPPED_QUOTA in statuses:
        return VerificationStatus.SKIPPED_QUOTA
    if VerificationStatus.VALIDATION_FAILED in statuses:
        return VerificationStatus.VALIDATION_FAILED
    if VerificationStatus.STALE in statuses:
        return VerificationStatus.STALE
    if VerificationStatus.LEAD in statuses:
        return VerificationStatus.LEAD
    return VerificationStatus.VALIDATED


def _cheapest_per_route(offers: list[FareOffer]) -> dict[tuple[str, str, str], FareOffer]:
    by_route: dict[tuple[str, str, str], FareOffer] = {}
    for o in offers:
        key = (o.origin, o.destination, o.date)
        prev = by_route.get(key)
        if prev is None or o.price_per_pax < prev.price_per_pax:
            by_route[key] = o
    return by_route


def assemble_structure_a(
    leg1_offers: list[FareOffer],  # SJO → EU gateway
    leg2_offers: list[FareOffer],  # EU gateway → DC airport
    leg3_offers: list[FareOffer],  # DC airport → SJO
    blackout_ranges: list[dict[str, str]],
    currency: str = "USD",
) -> list[ItineraryCandidate]:
    """For each (EU gateway, DC airport) pair, pick cheapest per leg."""
    l1 = _cheapest_per_route(leg1_offers)
    l2 = _cheapest_per_route(leg2_offers)
    l3 = _cheapest_per_route(leg3_offers)

    # Group by (eu_gateway, dc_airport) and pick best across date combos.
    candidates: list[ItineraryCandidate] = []
    eu_gateways = sorted({k[1] for k in l1})
    dc_airports = sorted({k[1] for k in l2})

    for eu in eu_gateways:
        # cheapest leg1 SJO → eu
        l1_options = [v for k, v in l1.items() if k[1] == eu]
        if not l1_options:
            continue
        best_l1 = min(l1_options, key=lambda o: o.price_per_pax)
        for dc in dc_airports:
            l2_options = [v for k, v in l2.items() if k[0] == eu and k[1] == dc]
            l3_options = [v for k, v in l3.items() if k[0] == dc]
            if not l2_options or not l3_options:
                continue
            best_l2 = min(l2_options, key=lambda o: o.price_per_pax)
            best_l3 = min(l3_options, key=lambda o: o.price_per_pax)

            legs = [best_l1, best_l2, best_l3]
            flags = []
            for leg in legs:
                if is_blackout(leg.date, blackout_ranges):
                    flags.append(Flag.BLACKOUT.value)
                    break

            candidates.append(
                ItineraryCandidate(
                    structure=Structure.A_THREE_ONEWAYS,
                    legs=legs,
                    gateway=eu,
                    total_party_price=_party_total(legs),
                    currency=currency,
                    flags=flags,
                    verification_status=_worst_status(legs),
                )
            )
    return candidates


def _cheapest_per_rt_route(offers: list[FareOffer]) -> dict[tuple[str, str, str, str], FareOffer]:
    """For round-trip offers, key by (origin, destination, outbound, return)."""
    by_route: dict[tuple[str, str, str, str], FareOffer] = {}
    for o in offers:
        if not o.is_round_trip:
            continue
        key = (o.origin, o.destination, o.date, o.return_date or "")
        prev = by_route.get(key)
        if prev is None or o.price_per_pax < prev.price_per_pax:
            by_route[key] = o
    return by_route


def assemble_structure_b(
    outer_rt_offers: list[FareOffer],  # SJO ⇄ DC round-trips
    inner_rt_offers: list[FareOffer],  # DC ⇄ EU round-trips
    blackout_ranges: list[dict[str, str]],
    long_gap_days: int,
    currency: str = "USD",
) -> list[ItineraryCandidate]:
    """Nested envelope, priced as TWO real round-trips:
       outer RT: SJO ⇄ DC airport (Sept outbound, Dec return)
       inner RT: DC airport ⇄ EU gateway (a day or two after outer arrive,
                 a day or two before outer return)

    Both fares are RT totals returned by the source (Google Flights' RT
    pricing), which is the whole point of B — capture the round-trip fare
    advantage that 4 separate one-ways would miss.

    LONG_GAP fires when the inner RT outbound→return gap exceeds long_gap_days
    (round-trip fare advantage erodes for very long stays).
    """
    outer_by_rt = _cheapest_per_rt_route(outer_rt_offers)
    inner_by_rt = _cheapest_per_rt_route(inner_rt_offers)

    candidates: list[ItineraryCandidate] = []
    dc_airports_outer = sorted({k[1] for k in outer_by_rt})

    for dc in dc_airports_outer:
        outer_candidates = [v for k, v in outer_by_rt.items() if k[1] == dc]
        if not outer_candidates:
            continue
        best_outer = min(outer_candidates, key=lambda o: o.price_per_pax)
        outer_out_d = parse_date(best_outer.date)
        outer_ret_d = parse_date(best_outer.return_date or best_outer.date)

        eu_gateways = sorted({k[1] for k in inner_by_rt if k[0] == dc})
        for eu in eu_gateways:
            inner_candidates = [
                v for k, v in inner_by_rt.items()
                if k[0] == dc and k[1] == eu
                and outer_out_d < parse_date(v.date)
                and parse_date(v.return_date or v.date) < outer_ret_d
                and parse_date(v.return_date or v.date) > parse_date(v.date)
            ]
            if not inner_candidates:
                continue
            best_inner = min(inner_candidates, key=lambda o: o.price_per_pax)

            legs = [best_outer, best_inner]
            flags: list[str] = []
            # BLACKOUT: check all four involved dates (each RT has 2 dates)
            for leg in legs:
                if is_blackout(leg.date, blackout_ranges):
                    flags.append(Flag.BLACKOUT.value)
                    break
                if leg.return_date and is_blackout(leg.return_date, blackout_ranges):
                    flags.append(Flag.BLACKOUT.value)
                    break
            inner_gap = (parse_date(best_inner.return_date or best_inner.date) - parse_date(best_inner.date)).days
            if inner_gap > long_gap_days:
                flags.append(Flag.LONG_GAP.value)

            candidates.append(
                ItineraryCandidate(
                    structure=Structure.B_NESTED_ENVELOPE,
                    legs=legs,
                    gateway=eu,
                    total_party_price=_party_total(legs),
                    currency=currency,
                    flags=flags,
                    verification_status=_worst_status(legs),
                )
            )
    return candidates


def assemble_stopover_variant_a(
    leg1a_offers: list[FareOffer],  # SJO → stopover
    leg1b_offers: list[FareOffer],  # stopover → EU gateway
    leg2_offers: list[FareOffer],   # EU gateway → DC
    leg3_offers: list[FareOffer],   # DC → SJO
    stopover_city: str,
    blackout_ranges: list[dict[str, str]],
    currency: str = "USD",
) -> list[ItineraryCandidate]:
    """Constructed-stopover variant of Structure A — 4 legs total.

    `landed-cost-model` will add the stopover lodging assumption because the
    last leg's `raw.stopover_city` flag triggers `FrictionAttributes.has_stopover`.
    """
    l1a = _cheapest_per_route(leg1a_offers)
    l1b = _cheapest_per_route(leg1b_offers)
    l2 = _cheapest_per_route(leg2_offers)
    l3 = _cheapest_per_route(leg3_offers)

    candidates: list[ItineraryCandidate] = []
    eu_gateways = sorted({k[1] for k in l1b})
    dc_airports = sorted({k[1] for k in l2})

    # Cheapest SJO → stopover (date-agnostic for simplicity in v1).
    l1a_options = [v for v in l1a.values() if v.destination == stopover_city]
    if not l1a_options:
        return []
    best_l1a = min(l1a_options, key=lambda o: o.price_per_pax)

    for eu in eu_gateways:
        l1b_options = [v for k, v in l1b.items() if k[0] == stopover_city and k[1] == eu]
        if not l1b_options:
            continue
        best_l1b = min(l1b_options, key=lambda o: o.price_per_pax)
        for dc in dc_airports:
            l2_options = [v for k, v in l2.items() if k[0] == eu and k[1] == dc]
            l3_options = [v for k, v in l3.items() if k[0] == dc]
            if not l2_options or not l3_options:
                continue
            best_l2 = min(l2_options, key=lambda o: o.price_per_pax)
            best_l3 = min(l3_options, key=lambda o: o.price_per_pax)

            # Mark every leg's raw with the stopover_city so the friction
            # extractor flags this itinerary as having_stopover.
            legs = []
            for o in [best_l1a, best_l1b, best_l2, best_l3]:
                raw = dict(o.raw or {})
                raw["stopover_city"] = stopover_city
                legs.append(FareOffer(
                    origin=o.origin, destination=o.destination, date=o.date,
                    return_date=o.return_date, carrier=o.carrier,
                    price_per_pax=o.price_per_pax, currency=o.currency,
                    stops=o.stops, duration_minutes=o.duration_minutes,
                    source=o.source, verification_status=o.verification_status,
                    passengers_queried=o.passengers_queried, raw=raw,
                ))

            flags = []
            for leg in legs:
                if is_blackout(leg.date, blackout_ranges):
                    flags.append(Flag.BLACKOUT.value)
                    break

            candidates.append(ItineraryCandidate(
                structure=Structure.A_THREE_ONEWAYS,
                legs=legs, gateway=eu,
                total_party_price=_party_total(legs),
                currency=currency, flags=flags,
                verification_status=_worst_status(legs),
            ))
    return candidates


def attach_train_metadata(c: ItineraryCandidate) -> dict | None:
    return venice_metadata(c.gateway) if c.gateway else None


def mark_incomplete_structures(
    candidates: list[ItineraryCandidate],
) -> list[ItineraryCandidate]:
    """Tag every candidate of a structure with no VALIDATED member as INCOMPLETE.

    The spec calls a structure "complete" when at least one of its candidates
    reaches VALIDATED. Anything else (only LEAD, only VALIDATION_FAILED, mixed
    LEAD/FAILED, etc.) is "incomplete" and gets flagged so the UI can show
    "incomplete — cannot compare" rather than silently dropping the structure.
    """
    has_validated: dict[Structure, bool] = {}
    for cand in candidates:
        if cand.verification_status == VerificationStatus.VALIDATED:
            has_validated[cand.structure] = True
        else:
            has_validated.setdefault(cand.structure, False)

    flag = Flag.INCOMPLETE.value
    for cand in candidates:
        if not has_validated.get(cand.structure, False):
            if flag not in cand.flags:
                cand.flags.append(flag)
    return candidates


def structure_completeness(
    candidates: list[ItineraryCandidate],
    structures_requested: list[str],
) -> dict[str, str]:
    """Return per-structure completeness: 'complete' / 'incomplete' / 'absent'.

    `cand.structure` is normally the `Structure` enum, but when candidates are
    re-hydrated from persisted Itinerary rows it's a plain string. Coerce.
    """
    by_struct: dict[str, list[ItineraryCandidate]] = {}
    for cand in candidates:
        key = cand.structure.value if hasattr(cand.structure, "value") else str(cand.structure)
        by_struct.setdefault(key, []).append(cand)

    result: dict[str, str] = {}
    for s in ["A", "B"]:
        if s not in structures_requested:
            result[s] = "absent"
            continue
        group = by_struct.get(s, [])
        if not group:
            result[s] = "incomplete"
            continue
        if any(c.verification_status == VerificationStatus.VALIDATED for c in group):
            result[s] = "complete"
        else:
            result[s] = "incomplete"
    return result


__all__ = [
    "ItineraryCandidate",
    "assemble_structure_a",
    "assemble_structure_b",
    "assemble_stopover_variant_a",
    "attach_train_metadata",
    "mark_incomplete_structures",
    "structure_completeness",
]
