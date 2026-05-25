"""trips + shortlist tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-25

Adds the `trip` and `shortlist_item` tables that back the PrimeVue SPA's
trip-workspace + shortlist features (per `web-api` spec).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trip",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("config_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(), nullable=False, server_default=""),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["config_id"], ["config.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "shortlist_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("itinerary_id", sa.Integer(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("notes", sa.String(), nullable=False, server_default=""),
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trip.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["run.id"]),
        sa.ForeignKeyConstraint(["itinerary_id"], ["itinerary.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("shortlist_item", schema=None) as batch:
        batch.create_index(batch.f("ix_shortlist_item_trip_id"), ["trip_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("shortlist_item", schema=None) as batch:
        batch.drop_index(batch.f("ix_shortlist_item_trip_id"))
    op.drop_table("shortlist_item")
    op.drop_table("trip")
