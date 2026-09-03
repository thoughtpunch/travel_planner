"""Link activities to costs and record refunds.

Revision ID: 0007
Revises: 0006
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("trip_cost") as batch:
        batch.add_column(sa.Column("activity_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("refunded_cents", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("refund_date", sa.String(), nullable=True))
        batch.create_foreign_key(
            "fk_trip_cost_activity_id_activity_option",
            "activity_option", ["activity_id"], ["id"], ondelete="SET NULL",
        )
        batch.create_unique_constraint("uq_trip_cost_activity_id", ["activity_id"])


def downgrade() -> None:
    with op.batch_alter_table("trip_cost") as batch:
        batch.drop_constraint("uq_trip_cost_activity_id", type_="unique")
        batch.drop_constraint("fk_trip_cost_activity_id_activity_option", type_="foreignkey")
        batch.drop_column("refund_date")
        batch.drop_column("refunded_cents")
        batch.drop_column("activity_id")
