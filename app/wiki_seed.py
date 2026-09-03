"""Idempotently import the legacy Italy site into the operational wiki.

The old HTML/JS/CSV files remain an audit trail and a one-time source for new
database rows. Existing database rows are never overwritten: after import,
SQLite is authoritative and edits made in the app survive deploys/restarts.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import json5
from sqlalchemy import select

from .db import get_session
from .models import (
    ActivityOption,
    TripCost,
    WikiDay,
    WikiItineraryItem,
    WikiLeg,
    WikiSetting,
    WikiStay,
    WikiStop,
    WikiTraveler,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT = REPO_ROOT / "italy-trip-2026"

STOPS = [
    (1, "milan", "Milan", "Arrival", "2026-09-11", "2026-09-13", 2, "Leonardo Science Museum, the Duomo and an intentionally light arrival day.", "#5B6573", 45.4642, 9.1900),
    (2, "turin", "Turin", "Piedmont", "2026-09-13", "2026-09-15", 2, "Mole House on Via San Massimo. Museo Egizio, the Mole and optional Damanhur visit.", "#28758C", 45.0703, 7.6869),
    (3, "ligurian-coast", "Ligurian coast", "Chiavari base", "2026-09-15", "2026-09-19", 4, "Cinque Terre, Genoa and the Tigullio coast. Rhys turns 18 on September 18.", "#C65035", 44.3167, 9.3247),
    (4, "florence", "Florence", "Work base", "2026-09-19", "2026-09-26", 7, "San Frediano base, Florence museums and a Bologna day trip.", "#9B6A2C", 43.7696, 11.2558),
    (5, "rome", "Rome", "Work base", "2026-09-26", "2026-10-03", 7, "Re di Roma base. Ancient sites, the Vatican and neighborhood days.", "#B8462E", 41.9028, 12.4964),
    (6, "venice", "Venice / Lido", "MuMu and anniversary", "2026-10-03", "2026-10-10", 7, "Lido base beside MuMu. Lagoon days and the anniversary on October 9.", "#225E7A", 45.4408, 12.3155),
    (7, "dolomites", "Dolomites", "Laion base", "2026-10-10", "2026-10-14", 4, "The car leg: Val Gardena, Seceda and Grey's 12th birthday.", "#55704F", 46.5825, 11.5661),
    (8, "malpensa", "Malpensa", "Last night", "2026-10-14", "2026-10-15", 1, "Osteria della Pista, car return and the flight home.", "#76706B", 45.6300, 8.7231),
]

TRAVELERS = [
    (1, "Dan", "adult", None, "Works Italy evenings during the Florence and Rome bases."),
    (2, "Kei", "adult", None, "Knee-friendly routing matters."),
    (3, "Rhys", "child", "2008-09-18", "Turns 18 in Chiavari on September 18."),
    (4, "Jude", "child", None, "Age 16 on the trip."),
    (5, "Grey", "child", "2014-10-12", "Turns 12 in the Dolomites on October 12."),
    (6, "Keir", "child", None, "Age 9 on the trip; minimum-age checks matter."),
]

LEGS = [
    (1, "arrival-mxp", "2026-09-11", "Keflavík", "milan", "flight", "15:45", "21:55", "KEF", "MXP T1", "Icelandair FI592", "booked", "AMBVO4", None, "EUR", "Schengen entry at Malpensa; continue by Malpensa Express."),
    (2, "milan-turin", "2026-09-13", "milan", "turin", "train", "11:15", "12:20", "Milano Porta Garibaldi", "Torino Porta Nuova", "Frecciarossa 9304", "booked", "NY2TU5", 8360, "EUR", "Coach 8. Ride through to Porta Nuova."),
    (3, "turin-chiavari", "2026-09-15", "turin", "ligurian-coast", "train", "15:15", "17:44", "Torino Porta Nuova", "Chiavari", "Frecciarossa 8623", "tobook", "", None, "EUR", "Replacement after Damanhur. The cancelled Intercity 511 used PNRs N7PZ5N / N7MGC5; €31.20 Bimbi Gratis refund recorded in the rail ledger."),
    (4, "chiavari-florence", "2026-09-19", "ligurian-coast", "florence", "train", "09:31", "12:33", "Chiavari", "Firenze S.M.N.", "Intercity 505 + RV 4030", "booked", "N7SKJN / N7S4TN", 11280, "EUR", "Party of seven with Grandma; 23-minute change at Pisa."),
    (5, "florence-rome", "2026-09-26", "florence", "rome", "train", "13:48", "15:35", "Firenze S.M.N.", "Roma Termini", "Frecciarossa 9415", "booked", "N7T7W5 / N7UFZN", 10580, "EUR", "Coach 5."),
    (6, "rome-venice", "2026-10-03", "rome", "venice", "train", "11:35", "15:34", "Roma Termini", "Venezia S. Lucia", "Frecciarossa", "tobook", "", 15700, "EUR", "Direct; current source says book by September 18."),
    (7, "venice-dolomites", "2026-10-10", "venice", "dolomites", "boat+car", "09:30", "16:00", "Lido / VCE", "Laion", "Alilaguna + Budget rental", "booked", "02391839US2", None, "EUR", "Collect the seven-seat automatic at VCE at noon."),
    (8, "dolomites-malpensa", "2026-10-14", "dolomites", "malpensa", "car", "08:30", "14:30", "Laion", "Casorate Sempione", "Budget rental", "plan", "02391839US2", None, "EUR", "Arrive during the property's approved 14:00–15:00 early check-in window. Scenic Garda west-shore route remains subject to road conditions and timing."),
    (9, "departure-mxp", "2026-10-15", "malpensa", "home", "flight", "16:20", "22:15", "MXP", "BWI via KEF", "Icelandair FI591 / FI641", "booked", "AMBVO4", None, "EUR", "Car return at MXP T1 by noon; 1h15 connection at Keflavík."),
]

STAYS = [
    ("stay-milan", "milan", "Milano Chic Retreat", "Via Antonio Dugnani 1, Milano", "2026-09-11", "00:15", "2026-09-13", "10:30", "HMBJHFZ3QS", "lo-milan"),
    ("stay-turin", "turin", '"Mole" House', "Via San Massimo 9, Torino", "2026-09-13", "12:30", "2026-09-15", "09:50", "HMMSR2JEC5", "lo-turin"),
    ("stay-chiavari", "ligurian-coast", "Vista sul Carruggio", "Via Vittorio Veneto 16, Chiavari", "2026-09-15", "15:00", "2026-09-19", "10:00", "", "lo-coast"),
    ("stay-florence", "florence", "San Frediano apartment", "Via dell'Orto 39, Firenze", "2026-09-19", "15:30", "2026-09-26", "10:00", "HMMQEFQS2H", "lo-florence"),
    ("stay-rome", "rome", "Domus Flavii Re di Roma", "Via Appia Nuova 185, Roma", "2026-09-26", "16:00", "2026-10-03", "10:00", "HMHZNB9MW3", "lo-rome"),
    ("stay-venice", "venice", "Appartamento alle terrazze", "Lido di Venezia", "2026-10-03", "", "2026-10-10", "10:00", "HMQTHRTN3R", "lo-venice"),
    ("stay-dolomites", "dolomites", "Funtnatsch Apartment Schlern", "39040 Laion (Lajen) BZ", "2026-10-10", "16:00–20:00", "2026-10-14", "09:30", "5740340654 / PIN 7729", "lo-dolomites"),
    ("stay-malpensa", "malpensa", "Osteria della Pista", "Via Verbano 1, Casorate Sempione", "2026-10-14", "14:00–15:00", "2026-10-15", "11:30", "", "lo-malpensa"),
]


def _money_to_cents(value: str) -> int | None:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return round(float(value) * 100)
    except ValueError:
        return None


def _slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return clean[:120] or "activity"


def _travel_scope(value: str) -> str:
    raw = (value or "base").strip().lower()
    return {
        "in town": "base",
        "base": "base",
        "on the way": "way",
        "way": "way",
        "day-trip": "day",
        "day trip": "day",
        "day": "day",
        "far · own trip": "far",
        "far / own trip": "far",
        "far": "far",
    }.get(raw, raw)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load_itinerary() -> list[dict]:
    source = (LEGACY_ROOT / "public" / "itinerary-data.js").read_text(encoding="utf-8")
    marker = source.index("window.ITINERARY")
    start = source.index("[", marker)
    end = source.rindex("]") + 1
    return json5.loads(source[start:end])


def _load_adventure_costs() -> dict[str, dict]:
    """Load the researched whole-party ranges used by the original explorer."""
    source = (LEGACY_ROOT / "public" / "adventure-costs.js").read_text(encoding="utf-8")
    marker = source.index("window.ADVENTURE_COSTS")
    start = source.index("{", marker)
    end = source.rindex("}") + 1
    return json5.loads(source[start:end])


def _load_shortlist() -> set[str]:
    source = (LEGACY_ROOT / "public" / "shortlist.js").read_text(encoding="utf-8")
    marker = source.index("window.TRIP_SHORTLIST")
    start = source.index("[", marker)
    end = source.rindex("]") + 1
    return set(json5.loads(source[start:end]))


def _seed_settings(session) -> None:
    if session.get(WikiSetting, "trip") is None:
        session.add(WikiSetting(key="trip", value={
            "title": "Italy 2026",
            "family": "Dan, Kei, Rhys, Jude, Grey and Keir",
            "date_start": "2026-09-11",
            "date_end": "2026-10-15",
            "nights": 34,
            "budget_usd": 20000,
            "flight_reference": "Icelandair AMBVO4",
        }))


def _seed_stops(session) -> None:
    existing = set(session.scalars(select(WikiStop.slug)).all())
    for row in STOPS:
        ordinal, slug, name, subtitle, date_start, date_end, nights, summary, accent, lat, lng = row
        if slug not in existing:
            session.add(WikiStop(
                ordinal=ordinal, slug=slug, name=name, subtitle=subtitle,
                date_start=date_start, date_end=date_end, nights=nights,
                summary=summary, accent=accent, latitude=lat, longitude=lng,
            ))


def _seed_travelers(session) -> None:
    if session.scalar(select(WikiTraveler.id).limit(1)) is not None:
        return
    for ordinal, name, role, birth_date, notes in TRAVELERS:
        session.add(WikiTraveler(
            ordinal=ordinal, name=name, role=role, birth_date=birth_date, notes=notes,
        ))


def _seed_legs(session) -> None:
    existing = set(session.scalars(select(WikiLeg.source_key)).all())
    for row in LEGS:
        ordinal, key, date, from_stop, to_stop, mode, departure, arrival, origin, destination, service, status, confirmation, cost_cents, currency, notes = row
        if key in existing:
            continue
        session.add(WikiLeg(
            source_key=key, ordinal=ordinal, date=date, from_stop=from_stop,
            to_stop=to_stop, mode=mode, departure_time=departure,
            arrival_time=arrival, origin=origin, destination=destination,
            service=service, booking_status=status, confirmation=confirmation,
            cost_cents=cost_cents, currency=currency, notes=notes,
        ))


def _seed_stays(session) -> None:
    existing = set(session.scalars(select(WikiStay.source_key)).all())
    for row in STAYS:
        key, stop_slug, name, address, checkin_date, checkin_time, checkout_date, checkout_time, confirmation, cost_key = row
        if key in existing:
            continue
        session.add(WikiStay(
            source_key=key, stop_slug=stop_slug, name=name, address=address,
            checkin_date=checkin_date, checkin_time=checkin_time,
            checkout_date=checkout_date, checkout_time=checkout_time,
            confirmation=confirmation, cost_source_key=cost_key,
        ))


def _seed_itinerary(session) -> None:
    existing_dates = set(session.scalars(select(WikiDay.date)).all())
    for raw_day in _load_itinerary():
        if raw_day["d"] in existing_dates:
            continue
        day = WikiDay(
            date=raw_day["d"], weekday=raw_day.get("wd", ""),
            city=raw_day.get("city", ""), stop_ordinal=int(raw_day.get("leg", 0)),
            note=raw_day.get("note", ""),
        )
        session.add(day)
        session.flush()
        for ordinal, item in enumerate(raw_day.get("items", [])):
            session.add(WikiItineraryItem(
                day_id=day.id, ordinal=ordinal, time=item.get("t", ""),
                kind=item.get("k", "do"), status=item.get("s", "plan"),
                title=item.get("w", ""), detail=item.get("d", ""),
            ))


def _seed_activities(session) -> None:
    existing = {
        activity.source_key: activity
        for activity in session.scalars(select(ActivityOption)).all()
    }
    preexisting_keys = set(existing)
    duplicate_counts: dict[str, int] = {}
    for row in _read_csv(LEGACY_ROOT / "public" / "adventures.csv"):
        base_key = f'{row.get("Leg", "0")}-{_slug(row.get("Title", "activity"))}'
        duplicate_counts[base_key] = duplicate_counts.get(base_key, 0) + 1
        source_key = base_key if duplicate_counts[base_key] == 1 else f"{base_key}-{duplicate_counts[base_key]}"
        activity = existing.get(source_key)
        if activity is None:
            activity = ActivityOption(
                source_key=source_key,
                stop_ordinal=int(row.get("Leg") or 0),
                location=row.get("City", ""), region=row.get("Region", ""),
                title=row.get("Title", ""), description=row.get("Description", ""),
                audience=row.get("Ideal for", "all"), category=row.get("Category", "sight"),
                travel_scope=_travel_scope(row.get("Reach", "base")),
                estimated_cost_text=row.get("Cost", ""), logistics=row.get("How to get there", ""),
                url=row.get("Website", ""), map_url=row.get("Google Maps", ""),
                image_url=row.get("Photo", ""), is_featured=bool((row.get("Adventure") or "").strip()),
                source_details=dict(row), notes="",
            )
            session.add(activity)
            existing[source_key] = activity
        else:
            # These columns were added after the first production import. Fill
            # source-owned rich content without touching choices or user edits.
            activity.description = activity.description or row.get("Description", "")
            activity.map_url = activity.map_url or row.get("Google Maps", "")
            activity.image_url = activity.image_url or row.get("Photo", "")
            activity.is_featured = bool((row.get("Adventure") or "").strip())
            activity.source_details = activity.source_details or dict(row)
            activity.travel_scope = _travel_scope(row.get("Reach", activity.travel_scope))

    # Restore the original explorer's researched party-of-six price model and
    # curated KEEP list. These are source facts, not user choices, so they are
    # safe to backfill on an existing production database. A user-entered
    # estimate is never replaced.
    researched_costs = _load_adventure_costs()
    shortlist = _load_shortlist()
    for source_key, activity in existing.items():
        cost = researched_costs.get(source_key)
        details = dict(activity.source_details or {})
        if cost:
            lo = float(cost["lo"])
            hi = float(cost.get("hi", lo))
            details["party_cost"] = {
                "low": lo,
                "high": hi,
                "midpoint": round((lo + hi) / 2),
                "note": cost.get("note", ""),
                "confidence": cost.get("conf", ""),
            }
            if activity.estimated_cost_cents is None:
                activity.estimated_cost_cents = round((lo + hi) / 2 * 100)
        details["is_shortlist"] = source_key in shortlist
        activity.source_details = details

    # The bike-park audit is a distinct source and includes rejected/fallback
    # choices that are still useful in the trip wiki.
    for row in _read_csv(LEGACY_ROOT / "public" / "bikeparks.csv"):
        source_key = f'bikepark-{_slug(row.get("Park", "activity"))}'
        fit = (row.get("Fit", "") or "").upper()
        activity = existing.get(source_key)
        description = " · ".join(filter(None, [
            f"Rentals: {row.get('Rentals', '')}" if row.get("Rentals") else "",
            f"Lifts: {row.get('Lifts', '')}" if row.get("Lifts") else "",
            f"Season: {row.get('2026 close', '')}" if row.get("2026 close") else "",
            f"Kid fit: {row.get('Kid-friendly', '')}" if row.get("Kid-friendly") else "",
        ]))
        if activity is None:
            activity = ActivityOption(
                source_key=source_key, stop_ordinal=7,
                location=row.get("Location", ""), region=row.get("Region", ""),
                title=row.get("Park", ""), description=description,
                audience="kids", category="bikepark", travel_scope="day",
                estimated_cost_text="", logistics=row.get("Reachable notes", ""),
                source_details=dict(row), notes="",
                selection_status="option" if fit == "YES" else "skipped",
            )
            session.add(activity)
            existing[source_key] = activity
        else:
            activity.description = activity.description or description
            activity.source_details = activity.source_details or dict(row)

    session.flush()

    # Merge hand-maintained status/notes from the normalized working CSV where
    # it identifies a matching legacy activity.
    normalized = _read_csv(LEGACY_ROOT / "tools" / "activities-seed.csv")
    by_title = {a.title: a for a in session.scalars(select(ActivityOption)).all()}
    for row in normalized:
        activity = by_title.get(row.get("title", ""))
        if not activity or activity.source_key in preexisting_keys:
            continue
        raw_status = (row.get("status") or "").strip().lower()
        if raw_status in {"option", "shortlisted", "selected", "booked", "done", "skipped"}:
            activity.selection_status = raw_status
        if row.get("notes") and not activity.notes:
            activity.notes = row["notes"]
        if row.get("updated"):
            activity.scheduled_date = row["updated"] if re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["updated"]) else None

    damanhur = session.scalars(
        select(ActivityOption).where(ActivityOption.title.contains("Damanhur"))
    ).first()
    if damanhur and damanhur.source_key not in preexisting_keys and damanhur.selection_status == "option":
        damanhur.selection_status = "selected"
        damanhur.scheduled_date = "2026-09-15"
        damanhur.scheduled_time = "09:00"
        damanhur.estimated_cost_text = "€156 tour for six; transport extra"
        damanhur.estimated_cost_cents = 15600
        damanhur.logistics = (
            "Classic Visit 09:00–12:30 in Vidracco. All four boys qualify (minimum age 9; Keir is 9). "
            "GTT 4512 cannot arrive by 09:00. Preferred transport: pre-booked NCC from the Turin flat "
            "around 07:45, luggage aboard, then Porta Nuova by about 13:40. Alternative: RV 2717 "
            "07:25–08:23 to Ivrea plus two pre-booked taxis (~€230 total)."
        )
        damanhur.notes = (
            "Selected, not yet confirmed: call +39 0124 512226 for the English Classic Visit and ask "
            "whether Damanhur can arrange a six-person Turin shuttle. Continue on the replacement "
            "FR 8623 at 15:15, arriving Chiavari at 17:44; that train still needs booking."
        )


def _seed_costs(session) -> None:
    existing = set(session.scalars(select(TripCost.source_key)).all())
    for row in _read_csv(LEGACY_ROOT / "public" / "costs.csv"):
        source_key = row.get("id", "")
        if not source_key or source_key in existing:
            continue
        is_rail_ledger = source_key == "tr-intercity"
        session.add(TripCost(
            source_key=source_key, category=row.get("Category", "Other"),
            label=("5 rail legs — 3 booked, 2 to book" if is_rail_ledger else row.get("Item", "")),
            amount_cents=_money_to_cents(row.get("Amount USD", "")),
            booking_status=(row.get("Status", "estimate") or "estimate").lower(),
            payment_status=("partial_refund" if is_rail_ledger else (row.get("Pay Status", "unknown") or "unknown").lower()),
            paid_cents=_money_to_cents(row.get("Paid USD", "")) or 0,
            refunded_cents=3619 if is_rail_ledger else 0,
            paid_date=row.get("Paid Date") or None, due_date=row.get("Due Date") or None,
            payment_reference=row.get("Pay Ref", ""),
            note=(
                row.get("Note", "")
                + (" Turin–Chiavari change: PNR N7PZ5N Bimbi Gratis €31.20 refunded; "
                   "tracked as $36.19 at the trip ledger's working EUR-to-USD rate. "
                   "Replacement FR 8623 at 15:15 still needs booking." if is_rail_ledger else "")
            ),
            url=row.get("URL", ""),
        ))


def _seed_activity_cost_links(session) -> None:
    """Backfill the ledger projection for choices made before revision 0007."""
    session.flush()
    linked_activity_ids = set(
        session.scalars(select(TripCost.activity_id).where(TripCost.activity_id.is_not(None))).all()
    )
    chosen = session.scalars(
        select(ActivityOption).where(
            ActivityOption.selection_status.in_({"selected", "booked", "done", "cancelled"}),
            ActivityOption.is_archived.is_(False),
        )
    ).all()
    for activity in chosen:
        if activity.id in linked_activity_ids:
            continue
        session.add(TripCost(
            activity_id=activity.id,
            source_key=f"activity-{activity.id}",
            category="Activities",
            label=activity.title,
            amount_cents=(
                activity.actual_cost_cents
                if activity.actual_cost_cents is not None
                else activity.estimated_cost_cents
            ),
            currency=activity.currency,
            booking_status=(
                "cancelled" if activity.selection_status == "cancelled"
                else "booked" if activity.selection_status in {"booked", "done"}
                else "estimate"
            ),
            payment_status=("pending" if activity.selection_status in {"booked", "done"} else "unknown"),
            paid_cents=0,
            refunded_cents=0,
            note=activity.notes,
            url=activity.user_url or activity.url,
        ))


def seed_wiki() -> None:
    """Create only missing records; never replace edits made through the API."""
    with get_session() as session:
        _seed_settings(session)
        _seed_stops(session)
        _seed_travelers(session)
        _seed_legs(session)
        _seed_stays(session)
        _seed_itinerary(session)
        _seed_activities(session)
        _seed_costs(session)
        _seed_activity_cost_links(session)
        session.commit()
