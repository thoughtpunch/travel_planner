"""Tests for the preference scorer.

Covers the load-bearing invariants of `preference-scoring`:
- HARD NO filters; counts are recorded per axis.
- HARD YES does NOT filter the base set (only construction triggers it).
- Soft scoring reorders WITHIN the ±soft_band_pct cost band.
- A 15% above-cheapest itinerary cannot be promoted above the cheapest by
  any stack of soft-desire boosts (soft-band bound).
- The function never mutates landed_cost / cost_breakdown.
"""

from __future__ import annotations

import pytest

from app.enums import Source, Structure, VerificationStatus
from app.orchestrator.landed_cost import compute_landed_cost
from app.orchestrator.preferences import apply_preferences
from app.orchestrator.structures import ItineraryCandidate
from app.preferences import (
    Axis,
    AxisSetting,
    CostAssumptions,
    Preferences,
    ScalePosition,
)
from app.sources.base import FareOffer


def _offer(
    *, origin="SJO", destination="MXP", date="2026-09-10",
    price_per_pax=900, passengers=6, status=VerificationStatus.VALIDATED,
    arrival_local_time="14:30", stops=0, raw_extra=None,
) -> FareOffer:
    raw = {"arrival_local_time": arrival_local_time}
    if raw_extra:
        raw.update(raw_extra)
    return FareOffer(
        origin=origin, destination=destination, date=date,
        carrier="LH", price_per_pax=price_per_pax, currency="USD",
        stops=stops, duration_minutes=600,
        source=Source.FLI, verification_status=status,
        passengers_queried=passengers, raw=raw,
    )


def _candidate(
    *, gateway="MXP", price=900, status=VerificationStatus.VALIDATED,
    arrival="14:30", stops=0, raw_extra=None, party=6,
) -> ItineraryCandidate:
    legs = [_offer(destination=gateway, price_per_pax=price, status=status,
                   arrival_local_time=arrival, stops=stops, raw_extra=raw_extra,
                   passengers=party)]
    assumptions = CostAssumptions(stopover_lodging_per_night=320, stopover_rooms=2)
    cost, friction = compute_landed_cost(
        legs=legs, gateway=gateway, assumptions=assumptions, party_size=party,
    )
    cand = ItineraryCandidate(
        structure=Structure.A_THREE_ONEWAYS, legs=legs, gateway=gateway,
        total_party_price=price * party, currency="USD",
        verification_status=status,
        landed_cost=cost.total, cost_breakdown=cost, friction_attributes=friction,
    )
    return cand


def test_hard_no_layover_filters_and_counts():
    layovers = [{"duration_minutes": 300}]  # 5h layover
    raw_extra = {"layovers": layovers}
    a = _candidate(gateway="MXP", price=900, raw_extra=raw_extra)
    b = _candidate(gateway="VCE", price=950)  # no layovers
    prefs = Preferences(defaults={
        Axis.LAYOVER_LENGTH: AxisSetting(position=ScalePosition.HARD_NO, threshold=240),  # 4h cap
    })
    result = apply_preferences([a, b], prefs, cheapest_validated_landed_cost=b.landed_cost)
    assert len(result.ranked) == 1
    assert result.ranked[0] is b
    assert result.filtered_out.get(Axis.LAYOVER_LENGTH) == 1


def test_hard_no_red_eye_filters():
    a = _candidate(gateway="MXP", price=900, arrival="04:15")  # red-eye arrival
    b = _candidate(gateway="VCE", price=950, arrival="14:30")
    prefs = Preferences(defaults={Axis.RED_EYE: AxisSetting(position=ScalePosition.HARD_NO)})
    result = apply_preferences([a, b], prefs, cheapest_validated_landed_cost=b.landed_cost)
    assert len(result.ranked) == 1
    assert result.ranked[0] is b
    assert result.filtered_out.get(Axis.RED_EYE) == 1


def test_soft_avoid_red_eye_reorders_within_band():
    """Cheaper red-eye should rank BELOW slightly-more-expensive non-red-eye
    when the more-expensive one is inside the ±10% soft band."""
    cheap_redeye = _candidate(gateway="VCE", price=900, arrival="04:15")  # 5460 landed
    pricier_normal = _candidate(gateway="VCE", price=940, arrival="14:30")  # 5700 landed
    # Both within ±10% of 5460 → 6006 → both inside band.
    prefs = Preferences(defaults={Axis.RED_EYE: AxisSetting(position=ScalePosition.STRONGLY_AVOID)})
    result = apply_preferences(
        [cheap_redeye, pricier_normal], prefs,
        cheapest_validated_landed_cost=cheap_redeye.landed_cost,
    )
    # Without soft scoring, cheap_redeye would win (cheaper). With strongly_avoid red-eye,
    # the soft delta tiebreaks ABOVE the cost-only sort if costs are close.
    # We expect pricier_normal to rank first.
    assert result.ranked[0] is pricier_normal
    assert any(e.axis == Axis.RED_EYE and e.direction == "avoid_match" for e in cheap_redeye.preference_explanations)


def test_soft_desire_cannot_promote_above_outside_band():
    """An itinerary 15% above the cheapest cannot beat the cheapest, no matter
    how many soft-desire boosts it stacks. The soft band is the safety bound."""
    cheap = _candidate(gateway="VCE", price=900)  # 5460 landed
    # 15% above 5460 = 6279. We give it a stopover (has_stopover requires a
    # raw stopover_city marker on the last leg).
    pricier = _candidate(
        gateway="VCE", price=1050,  # 1050*6 + 10*6 = 6360 (>15% above 5460)
        raw_extra={"stopover_city": "MAD"},
    )
    # Multiple strongly_desire on axes that match pricier.
    prefs = Preferences(defaults={
        Axis.STOPOVER: AxisSetting(position=ScalePosition.STRONGLY_DESIRE),
    }, soft_band_pct=10)
    result = apply_preferences(
        [cheap, pricier], prefs, cheapest_validated_landed_cost=cheap.landed_cost,
    )
    # pricier is outside the band → must rank below cheap on landed cost alone.
    assert result.ranked[0] is cheap
    assert result.ranked[1] is pricier


def test_no_double_count_for_hard_yes_stopover():
    """A HARD-YES stopover itinerary's landed cost is the same whether
    preferences mention stopover or not. Only its rank moves."""
    stopover_legs = [_offer(destination="VCE", price_per_pax=900,
                            raw_extra={"stopover_city": "MAD"})]
    assumptions = CostAssumptions(stopover_lodging_per_night=320, stopover_rooms=2)
    cost_neutral_prefs_input = compute_landed_cost(
        legs=stopover_legs, gateway="VCE", assumptions=assumptions, party_size=6,
    )[0]
    # Build candidate fresh for each prefs setting so mutation can't leak.
    def fresh():
        cost, friction = compute_landed_cost(
            legs=stopover_legs, gateway="VCE", assumptions=assumptions, party_size=6,
        )
        return ItineraryCandidate(
            structure=Structure.A_THREE_ONEWAYS, legs=stopover_legs, gateway="VCE",
            total_party_price=900 * 6, currency="USD",
            verification_status=VerificationStatus.VALIDATED,
            landed_cost=cost.total, cost_breakdown=cost, friction_attributes=friction,
        )

    neutral = Preferences(defaults={
        Axis.STOPOVER: AxisSetting(position=ScalePosition.NEUTRAL),
    })
    desired = Preferences(defaults={
        Axis.STOPOVER: AxisSetting(position=ScalePosition.STRONGLY_DESIRE),
    })

    cand_neutral = fresh()
    cand_desired = fresh()
    apply_preferences([cand_neutral], neutral, cheapest_validated_landed_cost=cand_neutral.landed_cost)
    apply_preferences([cand_desired], desired, cheapest_validated_landed_cost=cand_desired.landed_cost)
    # Landed cost is unchanged.
    assert cand_neutral.landed_cost == cand_desired.landed_cost == cost_neutral_prefs_input.total


def test_failed_candidates_skip_filtering():
    """FAILED candidates pass through HARD NO filters so the audit trail
    keeps them visible."""
    failed = _candidate(gateway="MXP", price=0, status=VerificationStatus.FAILED, arrival="04:15")
    ok = _candidate(gateway="VCE", price=900, arrival="14:30")
    prefs = Preferences(defaults={Axis.RED_EYE: AxisSetting(position=ScalePosition.HARD_NO)})
    result = apply_preferences([failed, ok], prefs, cheapest_validated_landed_cost=ok.landed_cost)
    assert failed in result.ranked
    assert ok in result.ranked


def test_function_never_mutates_cost_spine():
    """Pre/post fingerprint check is inside apply_preferences; this test
    asserts at the user level: landed_cost and cost_breakdown unchanged."""
    a = _candidate(gateway="VCE", price=900)
    pre_total = a.landed_cost
    pre_breakdown_total = a.cost_breakdown.total
    prefs = Preferences(defaults={
        Axis.RED_EYE: AxisSetting(position=ScalePosition.STRONGLY_AVOID),
        Axis.STOPOVER: AxisSetting(position=ScalePosition.STRONGLY_DESIRE),
    })
    apply_preferences([a], prefs, cheapest_validated_landed_cost=a.landed_cost)
    assert a.landed_cost == pre_total
    assert a.cost_breakdown.total == pre_breakdown_total


def test_preferences_validator_rejects_hard_yes_on_disallowed_axis():
    """The Preferences model rejects HARD YES on non-admitted axes at
    validation time, so the runner never sees an incoherent set."""
    with pytest.raises(ValueError, match="HARD YES is not meaningful"):
        Preferences(defaults={
            Axis.LAYOVER_LENGTH: AxisSetting(position=ScalePosition.HARD_YES),
        })


def test_preferences_validator_requires_stopover_target_for_hard_yes():
    with pytest.raises(ValueError, match="HARD YES on stopover requires stopover_target"):
        Preferences(defaults={
            Axis.STOPOVER: AxisSetting(position=ScalePosition.HARD_YES),
        })
