"""Activity, itinerary and ledger lifecycle integration tests."""

from __future__ import annotations

from importlib import reload

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def wiki_client(db_engine, tmp_path, monkeypatch):
    import app.api.wiki as wiki_module
    import app.config as config_module
    import app.main as main_module

    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    reload(config_module)
    reload(wiki_module)
    reload(main_module)
    with TestClient(main_module.app) as client:
        yield client


def _create_selected_activity(client: TestClient) -> dict:
    response = client.post("/api/wiki/activities", json={
        "title": "Test pasta class",
        "stop_ordinal": 4,
        "location": "Florence",
        "estimated_cost": 120,
        "currency": "EUR",
        "selection_status": "selected",
        "scheduled_date": "2026-09-22",
        "scheduled_time": "10:30",
        "notes": "Initial note",
        "user_url": "https://example.com/class",
    })
    assert response.status_code == 201
    return response.json()


def test_activity_creates_ledger_and_cost_edits_flow_back(wiki_client):
    activity = _create_selected_activity(wiki_client)
    assert activity["cost"]["activity_id"] == activity["id"]
    assert activity["cost"]["amount"] == 120
    assert activity["cost"]["booking_status"] == "estimate"

    cost_id = activity["cost"]["id"]
    response = wiki_client.patch(f"/api/wiki/costs/{cost_id}", json={
        "label": "Confirmed pasta class",
        "amount": 138,
        "booking_status": "booked",
        "payment_status": "paid",
        "paid_amount": 138,
        "paid_date": "2026-08-10",
        "note": "Paid from the budget page",
    })
    assert response.status_code == 200

    wiki = wiki_client.get("/api/wiki").json()
    updated = next(item for item in wiki["activities"] if item["id"] == activity["id"])
    assert updated["title"] == "Confirmed pasta class"
    assert updated["selection_status"] == "booked"
    assert updated["actual_cost"] == 138
    assert updated["notes"] == "Paid from the budget page"
    assert updated["cost"]["paid_amount"] == 138


def test_cancellation_and_refund_are_preserved_bidirectionally(wiki_client):
    activity = _create_selected_activity(wiki_client)
    cost_id = activity["cost"]["id"]
    wiki_client.patch(f"/api/wiki/costs/{cost_id}", json={
        "booking_status": "booked", "payment_status": "paid",
        "amount": 120, "paid_amount": 120,
    })

    response = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "selection_status": "cancelled",
        "payment_status": "partial_refund",
        "paid_amount": 120,
        "refunded_amount": 80,
        "refund_date": "2026-08-20",
    })
    assert response.status_code == 200
    cancelled = response.json()
    assert cancelled["selection_status"] == "cancelled"
    assert cancelled["cost"]["booking_status"] == "cancelled"
    assert cancelled["cost"]["refunded_amount"] == 80
    assert cancelled["cost"]["net_paid_amount"] == 40

    response = wiki_client.patch(f"/api/wiki/costs/{cost_id}", json={
        "payment_status": "refunded", "refunded_amount": 120,
    })
    assert response.status_code == 200
    assert response.json()["net_paid_amount"] == 0


def test_deselect_archives_projection_but_keeps_activity(wiki_client):
    activity = _create_selected_activity(wiki_client)
    cost_id = activity["cost"]["id"]
    response = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "selection_status": "option",
    })
    assert response.status_code == 200
    assert response.json()["cost"] is None

    wiki = wiki_client.get("/api/wiki").json()
    assert any(item["id"] == activity["id"] for item in wiki["activities"])
    assert not any(item["id"] == cost_id for item in wiki["costs"])


def test_wont_do_persists_and_can_be_restored(wiki_client):
    activity = _create_selected_activity(wiki_client)
    cost_id = activity["cost"]["id"]

    hidden = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "selection_status": "skipped",
    })
    assert hidden.status_code == 200
    assert hidden.json()["selection_status"] == "skipped"
    assert hidden.json()["cost"] is None

    wiki = wiki_client.get("/api/wiki").json()
    persisted = next(item for item in wiki["activities"] if item["id"] == activity["id"])
    assert persisted["selection_status"] == "skipped"
    assert not any(item["id"] == cost_id for item in wiki["costs"])

    restored = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "selection_status": "selected",
    })
    assert restored.status_code == 200
    assert restored.json()["selection_status"] == "selected"
    assert restored.json()["cost"]["id"] == cost_id


def test_bulk_hide_and_restore_is_atomic(wiki_client):
    wiki = wiki_client.get("/api/wiki").json()
    activity_ids = [
        item["id"] for item in wiki["activities"]
        if item["selection_status"] == "option"
    ][:2]
    assert len(activity_ids) == 2

    hidden = wiki_client.patch("/api/wiki/activities/bulk", json={
        "ids": activity_ids, "action": "hide",
    })
    assert hidden.status_code == 200
    assert set(hidden.json()["statuses"].values()) == {"skipped"}

    wiki = wiki_client.get("/api/wiki").json()
    statuses = {item["id"]: item["selection_status"] for item in wiki["activities"]}
    assert all(statuses[activity_id] == "skipped" for activity_id in activity_ids)

    restored = wiki_client.patch("/api/wiki/activities/bulk", json={
        "ids": activity_ids, "action": "restore",
    })
    assert restored.status_code == 200
    assert set(restored.json()["statuses"].values()) == {"option"}


def test_hiding_paid_activity_keeps_financial_history(wiki_client):
    activity = _create_selected_activity(wiki_client)
    cost_id = activity["cost"]["id"]
    paid = wiki_client.patch(f"/api/wiki/costs/{cost_id}", json={
        "booking_status": "booked", "payment_status": "paid",
        "amount": 120, "paid_amount": 120,
    })
    assert paid.status_code == 200

    hidden = wiki_client.patch("/api/wiki/activities/bulk", json={
        "ids": [activity["id"]], "action": "hide",
    })
    assert hidden.status_code == 200

    wiki = wiki_client.get("/api/wiki").json()
    saved_activity = next(item for item in wiki["activities"] if item["id"] == activity["id"])
    saved_cost = next(item for item in wiki["costs"] if item["id"] == cost_id)
    assert saved_activity["selection_status"] == "skipped"
    assert saved_cost["booking_status"] == "cancelled"
    assert saved_cost["net_paid_amount"] == 120

    restored = wiki_client.patch("/api/wiki/activities/bulk", json={
        "ids": [activity["id"]], "action": "restore",
    })
    assert restored.status_code == 200
    assert restored.json()["statuses"][str(activity["id"])] == "cancelled"


def test_archiving_linked_cost_archives_activity(wiki_client):
    activity = _create_selected_activity(wiki_client)
    cost_id = activity["cost"]["id"]
    response = wiki_client.delete(f"/api/wiki/costs/{cost_id}")
    assert response.status_code == 200

    wiki = wiki_client.get("/api/wiki").json()
    assert not any(item["id"] == activity["id"] for item in wiki["activities"])
    assert not any(item["id"] == cost_id for item in wiki["costs"])


def test_archiving_activity_archives_linked_cost(wiki_client):
    activity = _create_selected_activity(wiki_client)
    cost_id = activity["cost"]["id"]

    response = wiki_client.delete(f"/api/wiki/activities/{activity['id']}")
    assert response.status_code == 200

    wiki = wiki_client.get("/api/wiki").json()
    assert not any(item["id"] == activity["id"] for item in wiki["activities"])
    assert not any(item["id"] == cost_id for item in wiki["costs"])


def test_attachment_upload_download_and_delete(wiki_client):
    activity = _create_selected_activity(wiki_client)
    uploaded = wiki_client.post(
        f"/api/wiki/activities/{activity['id']}/attachments",
        files={"attachment": ("ticket.txt", b"booking confirmation", "text/plain")},
    )
    assert uploaded.status_code == 201
    attachment = uploaded.json()

    downloaded = wiki_client.get(attachment["download_url"])
    assert downloaded.status_code == 200
    assert downloaded.content == b"booking confirmation"

    wiki = wiki_client.get("/api/wiki").json()
    saved = next(item for item in wiki["activities"] if item["id"] == activity["id"])
    assert saved["attachments"][0]["filename"] == "ticket.txt"

    deleted = wiki_client.delete(f"/api/wiki/attachments/{attachment['id']}")
    assert deleted.status_code == 200
    assert wiki_client.get(attachment["download_url"]).status_code == 404

    wiki = wiki_client.get("/api/wiki").json()
    saved = next(item for item in wiki["activities"] if item["id"] == activity["id"])
    assert saved["attachments"] == []


def test_refund_cannot_exceed_payment(wiki_client):
    activity = _create_selected_activity(wiki_client)
    response = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "paid_amount": 25, "refunded_amount": 30,
    })
    assert response.status_code == 422
    assert "cannot exceed" in response.text


def test_activity_date_is_limited_to_its_itinerary_stop(wiki_client):
    activity = _create_selected_activity(wiki_client)

    too_early = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "scheduled_date": "2026-09-18",
    })
    assert too_early.status_code == 422
    assert "Florence activities must be scheduled" in too_early.text

    first_day = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "scheduled_date": "2026-09-19",
    })
    assert first_day.status_code == 200

    last_day = wiki_client.patch(f"/api/wiki/activities/{activity['id']}", json={
        "scheduled_date": "2026-09-26",
    })
    assert last_day.status_code == 200

    invalid_new_activity = wiki_client.post("/api/wiki/activities", json={
        "title": "Wrong-city date",
        "stop_ordinal": 1,
        "location": "Milan",
        "selection_status": "selected",
        "scheduled_date": "2026-09-15",
        "scheduled_time": "10:00",
    })
    assert invalid_new_activity.status_code == 422
    assert "Milan activities must be scheduled" in invalid_new_activity.text


def test_selected_activity_can_be_scheduled_without_a_time(wiki_client):
    response = wiki_client.post("/api/wiki/activities", json={
        "title": "Flexible Milan afternoon",
        "stop_ordinal": 1,
        "location": "Milan",
        "selection_status": "selected",
        "scheduled_date": "2026-09-12",
        "scheduled_time": "",
    })
    assert response.status_code == 201
    assert response.json()["scheduled_date"] == "2026-09-12"
    assert response.json()["scheduled_time"] == ""

    wiki = wiki_client.get("/api/wiki").json()
    saved = next(item for item in wiki["activities"] if item["title"] == "Flexible Milan afternoon")
    assert saved["scheduled_time"] == ""


def test_itinerary_day_and_item_full_crud(wiki_client):
    wiki = wiki_client.get("/api/wiki").json()
    day = next(item for item in wiki["days"] if item["date"] == "2026-09-26")
    original_count = len(day["items"])

    patched_day = wiki_client.patch(f"/api/wiki/days/{day['id']}", json={
        "note": "Bag storage confirmed",
    })
    assert patched_day.status_code == 200

    created = wiki_client.post("/api/wiki/itinerary-items", json={
        "day_id": day["id"], "ordinal": 1, "time": "10:30",
        "kind": "admin", "status": "plan", "title": "Store bags",
        "detail": "KiPoint",
    })
    assert created.status_code == 201
    item_id = created.json()["id"]
    assert created.json()["ordinal"] == 1

    updated = wiki_client.patch(f"/api/wiki/itinerary-items/{item_id}", json={
        "time": "10:45", "status": "booked", "detail": "KiPoint confirmed",
    })
    assert updated.status_code == 200
    assert updated.json()["time"] == "10:45"
    assert updated.json()["status"] == "booked"

    wiki = wiki_client.get("/api/wiki").json()
    saved_day = next(item for item in wiki["days"] if item["id"] == day["id"])
    assert saved_day["note"] == "Bag storage confirmed"
    assert len(saved_day["items"]) == original_count + 1
    assert next(item for item in saved_day["items"] if item["id"] == item_id)["detail"] == "KiPoint confirmed"

    deleted = wiki_client.delete(f"/api/wiki/itinerary-items/{item_id}")
    assert deleted.status_code == 200
    wiki = wiki_client.get("/api/wiki").json()
    saved_day = next(item for item in wiki["days"] if item["id"] == day["id"])
    assert len(saved_day["items"]) == original_count


def test_leg_and_stay_fact_fields_are_mutable(wiki_client):
    wiki = wiki_client.get("/api/wiki").json()
    leg = next(item for item in wiki["legs"] if item["source_key"] == "turin-chiavari")
    stay = next(item for item in wiki["stays"] if item["source_key"] == "stay-dolomites")

    leg_response = wiki_client.patch(f"/api/wiki/legs/{leg['id']}", json={
        "service": "Frecciarossa 8623", "departure_time": "15:15",
        "arrival_time": "17:44", "booking_status": "tobook",
        "confirmation": "", "cost": None, "currency": "eur",
    })
    assert leg_response.status_code == 200

    stay_response = wiki_client.patch(f"/api/wiki/stays/{stay['id']}", json={
        "checkin_time": "16:00–20:00", "checkout_time": "09:30",
        "notes": "Hard check-in window",
    })
    assert stay_response.status_code == 200

    wiki = wiki_client.get("/api/wiki").json()
    saved_leg = next(item for item in wiki["legs"] if item["id"] == leg["id"])
    saved_stay = next(item for item in wiki["stays"] if item["id"] == stay["id"])
    assert saved_leg["service"] == "Frecciarossa 8623"
    assert saved_leg["cost"] is None
    assert saved_leg["currency"] == "EUR"
    assert saved_stay["checkin_time"] == "16:00–20:00"
    assert saved_stay["checkout_time"] == "09:30"


def test_manual_cost_full_crud(wiki_client):
    created = wiki_client.post("/api/wiki/costs", json={
        "label": "Travel insurance", "category": "Insurance",
        "amount": 90, "currency": "USD",
    })
    assert created.status_code == 201
    cost_id = created.json()["id"]

    updated = wiki_client.patch(f"/api/wiki/costs/{cost_id}", json={
        "label": "Family travel insurance", "amount": 95,
        "payment_status": "paid", "paid_amount": 95,
        "payment_reference": "INS-123", "url": "https://example.com/policy",
    })
    assert updated.status_code == 200
    assert updated.json()["label"] == "Family travel insurance"
    assert updated.json()["paid_amount"] == 95

    assert wiki_client.delete(f"/api/wiki/costs/{cost_id}").status_code == 200
    assert not any(item["id"] == cost_id for item in wiki_client.get("/api/wiki").json()["costs"])
