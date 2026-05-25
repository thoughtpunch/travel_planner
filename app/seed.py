"""Seed the engagement config (tasks.md §8).

SJO origin; gateways {VCE,MXP,LIN,ZRH,MUC,BLQ}; Leg2 {VCE,MXP,BLQ,FCO}→{IAD,DCA,BWI};
Leg3 {IAD,DCA,BWI}→SJO; 6 adults; $6000 ceiling; Thanksgiving blackout; price A and B.

Two configs are seeded:
- A: three one-way legs (SJO→EU, EU→DC, DC→SJO).
- B: two round-trip legs (SJO ⇄ DC outer, DC ⇄ EU inner), so the source
  returns the round-trip total — the whole point of B is capturing the RT
  fare advantage that 4 separate one-ways would miss.

For Phase 1 each structure is its own config so the leg semantics are
unambiguous per run.
"""

from __future__ import annotations

from sqlalchemy import select

from .db import get_session
from .models import Config, Leg
from .orchestrator.blackout import thanksgiving_weekend
from .preferences import (
    Axis,
    AxisSetting,
    CostAssumptions,
    Preferences,
    ScalePosition,
)

EU_GATEWAYS = ["VCE", "MXP", "LIN", "ZRH", "MUC", "BLQ"]
EU_DEPARTURE_AIRPORTS = ["VCE", "MXP", "BLQ", "FCO"]
DC_AIRPORTS = ["IAD", "DCA", "BWI"]


def seed_config_a(session) -> int:
    name = "Engagement — Structure A (3 one-ways)"
    existing = session.scalars(select(Config).where(Config.name == name)).first()
    if existing:
        return existing.id
    cfg = Config(
        name=name,
        budget_party_total=6000,
        currency="USD",
        passengers={"adults": 6, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        structures=["A"],
        blackout_ranges=[thanksgiving_weekend(2026)],
        validation_tolerance_pct=15,
        validation_top_n=5,
        envelope_long_gap_days=30,
    )
    session.add(cfg)
    session.commit()
    session.refresh(cfg)
    session.add_all([
        Leg(config_id=cfg.id, ordinal=1, origins=["SJO"], destinations=EU_GATEWAYS,
            date_anchor="2026-09-10", window_days=7, sampling_strategy="anchor,+/-3,+/-7"),
        Leg(config_id=cfg.id, ordinal=2, origins=EU_DEPARTURE_AIRPORTS, destinations=DC_AIRPORTS,
            date_anchor="2026-11-10", window_days=7, sampling_strategy="anchor,+/-3,+/-7"),
        Leg(config_id=cfg.id, ordinal=3, origins=DC_AIRPORTS, destinations=["SJO"],
            date_anchor="2026-12-20", window_days=7, sampling_strategy="anchor,+/-3,+/-7"),
    ])
    session.commit()
    return cfg.id


def seed_config_b(session) -> int:
    name = "Engagement — Structure B (nested envelope)"
    existing = session.scalars(select(Config).where(Config.name == name)).first()
    if existing:
        return existing.id
    cfg = Config(
        name=name,
        budget_party_total=6000,
        currency="USD",
        passengers={"adults": 6, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        structures=["B"],
        blackout_ranges=[thanksgiving_weekend(2026)],
        validation_tolerance_pct=15,
        validation_top_n=5,
        envelope_long_gap_days=30,
    )
    session.add(cfg)
    session.commit()
    session.refresh(cfg)
    # Tight defaults: anchor-only on both sides for each RT (1 outbound × 1
    # return per origin/dest pair). Keeps the worst-case SerpAPI burn small
    # if the scraper falls back. Bump windows/sampling in the UI to broaden.
    session.add_all([
        # Outer RT: SJO ⇄ DC (Sept outbound, Dec return)
        Leg(
            config_id=cfg.id, ordinal=1,
            origins=["SJO"], destinations=DC_AIRPORTS,
            date_anchor="2026-09-05", window_days=5, sampling_strategy="anchor",
            return_date_anchor="2026-12-20", return_window_days=5,
            return_sampling_strategy="anchor",
        ),
        # Inner RT: DC ⇄ EU (a day or two after outer arrival → a day or two
        # before outer return). Sampled tight; cross-product grows fast.
        Leg(
            config_id=cfg.id, ordinal=2,
            origins=DC_AIRPORTS, destinations=EU_GATEWAYS,
            date_anchor="2026-09-07", window_days=5, sampling_strategy="anchor",
            return_date_anchor="2026-12-17", return_window_days=5,
            return_sampling_strategy="anchor",
        ),
    ])
    session.commit()
    return cfg.id


def seed_venice_family() -> int:
    """Seed the 'Venice family of 6' canonical engagement config — Structure A
    legs (SJO → EU gateway → DC → SJO) plus the default preference + cost
    assumption set the operator typically starts with: avoid long layovers,
    avoid red-eye, neutral on stopover, $320/night × 2 rooms for any
    forced/intentional overnight.

    This is the config the `landed-cost-model` cheaper-fare-loses scenario
    is demonstrated against in the e2e verification (task 9.2).
    """
    from .enums import Structure

    name = "Venice family of 6 — landed cost"
    with get_session() as session:
        existing = session.scalars(select(Config).where(Config.name == name)).first()
        if existing:
            return existing.id
        preferences = Preferences(
            defaults={
                Axis.LAYOVER_LENGTH: AxisSetting(position=ScalePosition.AVOID, threshold=180),
                Axis.RED_EYE: AxisSetting(position=ScalePosition.AVOID),
                Axis.STOPOVER: AxisSetting(position=ScalePosition.NEUTRAL),
                Axis.PLANE_CHANGES: AxisSetting(position=ScalePosition.NEUTRAL),
                Axis.TRANSFER_LENGTH: AxisSetting(position=ScalePosition.NEUTRAL),
            },
        )
        assumptions = CostAssumptions(stopover_lodging_per_night=320, stopover_rooms=2)
        cfg = Config(
            name=name,
            budget_party_total=8000,
            currency="USD",
            passengers={"adults": 6, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
            structures=[Structure.A_THREE_ONEWAYS.value],
            blackout_ranges=[thanksgiving_weekend(2026)],
            validation_tolerance_pct=15,
            validation_top_n=5,
            envelope_long_gap_days=30,
            preferences=preferences.model_dump(mode="json"),
            cost_assumptions=assumptions.model_dump(mode="json"),
        )
        session.add(cfg)
        session.commit()
        session.refresh(cfg)
        session.add_all([
            Leg(config_id=cfg.id, ordinal=1, origins=["SJO"], destinations=EU_GATEWAYS,
                date_anchor="2026-09-10", window_days=7, sampling_strategy="anchor,+/-3,+/-7"),
            Leg(config_id=cfg.id, ordinal=2, origins=EU_DEPARTURE_AIRPORTS, destinations=DC_AIRPORTS,
                date_anchor="2026-11-10", window_days=7, sampling_strategy="anchor,+/-3,+/-7"),
            Leg(config_id=cfg.id, ordinal=3, origins=DC_AIRPORTS, destinations=["SJO"],
                date_anchor="2026-12-20", window_days=7, sampling_strategy="anchor,+/-3,+/-7"),
        ])
        session.commit()
        return cfg.id


def seed_all() -> dict[str, int]:
    with get_session() as session:
        a_id = seed_config_a(session)
        b_id = seed_config_b(session)
    venice_id = seed_venice_family()
    return {"A": a_id, "B": b_id, "Venice": venice_id}
