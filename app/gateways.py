"""Static gateway → Venice (VCE) train metadata. Hardcoded per design.md.

Source: typical Trenitalia / OBB / SBB routings to Venezia S. Lucia, rough EUR
2nd-class fares booked ~2 weeks ahead. Not booked by this system — decision
context only for door-to-door ranking.
"""

GATEWAY_TO_VENICE: dict[str, dict] = {
    "VCE": {"train_minutes": 0, "train_eur_per_pax": 0, "note": "Venice Marco Polo — direct"},
    "MXP": {"train_minutes": 260, "train_eur_per_pax": 45, "note": "Milan MXP → Venezia S. Lucia (Frecciarossa via MIL)"},
    "LIN": {"train_minutes": 240, "train_eur_per_pax": 45, "note": "Milan LIN → Venezia S. Lucia"},
    "BLQ": {"train_minutes": 130, "train_eur_per_pax": 30, "note": "Bologna → Venezia S. Lucia"},
    "FCO": {"train_minutes": 240, "train_eur_per_pax": 60, "note": "Rome FCO → Venezia S. Lucia (Frecciarossa via ROM)"},
    "ZRH": {"train_minutes": 420, "train_eur_per_pax": 90, "note": "Zurich → Venezia S. Lucia (EuroCity via MIL)"},
    "MUC": {"train_minutes": 430, "train_eur_per_pax": 100, "note": "Munich → Venezia S. Lucia (EuroCity via Verona)"},
}


def venice_metadata(gateway: str) -> dict:
    return GATEWAY_TO_VENICE.get(gateway, {"train_minutes": None, "train_eur_per_pax": None, "note": "unknown"})
