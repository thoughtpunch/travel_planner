"""Activity times, user links and durable attachments.

Revision ID: 0005
Revises: 0004
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("activity_option") as batch:
        batch.add_column(sa.Column("scheduled_time", sa.String(), nullable=False, server_default=""))
        batch.add_column(sa.Column("user_url", sa.String(), nullable=False, server_default=""))
    op.create_table(
        "activity_attachment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("storage_key", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False, server_default="application/octet-stream"),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activity_option.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(
        op.f("ix_activity_attachment_activity_id"),
        "activity_attachment", ["activity_id"], unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_activity_attachment_activity_id"), table_name="activity_attachment")
    op.drop_table("activity_attachment")
    with op.batch_alter_table("activity_option") as batch:
        batch.drop_column("user_url")
        batch.drop_column("scheduled_time")
