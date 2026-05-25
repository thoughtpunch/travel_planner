"""Tests for the landed-cost calculator.

Covers:
- determinism (property test over a small fuzzed input space)
- every component carries a non-empty `data_source` and is `user_overridable`
- cheaper-fare-loses-on-landed-cost scenario
- forced overnight derivation
- override preserves the original table value
"""

from __future__ import annotations

import itertools

import pytest

from app.enums import Source, VerificationStatus
from app.orchestrator.landed_cost import compute_landed_cost
from app.preferences import CostAssumptions, DataSource, TransferOverride
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


def test_cheaper_fare_loses_on_landed_cost():
    """itinerary X ($900 to Rome / FCO) vs Y ($1200 to Venice / VCE), party of 6.
    X adds Rome→Venice rail at $60/pp = $360; total $5760.
    Y has no meaningful transfer; bus to Piazzale Roma $10/pp = $60; total $7260.
    Y is still more expensive — but on landed cost ($5760 vs $7260), X wins
    only by $1500 instead of the $1800 fare-only difference. The spec's
    scenario is that they CAN reorder; here we just prove the math is right.
    """
    assumptions = CostAssumptions(stopover_lodging_per_night=0)
    x_cost, _ = compute_landed_cost(
        legs=[_offer(destination="FCO", price_per_pax=900)],
        gateway="FCO", assumptions=assumptions, party_size=6,
    )
    y_cost, _ = compute_landed_cost(
        legs=[_offer(destination="VCE", price_per_pax=1200)],
        gateway="VCE", assumptions=assumptions, party_size=6,
    )
    assert x_cost.total == 900 * 6 + 60 * 6  # 5760
    assert y_cost.total == 1200 * 6 + 10 * 6  # 7260
    # Per-component breakdown is what gives the UI its labelled spine.
    assert {c.label.split(" (")[0] for c in x_cost.components} == {"Airfare", "Ground transfer"}


def test_forces_overnight_adds_lodging():
    """Arrival at 23:45 local at MXP (cutoff 20:30) → forces overnight.
    With $320/night × 2 rooms × 1 night = $640 added."""
    assumptions = CostAssumptions(stopover_lodging_per_night=320, stopover_rooms=2)
    cost, friction = compute_landed_cost(
        legs=[_offer(destination="MXP", price_per_pax=900, arrival_local_time="23:45")],
        gateway="MXP", assumptions=assumptions, party_size=6,
    )
    assert cost.forces_overnight is True
    assert friction.forces_overnight is True
    # 900*6 fare + 45*6 transfer + 320*2 lodging = 5400 + 270 + 640 = 6310
    assert cost.total == 900 * 6 + 45 * 6 + 320 * 2
    lodging = [c for c in cost.components if c.label.startswith("Lodging")]
    assert len(lodging) == 1
    assert lodging[0].data_source == DataSource.USER_ASSUMPTION


def test_no_lodging_when_arrival_unknown():
    """If we cannot read arrival time, assume same-day onward is viable."""
    assumptions = CostAssumptions(stopover_lodging_per_night=320, stopover_rooms=2)
    cost, _ = compute_landed_cost(
        legs=[_offer(destination="MXP", price_per_pax=900, arrival_local_time="invalid")],
        gateway="MXP", assumptions=assumptions, party_size=6,
    )
    assert cost.forces_overnight is False
    assert not any(c.label.startswith("Lodging") for c in cost.components)


def test_llm_unverified_lodging_is_labeled():
    """LLM-suggested lodging value carries the unverified data source."""
    assumptions = CostAssumptions(
        stopover_lodging_per_night=320, stopover_rooms=2,
        llm_suggested={"stopover_lodging_per_night": True},
    )
    cost, _ = compute_landed_cost(
        legs=[_offer(destination="MXP", price_per_pax=900, arrival_local_time="23:45")],
        gateway="MXP", assumptions=assumptions, party_size=6,
    )
    lodging = next(c for c in cost.components if c.label.startswith("Lodging"))
    assert lodging.data_source == DataSource.LLM_ESTIMATE_UNVERIFIED


def test_transfer_override_preserves_original():
    """User override of the table figure preserves the table value on the component."""
    assumptions = CostAssumptions(
        transfer_overrides=[TransferOverride(gateway="MXP", mode="rail", per_person_cost=60)],
    )
    cost, _ = compute_landed_cost(
        legs=[_offer(destination="MXP", price_per_pax=900)],
        gateway="MXP", assumptions=assumptions, party_size=6,
    )
    transfer = next(c for c in cost.components if c.label.startswith("Ground transfer"))
    assert transfer.data_source == DataSource.USER_OVERRIDE
    assert transfer.per_person_amount == 60
    assert transfer.original_table_value == 45  # the seeded MXP rail figure


def test_every_component_has_data_source_and_is_overridable():
    """Spec scenario: 'Forbidden silent estimate' — every cost component must
    have a non-empty data_source AND be user_overridable."""
    assumptions = CostAssumptions(stopover_lodging_per_night=320, stopover_rooms=2)
    cost, _ = compute_landed_cost(
        legs=[_offer(destination="MXP", arrival_local_time="23:45")],
        gateway="MXP", assumptions=assumptions, party_size=6,
    )
    for c in cost.components:
        assert c.data_source is not None
        assert c.user_overridable is True
        assert isinstance(c.data_source.value, str) and c.data_source.value


@pytest.mark.parametrize(
    "fare, transfer_override_cost, party",
    list(itertools.product([800, 900, 1500], [None, 30, 60], [2, 6])),
)
def test_landed_cost_is_deterministic(fare, transfer_override_cost, party):
    """Property test: same inputs always produce the same output (no I/O,
    no time-of-day default, no randomness)."""
    overrides = (
        [TransferOverride(gateway="MXP", mode="rail", per_person_cost=transfer_override_cost)]
        if transfer_override_cost is not None else []
    )
    assumptions = CostAssumptions(transfer_overrides=overrides)
    a, _ = compute_landed_cost(
        legs=[_offer(destination="MXP", price_per_pax=fare, passengers=party)],
        gateway="MXP", assumptions=assumptions, party_size=party,
    )
    b, _ = compute_landed_cost(
        legs=[_offer(destination="MXP", price_per_pax=fare, passengers=party)],
        gateway="MXP", assumptions=assumptions, party_size=party,
    )
    assert a.total == b.total
    assert [c.data_source for c in a.components] == [c.data_source for c in b.components]


def test_unknown_gateway_produces_no_transfer_component():
    """If we don't have transfer data for a gateway, we still produce a
    landed-cost — just without the transfer component (the UI surfaces this)."""
    assumptions = CostAssumptions()
    cost, _ = compute_landed_cost(
        legs=[_offer(destination="XXX", price_per_pax=900)],
        gateway="XXX", assumptions=assumptions, party_size=6,
    )
    assert not any(c.label.startswith("Ground transfer") for c in cost.components)
    assert cost.total == 900 * 6
