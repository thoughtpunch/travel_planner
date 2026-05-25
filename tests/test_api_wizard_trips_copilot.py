"""Contract tests for the new SPA-supporting endpoints from
add-primevue-trip-wizard:

- Wizard state PATCH (idempotent merge, rejects incoherent prefs)
- Config finalize (422 on bad preferences)
- Config preview (dry-run matrix size + constructed stopover count)
- Trips CRUD + soft delete
- Shortlist CRUD with immutable snapshots
- Copilot endpoints with contract enforcement (cost suggestions must be
  unverified; forbidden paths rejected)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(db_engine):
    from app.main import app
    return TestClient(app)


def _minimal_config_body(**overrides):
    body = {
        "name": "Test trip",
        "budget_party_total": 8000,
        "currency": "USD",
        "passengers": {"adults": 6},
        "structures": ["A"],
        "blackout_ranges": [],
        "validation_tolerance_pct": 15,
        "validation_top_n": 5,
        "envelope_long_gap_days": 30,
        "preferences": {},
        "cost_assumptions": {},
        "legs": [
            {"ordinal": 1, "origins": ["SJO"], "destinations": ["VCE"],
             "date_anchor": "2027-01-10", "window_days": 1, "sampling_strategy": "anchor"},
        ],
    }
    body.update(overrides)
    return body


# Wizard PATCH ---------------------------------------------------------------

def test_patch_config_merges_partial_preferences(client):
    r = client.post("/api/configs", json=_minimal_config_body())
    assert r.status_code == 201
    cid = r.json()["id"]

    # PATCH only one axis — other fields untouched.
    r = client.patch(f"/api/configs/{cid}", json={
        "preferences": {"defaults": {"layover_length": {"position": "avoid", "threshold": 180}}},
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["preferences"]["defaults"]["layover_length"]["position"] == "avoid"

    # Second PATCH on a different axis — first remains.
    r = client.patch(f"/api/configs/{cid}", json={
        "preferences": {"defaults": {"red_eye": {"position": "strongly_avoid"}}},
    })
    assert r.status_code == 200
    prefs = r.json()["preferences"]["defaults"]
    assert prefs["layover_length"]["position"] == "avoid"
    assert prefs["red_eye"]["position"] == "strongly_avoid"


def test_patch_config_rejects_incoherent_preferences(client):
    r = client.post("/api/configs", json=_minimal_config_body())
    cid = r.json()["id"]
    # HARD YES on layover_length — not admitted.
    r = client.patch(f"/api/configs/{cid}", json={
        "preferences": {"defaults": {"layover_length": {"position": "hard_yes"}}},
    })
    assert r.status_code == 422
    assert "HARD YES is not meaningful" in r.text or "layover_length" in r.text


def test_finalize_rejects_incoherent(client):
    r = client.post("/api/configs", json=_minimal_config_body(
        preferences={"defaults": {"stopover": {"position": "hard_yes"}}},
    ))
    # POST itself validates and rejects.
    assert r.status_code in (400, 422)


def test_finalize_passes_when_coherent(client):
    r = client.post("/api/configs", json=_minimal_config_body())
    cid = r.json()["id"]
    r = client.post(f"/api/configs/{cid}/finalize")
    assert r.status_code == 200


# Preview --------------------------------------------------------------------

def test_preview_returns_matrix_and_stopover_count(client):
    r = client.post("/api/configs", json=_minimal_config_body(
        preferences={
            "defaults": {"stopover": {"position": "hard_yes"}},
            "stopover_target": {"city": "MAD"},
        },
        cost_assumptions={"stopover_lodging_per_night": 300, "stopover_rooms": 2},
    ))
    cid = r.json()["id"]
    r = client.get(f"/api/configs/{cid}/preview")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["constructed_stopover_count"] >= 1
    assert body["stopover_matrix_size"] > 0
    assert body["planned_serpapi_calls"] > 0


# Trips CRUD -----------------------------------------------------------------

def test_trip_create_get_patch_softdelete(client):
    # Create with implicit draft config.
    r = client.post("/api/trips", json={"name": "Venice spring"})
    assert r.status_code == 201, r.text
    trip = r.json()
    assert trip["name"] == "Venice spring"
    tid = trip["id"]

    # Get.
    r = client.get(f"/api/trips/{tid}")
    assert r.status_code == 200

    # Patch name + notes.
    r = client.patch(f"/api/trips/{tid}", json={"name": "Venice 2026", "notes": "first pass"})
    assert r.status_code == 200
    assert r.json()["name"] == "Venice 2026"
    assert r.json()["notes"] == "first pass"

    # Soft delete.
    r = client.delete(f"/api/trips/{tid}")
    assert r.status_code == 204

    # Not in default list.
    r = client.get("/api/trips")
    assert all(t["id"] != tid for t in r.json())
    # But appears with include_deleted.
    r = client.get("/api/trips?include_deleted=true")
    assert any(t["id"] == tid for t in r.json())


def test_trip_create_with_existing_config(client):
    r = client.post("/api/configs", json=_minimal_config_body())
    cid = r.json()["id"]
    r = client.post("/api/trips", json={"name": "T2", "config_id": cid})
    assert r.status_code == 201
    assert r.json()["config_id"] == cid


def test_trip_create_unknown_config_404(client):
    r = client.post("/api/trips", json={"name": "T3", "config_id": 99999})
    assert r.status_code == 404


# Shortlist (snapshot fidelity) ---------------------------------------------

def test_shortlist_snapshot_is_immutable(client, db_engine):
    """The save-to-shortlist endpoint snapshots the itinerary fully; later
    edits to the underlying run/itinerary MUST NOT mutate the snapshot."""
    from app.db import get_session
    from app.enums import RunStatus
    from app.models import Itinerary, Run

    # Create a trip + config + run + itinerary by hand.
    r = client.post("/api/trips", json={"name": "Snapshot trip"})
    tid = r.json()["id"]
    cid = r.json()["config_id"]

    with get_session() as s:
        run = Run(config_id=cid, config_snapshot={}, status=RunStatus.COMPLETE.value)
        s.add(run)
        s.commit()
        s.refresh(run)
        it = Itinerary(
            run_id=run.id, structure="A", total_party_price=5400,
            currency="USD", verification_status="VALIDATED",
            fare_ids=[], gateway="VCE", flags=[], rank=1,
            landed_cost=5460,
            cost_breakdown={"total": 5460, "currency": "USD", "components": [
                {"label": "Airfare", "per_person_amount": 900, "party_multiplier": 6,
                 "total": 5400, "currency": "USD", "data_source": "validated_airfare",
                 "user_overridable": True, "metadata": {}, "original_table_value": None}
            ], "forces_overnight": False},
        )
        s.add(it)
        s.commit()
        s.refresh(it)
        run_id, itin_id = run.id, it.id

    # Save to shortlist.
    r = client.post(f"/api/trips/{tid}/shortlist", json={"run_id": run_id, "itinerary_id": itin_id})
    assert r.status_code == 201, r.text
    snap_total = r.json()["snapshot"]["landed_cost"]

    # Mutate the underlying itinerary — snapshot must not change.
    with get_session() as s:
        it = s.get(Itinerary, itin_id)
        it.landed_cost = 99999
        s.add(it)
        s.commit()

    r = client.get(f"/api/trips/{tid}/shortlist")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["snapshot"]["landed_cost"] == snap_total
    assert snap_total == 5460


def test_shortlist_update_and_delete(client):
    r = client.post("/api/trips", json={"name": "Edit-list trip"})
    tid = r.json()["id"]
    cid = r.json()["config_id"]

    from app.db import get_session
    from app.enums import RunStatus
    from app.models import Itinerary, Run

    with get_session() as s:
        run = Run(config_id=cid, config_snapshot={}, status=RunStatus.COMPLETE.value)
        s.add(run); s.commit(); s.refresh(run)
        it = Itinerary(run_id=run.id, structure="A", total_party_price=5400,
                       currency="USD", verification_status="VALIDATED",
                       fare_ids=[], gateway="VCE", flags=[], rank=1)
        s.add(it); s.commit(); s.refresh(it)
        rid, iid = run.id, it.id

    r = client.post(f"/api/trips/{tid}/shortlist", json={"run_id": rid, "itinerary_id": iid})
    item_id = r.json()["id"]

    r = client.patch(f"/api/trips/{tid}/shortlist/{item_id}", json={
        "notes": "looks good", "tags": ["leading"], "order_index": 5,
    })
    assert r.status_code == 200
    assert r.json()["notes"] == "looks good"
    assert r.json()["tags"] == ["leading"]
    assert r.json()["order_index"] == 5

    r = client.delete(f"/api/trips/{tid}/shortlist/{item_id}")
    assert r.status_code == 204


# Copilot contract enforcement ----------------------------------------------

def test_copilot_preferences_suggests(client):
    r = client.post("/api/copilot/preferences/suggest", json={
        "natural_language": "family with two toddlers, hate red-eyes",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert "suggestions" in body
    assert all(not s.get("unverified", False) for s in body["suggestions"]
               if not s["path"].startswith("cost_assumptions"))


def test_copilot_cost_suggestions_carry_unverified_flag(client):
    r = client.post("/api/copilot/cost_assumptions/suggest", json={
        "trip_context": {"party": 6},
    })
    assert r.status_code == 200, r.text
    for s in r.json()["suggestions"]:
        assert s["unverified"] is True, f"cost suggestion missing unverified flag: {s}"


def test_copilot_gateway_rejects_cost_without_unverified(client, monkeypatch):
    """Force the stub to return a cost suggestion without unverified=True;
    the gateway must reject with 502."""
    from app.schemas import CopilotResponse, CopilotSuggestion

    def _bad(_ctx):
        return CopilotResponse(suggestions=[CopilotSuggestion(
            path="cost_assumptions.stopover_lodging_per_night",
            value=400, confidence=0.5, rationale="forgot the flag", unverified=False,
        )])

    monkeypatch.setattr("app.api.copilot.suggest_cost_assumptions", _bad)
    r = client.post("/api/copilot/cost_assumptions/suggest", json={"trip_context": {}})
    assert r.status_code == 502
    assert "contract violation" in r.text


def test_copilot_gateway_rejects_forbidden_path(client, monkeypatch):
    from app.schemas import CopilotResponse, CopilotSuggestion

    def _bad(_nl):
        return CopilotResponse(suggestions=[CopilotSuggestion(
            path="results.exclude_itinerary_ids", value=[1, 2],
            confidence=0.9, rationale="don't show these", unverified=False,
        )])

    monkeypatch.setattr("app.api.copilot.suggest_preferences", _bad)
    r = client.post("/api/copilot/preferences/suggest", json={"natural_language": "x"})
    assert r.status_code == 422
    assert "forbidden" in r.text.lower()


def test_copilot_stopover_waypoints(client):
    r = client.post("/api/copilot/stopover_waypoints/suggest", json={
        "origin": "SJO", "destination_gateways": ["VCE", "MXP"],
    })
    assert r.status_code == 200
    body = r.json()
    assert "candidates" in body and len(body["candidates"]) > 0


# SPA catch-all --------------------------------------------------------------

def test_spa_catchall_returns_503_when_not_built(client):
    r = client.get("/trips/42")
    # In a clean test env the SPA isn't built; we expect either 200 (built)
    # or 503 (graceful fallback message).
    assert r.status_code in (200, 503)
