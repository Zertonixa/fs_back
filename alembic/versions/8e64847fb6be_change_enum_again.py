"""Change enum

Revision ID: f4b682c1b01d
Revises: recreate_complaints_uuid
Create Date: 2026-04-02 18:47:54.132932

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "8e64847fb6be"
down_revision: Union[str, None] = "f4b682c1b01d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE complaintstatus ADD VALUE IF NOT EXISTS 'Updated';")


def downgrade() -> None:
    op.execute("""
    ALTER TYPE complaintstatus RENAME TO complaintstatus_old;
    """)

    op.execute("""
    CREATE TYPE complaintstatus AS ENUM ('Sent', 'Received', 'Solved');
    """)

    op.execute("""
    ALTER TABLE complaints
    ALTER COLUMN status
    TYPE complaintstatus
    USING status::text::complaintstatus;
    """)

    op.execute("""
    DROP TYPE complaintstatus_old;
    """)