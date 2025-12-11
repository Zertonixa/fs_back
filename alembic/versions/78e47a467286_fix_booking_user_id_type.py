"""fix booking user_id type

Revision ID: 78e47a467286
Revises: 42f85a36d5eb
Create Date: 2025-11-30 12:24:23.518421

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "78e47a467286"
down_revision: Union[str, None] = "42f85a36d5eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "booking",
        "notification_task_id",
        type_=sa.String(),
        existing_type=sa.BigInteger(),
        existing_nullable=True,
        postgresql_using="notification_task_id::text",
    )


def downgrade() -> None:
    op.alter_column(
        "booking",
        "notification_task_id",
        type_=sa.BigInteger(),
        existing_type=sa.String(),
        existing_nullable=True,
        postgresql_using="notification_task_id::bigint",
    )
