from __future__ import annotations

from app.enums import Flag, Source, Structure, VerificationStatus
from app.orchestrator.blackout import is_blackout, thanksgiving_weekend
from app.orchestrator.dates import sample_dates
from app.orchestrator.matrix import LegSpec, expand_leg
from app.orchestrator.ranker import budget_verdict, rank_candidates
from app.orchestrator.structures import (
    ItineraryCandidate,
    assemble_structure_a,
    assemble_structure_b,
    mark_incomplete_structures,
    structure_completeness,
)
from app.sources.base import FareOffer


def _offer(o, d, date, price, status=VerificationStatus.LEAD, pax=6, return_date=None):
    return FareOffer(
        origin=o, destination=d, date=date, return_date=return_date, carrier="LH",
        price_per_pax=price, currency="USD", stops=0, duration_minutes=600,
        source=Source.FAST_FLIGHTS, verification_status=status,
        passengers_queried=pax,
    )


def test_sample_dates_anchor_plus_minus():
    out = sample_dates("2026-09-10", window_days=7, strategy="anchor,+/-3,+/-7")
    assert out == ["2026-09-03", "2026-09-07", "2026-09-10", "2026-09-13", "2026-09-17"]


def test_sample_dates_bounded_by_window():
    out = sample_dates("2026-09-10", window_days=3, strategy="+/-7")
    assert out == []  # ±7 outside ±3 window


def test_thanksgiving_2026_blackout():
    rng = thanksgiving_weekend(2026)
    assert rng["start"] == "2026-11-25"
    assert rng["end"] == "2026-11-29"
    assert is_blackout("2026-11-26", [rng]) is True
    assert is_blackout("2026-11-30", [rng]) is False


def test_expand_leg_cartesian():
    leg = LegSpec(
        ordinal=1, origins=["SJO"], destinations=["VCE", "MXP"],
        date_anchor="2026-09-10", window_days=7, sampling_strategy="anchor,+/-3",
    )
    qs = expand_leg(leg, adults=6)
    # 1 origin × 2 destinations × 3 dates = 6
    assert len(qs) == 6
    assert all(q.adults == 6 for q in qs)


def test_structure_a_picks_cheapest_per_route_and_aggregates_party():
    leg1 = [_offer("SJO", "VCE", "2026-09-10", 700), _offer("SJO", "VCE", "2026-09-13", 650)]
    leg2 = [_offer("VCE", "IAD", "2026-11-10", 500)]
    leg3 = [_offer("IAD", "SJO", "2026-12-20", 400)]
    out = assemble_structure_a(leg1, leg2, leg3, blackout_ranges=[])
    assert len(out) == 1
    c = out[0]
    assert c.structure == Structure.A_THREE_ONEWAYS
    assert c.gateway == "VCE"
    # cheapest leg1 = 650, leg2 = 500, leg3 = 400; party of 6
    assert c.total_party_price == (650 + 500 + 400) * 6


def test_structure_a_blackout_flag():
    leg1 = [_offer("SJO", "VCE", "2026-09-10", 700)]
    leg2 = [_offer("VCE", "IAD", "2026-11-10", 500)]
    leg3 = [_offer("IAD", "SJO", "2026-11-27", 400)]  # Thanksgiving
    rng = [thanksgiving_weekend(2026)]
    out = assemble_structure_a(leg1, leg2, leg3, blackout_ranges=rng)
    assert Flag.BLACKOUT.value in out[0].flags


def test_structure_b_round_trip_pairs_outer_and_inner():
    # Outer RT: SJO ⇄ IAD as one round-trip per pax priced at 700
    outer_rt = [_offer("SJO", "IAD", "2026-09-05", 700, return_date="2026-12-20")]
    # Inner RT: IAD ⇄ VCE, gap = Sept 6 → Dec 15 (> 30 days)
    inner_rt = [_offer("IAD", "VCE", "2026-09-06", 600, return_date="2026-12-15")]
    out = assemble_structure_b(outer_rt, inner_rt, blackout_ranges=[], long_gap_days=30)
    assert len(out) == 1
    cand = out[0]
    assert cand.gateway == "VCE"
    # 2 RT fares × 6 pax = (700 + 600) × 6
    assert cand.total_party_price == (700 + 600) * 6
    assert Flag.LONG_GAP.value in cand.flags


def test_structure_b_requires_inner_inside_outer_envelope():
    outer_rt = [_offer("SJO", "IAD", "2026-09-05", 700, return_date="2026-12-20")]
    # Inner outbound BEFORE outer outbound — must be rejected
    inner_rt_too_early = [_offer("IAD", "VCE", "2026-09-04", 600, return_date="2026-12-15")]
    assert assemble_structure_b(outer_rt, inner_rt_too_early, [], long_gap_days=30) == []


def test_structure_b_blackout_flag_on_rt_return_date():
    outer_rt = [_offer("SJO", "IAD", "2026-09-05", 700, return_date="2026-11-27")]  # Thanksgiving
    inner_rt = [_offer("IAD", "VCE", "2026-09-06", 600, return_date="2026-11-20")]
    out = assemble_structure_b(
        outer_rt, inner_rt,
        blackout_ranges=[thanksgiving_weekend(2026)],
        long_gap_days=200,
    )
    assert Flag.BLACKOUT.value in out[0].flags


def test_round_trip_matrix_expansion_cross_products_dates():
    leg = LegSpec(
        ordinal=1, origins=["SJO"], destinations=["IAD"],
        date_anchor="2026-09-05", window_days=5, sampling_strategy="anchor,+/-3",
        return_date_anchor="2026-12-20", return_window_days=5,
        return_sampling_strategy="anchor,+/-3",
    )
    qs = expand_leg(leg, adults=6)
    # 1 × 1 × (3 outbound × 3 return) = 9 RT queries (returns all > outbound)
    assert len(qs) == 9
    assert all(q.return_date is not None for q in qs)
    assert all(q.return_date > q.date for q in qs)


def test_ranker_validated_beats_cheaper_lead():
    cheap_lead = _offer("SJO", "VCE", "2026-09-10", 500)
    expensive_validated = _offer("SJO", "VCE", "2026-09-10", 900, status=VerificationStatus.VALIDATED)
    from app.orchestrator.structures import ItineraryCandidate
    a = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[cheap_lead], gateway="VCE",
        total_party_price=cheap_lead.price_per_pax * 6, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    b = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[expensive_validated], gateway="VCE",
        total_party_price=expensive_validated.price_per_pax * 6, currency="USD",
        verification_status=VerificationStatus.VALIDATED,
    )
    ranked = rank_candidates([a, b])
    assert ranked[0].verification_status == VerificationStatus.VALIDATED


def test_budget_verdict_ignores_leads():
    from app.orchestrator.structures import ItineraryCandidate
    lead = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[], gateway="VCE",
        total_party_price=4000, currency="USD",
        verification_status=VerificationStatus.LEAD,
    )
    verdict = budget_verdict([lead], budget_party_total=6000)
    assert verdict["met"] is False
    assert "no VALIDATED" in verdict["reason"]


def test_budget_verdict_uses_validated():
    from app.orchestrator.structures import ItineraryCandidate
    v = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=[], gateway="VCE",
        total_party_price=5800, currency="USD",
        verification_status=VerificationStatus.VALIDATED,
    )
    verdict = budget_verdict([v], budget_party_total=6000)
    assert verdict["met"] is True
    assert verdict["best_validated_price"] == 5800


def _cand(structure, status, flags=None):
    return ItineraryCandidate(
        structure=structure, legs=[], gateway="VCE",
        total_party_price=5000, currency="USD",
        verification_status=status,
        flags=list(flags) if flags else [],
    )


def test_mark_incomplete_flags_only_unvalidated_structure():
    a_validated = _cand(Structure.A_THREE_ONEWAYS, VerificationStatus.VALIDATED)
    a_lead = _cand(Structure.A_THREE_ONEWAYS, VerificationStatus.LEAD)
    b_lead = _cand(Structure.B_NESTED_ENVELOPE, VerificationStatus.LEAD)
    b_failed = _cand(Structure.B_NESTED_ENVELOPE, VerificationStatus.VALIDATION_FAILED)

    out = mark_incomplete_structures([a_validated, a_lead, b_lead, b_failed])

    assert Flag.INCOMPLETE.value not in a_validated.flags
    assert Flag.INCOMPLETE.value not in a_lead.flags
    assert Flag.INCOMPLETE.value in b_lead.flags
    assert Flag.INCOMPLETE.value in b_failed.flags
    completeness = structure_completeness(out, ["A", "B"])
    assert completeness == {"A": "complete", "B": "incomplete"}


def test_mark_incomplete_noop_when_both_structures_have_validated():
    a = _cand(Structure.A_THREE_ONEWAYS, VerificationStatus.VALIDATED)
    a_lead = _cand(Structure.A_THREE_ONEWAYS, VerificationStatus.LEAD)
    b = _cand(Structure.B_NESTED_ENVELOPE, VerificationStatus.VALIDATED)

    mark_incomplete_structures([a, a_lead, b])

    assert all(Flag.INCOMPLETE.value not in c.flags for c in [a, a_lead, b])
    assert structure_completeness([a, a_lead, b], ["A", "B"]) == {
        "A": "complete", "B": "complete",
    }


def test_structure_completeness_marks_unrequested_as_absent():
    a = _cand(Structure.A_THREE_ONEWAYS, VerificationStatus.VALIDATED)
    assert structure_completeness([a], ["A"]) == {"A": "complete", "B": "absent"}
