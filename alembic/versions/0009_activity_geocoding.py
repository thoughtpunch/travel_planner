"""Persist geocoded activity coordinates.

Revision ID: 0009
Revises: 0008
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009"
down_revision: str | Sequence[str] | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("activity_option") as batch:
        batch.add_column(sa.Column("latitude", sa.Float(), nullable=True))
        batch.add_column(sa.Column("longitude", sa.Float(), nullable=True))
        batch.add_column(sa.Column("geocode_precision", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("activity_option") as batch:
        batch.drop_column("geocode_precision")
        batch.drop_column("longitude")
        batch.drop_column("latitude")
