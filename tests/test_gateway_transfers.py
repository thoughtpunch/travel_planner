"""Sanity tests for the hardcoded gateway → Venice transfer table.

Per `landed-cost-model` Decision 5 + task 2.3: every entry must have a
`last_reviewed` date and a non-empty `notes` field. A static lint warns
(does not fail) if any entry is older than 180 days.
"""

from __future__ import annotations

import warnings
from datetime import date, timedelta

import pytest

from app.data.gateway_transfers import GATEWAY_TRANSFERS, snapshot_table

SEEDED_GATEWAYS = {"VCE", "MXP", "LIN", "BLQ", "VRN", "TRS", "ZRH", "MUC"}


def test_seeded_gateways_present():
    """The seed set the spec calls for must all be present."""
    missing = SEEDED_GATEWAYS - set(GATEWAY_TRANSFERS)
    assert not missing, f"missing gateways in transfer table: {missing}"


@pytest.mark.parametrize("gateway", sorted(SEEDED_GATEWAYS))
def test_every_entry_has_last_reviewed_and_notes(gateway):
    entries = GATEWAY_TRANSFERS[gateway]
    assert entries, f"{gateway} has no transfer entries"
    for entry in entries:
        assert entry.last_reviewed is not None, f"{gateway}/{entry.mode}: last_reviewed missing"
        assert entry.notes.strip(), f"{gateway}/{entry.mode}: notes empty"
        assert entry.per_person_cost >= 0
        assert entry.duration_minutes > 0


def test_last_reviewed_freshness_warning():
    """Warn (don't fail) if any entry is more than 180 days stale."""
    cutoff = date.today() - timedelta(days=180)
    stale: list[tuple[str, str, date]] = []
    for gateway, entries in GATEWAY_TRANSFERS.items():
        for e in entries:
            if e.last_reviewed < cutoff:
                stale.append((gateway, e.mode, e.last_reviewed))
    if stale:
        warnings.warn(
            f"{len(stale)} gateway-transfer entries older than 180 days: {stale}",
            stacklevel=2,
        )


def test_snapshot_table_is_serialisable():
    snap = snapshot_table()
    assert SEEDED_GATEWAYS.issubset(snap.keys())
    # Every snapshot entry has the fields the runner persists into config_snapshot.
    for gw, entries in snap.items():
        for e in entries:
            assert e["mode"] in {"rail", "ferry", "bus", "drive"}
            assert isinstance(e["per_person_cost"], int)
            assert isinstance(e["last_reviewed"], str)
            assert isinstance(e["last_viable_onward_local_time"], str)
            assert e["notes"]
