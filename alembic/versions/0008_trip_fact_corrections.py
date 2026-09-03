"""Apply verified operational trip corrections.

Revision ID: 0008
Revises: 0007
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | Sequence[str] | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(sa.text("""
        UPDATE wiki_leg
        SET departure_time = '15:15', arrival_time = '17:44',
            origin = 'Torino Porta Nuova', destination = 'Chiavari',
            service = 'Frecciarossa 8623', booking_status = 'tobook',
            confirmation = '', cost_cents = NULL,
            notes = 'Replacement after Damanhur. The cancelled Intercity 511 used PNRs N7PZ5N / N7MGC5; €31.20 Bimbi Gratis refund recorded in the rail ledger.'
        WHERE source_key = 'turin-chiavari'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_leg
        SET arrival_time = '14:30',
            notes = 'Arrive during the property''s approved 14:00–15:00 early check-in window. Scenic Garda west-shore route remains subject to road conditions and timing.'
        WHERE source_key = 'dolomites-malpensa'
    """))

    connection.execute(sa.text("""
        UPDATE wiki_stay SET checkout_time = '10:00'
        WHERE source_key = 'stay-venice'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_stay
        SET checkin_time = '16:00–20:00', checkout_time = '09:30',
            notes = 'Hard check-in window: 16:00–20:00. Verified checkout deadline: 09:30.'
        WHERE source_key = 'stay-dolomites'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_stay
        SET checkin_time = '14:00–15:00',
            notes = 'The property approved this early check-in window.'
        WHERE source_key = 'stay-malpensa'
    """))

    connection.execute(sa.text("""
        UPDATE wiki_itinerary_item
        SET time = '12:20', title = 'ARRIVE AT TORINO PORTA NUOVA',
            detail = 'Stay aboard to the final stop. The flat on Via San Massimo is about 1.1 km away; take a short taxi with the luggage.'
        WHERE day_id = (SELECT id FROM wiki_day WHERE date = '2026-09-13')
          AND title = 'GET OFF AT TORINO PORTA SUSA'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_day
        SET city = 'TURIN → DAMANHUR → LIGURIAN COAST',
            note = 'Damanhur Classic Visit selected. FR 8623 still needs booking.'
        WHERE date = '2026-09-15'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_itinerary_item
        SET time = '07:45',
            detail = 'Take all luggage in the pre-booked NCC to Vidracco. Host Marcello +39 333 822 7352.'
        WHERE day_id = (SELECT id FROM wiki_day WHERE date = '2026-09-15')
          AND title = 'CHECK OUT — Turin'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_itinerary_item
        SET time = '15:15', status = 'tobook',
            title = 'Torino Porta Nuova → Chiavari · Frecciarossa 8623',
            detail = 'Replacement after Damanhur; arrives 17:44. Book for six. The cancelled Intercity 511 used PNRs N7PZ5N / N7MGC5; the €31.20 Bimbi Gratis refund is recorded in the rail ledger.'
        WHERE day_id = (SELECT id FROM wiki_day WHERE date = '2026-09-15')
          AND title LIKE 'Torino Porta Nuova → Chiavari%'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_itinerary_item
        SET time = '~18:00',
            detail = 'Via Vittorio Veneto 16, INTERNO 1, PIANO 1, 16043 Chiavari GE. €506.54 paid. Station is 600 m / 8 min. Piano 1 = first floor; lift NOT confirmed.'
        WHERE day_id = (SELECT id FROM wiki_day WHERE date = '2026-09-15')
          AND title = 'CHECK IN — Vista sul Carruggio, Chiavari'
    """))

    florence_day = connection.scalar(sa.text(
        "SELECT id FROM wiki_day WHERE date = '2026-09-26'"
    ))
    if florence_day is not None:
        connection.execute(sa.text("""
            UPDATE wiki_itinerary_item
            SET detail = 'Verified checkout deadline is 10:00. Take all luggage to Firenze S.M.N.'
            WHERE day_id = :day_id AND title = 'CHECK OUT — Florence'
        """), {"day_id": florence_day})
        exists = connection.scalar(sa.text("""
            SELECT 1 FROM wiki_itinerary_item
            WHERE day_id = :day_id AND title = 'DROP BAGS — KiPoint, Firenze S.M.N.'
        """), {"day_id": florence_day})
        if not exists:
            connection.execute(sa.text("""
                UPDATE wiki_itinerary_item SET ordinal = ordinal + 1
                WHERE day_id = :day_id AND ordinal >= 1
            """), {"day_id": florence_day})
            connection.execute(sa.text("""
                INSERT INTO wiki_itinerary_item
                    (day_id, ordinal, time, kind, status, title, detail)
                VALUES
                    (:day_id, 1, '~10:30', 'admin', 'plan',
                     'DROP BAGS — KiPoint, Firenze S.M.N.',
                     'Leave all luggage at the station KiPoint. Collect it by about 13:20 for the 13:48 Frecciarossa.')
            """), {"day_id": florence_day})

    connection.execute(sa.text("""
        UPDATE wiki_itinerary_item
        SET time = '14:00–15:00',
            detail = 'The property approved this early check-in window. Via Verbano 1, 9 minutes from MXP, restaurant downstairs. $406, charges Oct 9.'
        WHERE day_id = (SELECT id FROM wiki_day WHERE date = '2026-10-14')
          AND title = 'CHECK IN — Osteria della Pista, Casorate Sempione'
    """))

    connection.execute(sa.text("""
        UPDATE activity_option
        SET selection_status = 'selected', scheduled_date = '2026-09-15',
            scheduled_time = '09:00', estimated_cost_cents = 15600,
            estimated_cost_text = '€156 tour for six; transport extra',
            notes = 'Selected, not yet confirmed: call +39 0124 512226 for the English Classic Visit and ask whether Damanhur can arrange a six-person Turin shuttle. Continue on the replacement FR 8623 at 15:15, arriving Chiavari at 17:44; that train still needs booking.',
            updated_at = CURRENT_TIMESTAMP
        WHERE lower(title) LIKE '%damanhur%'
    """))

    connection.execute(sa.text("""
        UPDATE trip_cost
        SET label = '5 rail legs — 3 booked, 2 to book',
            payment_status = 'partial_refund', refunded_cents = 3619,
            note = note || ' Turin–Chiavari change: PNR N7PZ5N Bimbi Gratis €31.20 refunded; tracked as $36.19 at the trip ledger''s working EUR-to-USD rate. Replacement FR 8623 at 15:15 still needs booking.'
        WHERE source_key = 'tr-intercity'
    """))


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text("""
        DELETE FROM wiki_itinerary_item
        WHERE day_id = (SELECT id FROM wiki_day WHERE date = '2026-09-26')
          AND title = 'DROP BAGS — KiPoint, Firenze S.M.N.'
    """))
    connection.execute(sa.text("""
        UPDATE wiki_leg
        SET departure_time = '10:40', arrival_time = '13:10',
            service = 'Intercity 511', booking_status = 'booked',
            confirmation = 'N7PZ5N / N7MGC5', cost_cents = 6760,
            notes = 'Direct. Damanhur on this date would require changing this booked leg to the proposed 15:15 service.'
        WHERE source_key = 'turin-chiavari'
    """))
    connection.execute(sa.text("""
        UPDATE activity_option SET selection_status = 'shortlisted', scheduled_time = ''
        WHERE lower(title) LIKE '%damanhur%'
    """))
    connection.execute(sa.text("""
        UPDATE trip_cost SET refunded_cents = 0, refund_date = NULL
        WHERE source_key = 'tr-intercity'
    """))
