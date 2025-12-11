"""add booking celery task ids

Revision ID: a65ef663550a
Revises: 20d4b1d14495
Create Date: 2025-12-07 16:47:44.932254

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a65ef663550a"
down_revision: Union[str, None] = "20d4b1d14495"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "booking",
        sa.Column("start_reminder_task_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "booking",
        sa.Column("end_reminder_task_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "booking",
        sa.Column("complete_task_id", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("booking", "complete_task_id")
    op.drop_column("booking", "end_reminder_task_id")
    op.drop_column("booking", "start_reminder_task_id")
