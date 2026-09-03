"""Restore complete activity content and imagery.

Revision ID: 0006
Revises: 0005
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("activity_option") as batch:
        batch.add_column(sa.Column("description", sa.Text(), nullable=False, server_default=""))
        batch.add_column(sa.Column("map_url", sa.String(), nullable=False, server_default=""))
        batch.add_column(sa.Column("image_url", sa.Text(), nullable=False, server_default=""))
        batch.add_column(sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("source_details", sa.JSON(), nullable=False, server_default="{}"))


def downgrade() -> None:
    with op.batch_alter_table("activity_option") as batch:
        batch.drop_column("source_details")
        batch.drop_column("is_featured")
        batch.drop_column("image_url")
        batch.drop_column("map_url")
        batch.drop_column("description")
