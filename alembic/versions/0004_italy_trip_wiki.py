"""Italy trip operational wiki tables.

Revision ID: 0004
Revises: 0003
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wiki_setting",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_table(
        "wiki_stop",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("subtitle", sa.String(), nullable=False, server_default=""),
        sa.Column("date_start", sa.String(), nullable=False),
        sa.Column("date_end", sa.String(), nullable=False),
        sa.Column("nights", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("accent", sa.String(), nullable=False, server_default="#173F5F"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wiki_stop_slug"), "wiki_stop", ["slug"], unique=True)
    op.create_table(
        "wiki_traveler",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="family"),
        sa.Column("birth_date", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "wiki_leg",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_key", sa.String(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("from_stop", sa.String(), nullable=False),
        sa.Column("to_stop", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("departure_time", sa.String(), nullable=False, server_default=""),
        sa.Column("arrival_time", sa.String(), nullable=False, server_default=""),
        sa.Column("origin", sa.String(), nullable=False, server_default=""),
        sa.Column("destination", sa.String(), nullable=False, server_default=""),
        sa.Column("service", sa.String(), nullable=False, server_default=""),
        sa.Column("booking_status", sa.String(), nullable=False, server_default="plan"),
        sa.Column("confirmation", sa.String(), nullable=False, server_default=""),
        sa.Column("party_size", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("cost_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(), nullable=False, server_default="EUR"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wiki_leg_source_key"), "wiki_leg", ["source_key"], unique=True)
    op.create_table(
        "wiki_stay",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_key", sa.String(), nullable=False),
        sa.Column("stop_slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False, server_default=""),
        sa.Column("checkin_date", sa.String(), nullable=False),
        sa.Column("checkin_time", sa.String(), nullable=False, server_default=""),
        sa.Column("checkout_date", sa.String(), nullable=False),
        sa.Column("checkout_time", sa.String(), nullable=False, server_default=""),
        sa.Column("booking_status", sa.String(), nullable=False, server_default="booked"),
        sa.Column("confirmation", sa.String(), nullable=False, server_default=""),
        sa.Column("cost_source_key", sa.String(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wiki_stay_source_key"), "wiki_stay", ["source_key"], unique=True)
    op.create_index(op.f("ix_wiki_stay_stop_slug"), "wiki_stay", ["stop_slug"], unique=False)
    op.create_table(
        "wiki_day",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("weekday", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("stop_ordinal", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wiki_day_date"), "wiki_day", ["date"], unique=True)
    op.create_table(
        "wiki_itinerary_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("day_id", sa.Integer(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("time", sa.String(), nullable=False, server_default=""),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(["day_id"], ["wiki_day.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_wiki_itinerary_item_day_id"), "wiki_itinerary_item", ["day_id"], unique=False
    )
    op.create_table(
        "activity_option",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_key", sa.String(), nullable=False),
        sa.Column("stop_ordinal", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False, server_default=""),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("audience", sa.String(), nullable=False, server_default="all"),
        sa.Column("category", sa.String(), nullable=False, server_default="sight"),
        sa.Column("travel_scope", sa.String(), nullable=False, server_default="base"),
        sa.Column("estimated_cost_text", sa.String(), nullable=False, server_default=""),
        sa.Column("estimated_cost_cents", sa.Integer(), nullable=True),
        sa.Column("actual_cost_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(), nullable=False, server_default="EUR"),
        sa.Column("logistics", sa.Text(), nullable=False, server_default=""),
        sa.Column("url", sa.String(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("selection_status", sa.String(), nullable=False, server_default="option"),
        sa.Column("scheduled_date", sa.String(), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_activity_option_source_key"), "activity_option", ["source_key"], unique=True
    )
    op.create_table(
        "trip_cost",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_key", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
        sa.Column("booking_status", sa.String(), nullable=False, server_default="estimate"),
        sa.Column("payment_status", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("paid_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("paid_date", sa.String(), nullable=True),
        sa.Column("due_date", sa.String(), nullable=True),
        sa.Column("payment_reference", sa.Text(), nullable=False, server_default=""),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("url", sa.String(), nullable=False, server_default=""),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trip_cost_source_key"), "trip_cost", ["source_key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_trip_cost_source_key"), table_name="trip_cost")
    op.drop_table("trip_cost")
    op.drop_index(op.f("ix_activity_option_source_key"), table_name="activity_option")
    op.drop_table("activity_option")
    op.drop_index(op.f("ix_wiki_itinerary_item_day_id"), table_name="wiki_itinerary_item")
    op.drop_table("wiki_itinerary_item")
    op.drop_index(op.f("ix_wiki_day_date"), table_name="wiki_day")
    op.drop_table("wiki_day")
    op.drop_index(op.f("ix_wiki_stop_slug"), table_name="wiki_stop")
    op.drop_table("wiki_stop")
    op.drop_index(op.f("ix_wiki_stay_stop_slug"), table_name="wiki_stay")
    op.drop_index(op.f("ix_wiki_stay_source_key"), table_name="wiki_stay")
    op.drop_table("wiki_stay")
    op.drop_index(op.f("ix_wiki_leg_source_key"), table_name="wiki_leg")
    op.drop_table("wiki_leg")
    op.drop_table("wiki_traveler")
    op.drop_table("wiki_setting")
