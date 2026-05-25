"""Hardcoded gateway → Venice transfer table.

Per `landed-cost-model` Decision 5 (and the design): rail/ferry fares between
European gateways and Venice are stable enough that scraping them is the
wrong tradeoff. A maintained table with `last_reviewed` dates is accurate
and reviewable.

`forces_overnight` is NOT pre-baked here — it is derived per itinerary
from the actual arrival local time vs. the gateway's
`last_viable_onward_local_time`.

Maintainer commitment: quarterly review (see docs/gateway-transfers.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Literal

TransferMode = Literal["rail", "ferry", "bus", "drive"]


@dataclass(frozen=True)
class TransferModel:
    gateway: str  # IATA
    mode: TransferMode
    per_person_cost: int  # whole currency units, USD
    duration_minutes: int
    transfers: int  # train-to-train changes; 0 = direct
    last_viable_onward_local_time: time  # after this local arrival time, no same-day onward
    last_reviewed: date
    currency: str = "USD"
    notes: str = ""
    # When set, the airfare must arrive at one of these IATA codes for this
    # transfer to apply. Lets us model "MXP arrivals use this train" vs.
    # "LIN arrivals use that train" cleanly when both serve the same metro.
    arrival_airports: tuple[str, ...] = field(default_factory=tuple)


# Whole-currency USD. EUR figures rough-converted at 1.0 to keep the spine in
# one currency; user can override per-config via cost_assumptions.transfer_overrides.
GATEWAY_TRANSFERS: dict[str, list[TransferModel]] = {
    "VCE": [
        TransferModel(
            gateway="VCE", mode="bus", per_person_cost=10, duration_minutes=20, transfers=0,
            last_viable_onward_local_time=time(23, 30), last_reviewed=date(2026, 4, 12),
            notes="Marco Polo → Piazzale Roma — ATVO/ACTV airport bus, every 30 min.",
        ),
    ],
    "MXP": [
        TransferModel(
            gateway="MXP", mode="rail", per_person_cost=45, duration_minutes=260, transfers=1,
            last_viable_onward_local_time=time(20, 30), last_reviewed=date(2026, 4, 12),
            notes="Malpensa Express → MIL Centrale → Frecciarossa to VEZ Santa Lucia.",
        ),
    ],
    "LIN": [
        TransferModel(
            gateway="LIN", mode="rail", per_person_cost=45, duration_minutes=240, transfers=1,
            last_viable_onward_local_time=time(21, 0), last_reviewed=date(2026, 4, 12),
            notes="Linate bus to MIL Centrale → Frecciarossa to VEZ Santa Lucia.",
        ),
    ],
    "BLQ": [
        TransferModel(
            gateway="BLQ", mode="rail", per_person_cost=30, duration_minutes=130, transfers=1,
            last_viable_onward_local_time=time(22, 30), last_reviewed=date(2026, 4, 12),
            notes="Marconi Express to BO Centrale → direct regional/IC to VEZ Santa Lucia.",
        ),
    ],
    "VRN": [
        TransferModel(
            gateway="VRN", mode="rail", per_person_cost=18, duration_minutes=80, transfers=1,
            last_viable_onward_local_time=time(22, 30), last_reviewed=date(2026, 4, 12),
            notes="ATV bus to Verona Porta Nuova → regional to VEZ Santa Lucia (frequent).",
        ),
    ],
    "TRS": [
        TransferModel(
            gateway="TRS", mode="rail", per_person_cost=22, duration_minutes=150, transfers=1,
            last_viable_onward_local_time=time(21, 0), last_reviewed=date(2026, 4, 12),
            notes="APT bus to Trieste Centrale → regional/IC to VEZ Santa Lucia.",
        ),
        TransferModel(
            gateway="TRS", mode="ferry", per_person_cost=35, duration_minutes=210, transfers=0,
            last_viable_onward_local_time=time(15, 0), last_reviewed=date(2026, 4, 12),
            notes="Seasonal Trieste ↔ Venice ferry (Trieste Lines); summer only — verify dates.",
        ),
    ],
    "ZRH": [
        TransferModel(
            gateway="ZRH", mode="rail", per_person_cost=90, duration_minutes=420, transfers=1,
            last_viable_onward_local_time=time(18, 0), last_reviewed=date(2026, 4, 12),
            notes="EuroCity to MIL Centrale → Frecciarossa to VEZ Santa Lucia. 7h door-to-door.",
        ),
    ],
    "MUC": [
        TransferModel(
            gateway="MUC", mode="rail", per_person_cost=100, duration_minutes=430, transfers=1,
            last_viable_onward_local_time=time(17, 30), last_reviewed=date(2026, 4, 12),
            notes="EuroCity via Verona to VEZ Santa Lucia. 7h door-to-door.",
        ),
    ],
    "FCO": [
        TransferModel(
            gateway="FCO", mode="rail", per_person_cost=60, duration_minutes=240, transfers=1,
            last_viable_onward_local_time=time(20, 0), last_reviewed=date(2026, 4, 12),
            notes="Leonardo Express to ROM Termini → Frecciarossa to VEZ Santa Lucia.",
        ),
    ],
}


def get_transfers(gateway: str) -> list[TransferModel]:
    """Return all available transfer modes for a gateway; empty list if unknown."""
    return list(GATEWAY_TRANSFERS.get(gateway, []))


def snapshot_table() -> dict[str, list[dict]]:
    """Run-snapshot view of the table — every entry serialised with its
    `last_reviewed` date so historical runs remain interpretable."""
    out: dict[str, list[dict]] = {}
    for gateway, entries in GATEWAY_TRANSFERS.items():
        out[gateway] = [
            {
                "mode": e.mode,
                "per_person_cost": e.per_person_cost,
                "currency": e.currency,
                "duration_minutes": e.duration_minutes,
                "transfers": e.transfers,
                "last_viable_onward_local_time": e.last_viable_onward_local_time.isoformat(),
                "last_reviewed": e.last_reviewed.isoformat(),
                "notes": e.notes,
            }
            for e in entries
        ]
    return out


__all__ = ["GATEWAY_TRANSFERS", "TransferModel", "TransferMode", "get_transfers", "snapshot_table"]
