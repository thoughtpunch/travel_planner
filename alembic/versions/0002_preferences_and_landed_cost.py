"""preferences + landed cost columns

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-25

Adds the JSON columns the `add-preference-weighted-landed-cost` change relies
on: per-config preferences + cost assumptions, per-itinerary landed cost
breakdown + friction + preference explanations, per-run filter counts.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("config", schema=None) as batch:
        batch.add_column(sa.Column("preferences", sa.JSON(), nullable=False, server_default="{}"))
        batch.add_column(sa.Column("cost_assumptions", sa.JSON(), nullable=False, server_default="{}"))

    with op.batch_alter_table("run", schema=None) as batch:
        batch.add_column(
            sa.Column("filtered_out_count_by_axis", sa.JSON(), nullable=False, server_default="{}")
        )

    with op.batch_alter_table("itinerary", schema=None) as batch:
        batch.add_column(sa.Column("landed_cost", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("cost_breakdown", sa.JSON(), nullable=True))
        batch.add_column(sa.Column("friction_attributes", sa.JSON(), nullable=True))
        batch.add_column(
            sa.Column("preference_explanations", sa.JSON(), nullable=False, server_default="[]")
        )


def downgrade() -> None:
    with op.batch_alter_table("itinerary", schema=None) as batch:
        batch.drop_column("preference_explanations")
        batch.drop_column("friction_attributes")
        batch.drop_column("cost_breakdown")
        batch.drop_column("landed_cost")

    with op.batch_alter_table("run", schema=None) as batch:
        batch.drop_column("filtered_out_count_by_axis")

    with op.batch_alter_table("config", schema=None) as batch:
        batch.drop_column("cost_assumptions")
        batch.drop_column("preferences")
