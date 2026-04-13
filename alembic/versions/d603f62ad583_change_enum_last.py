"""Change enum

Revision ID: f4b682c1b01d
Revises: recreate_complaints_uuid
Create Date: 2026-04-02 18:47:54.132932

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d603f62ad583"
down_revision: Union[str, None] = "8e64847fb6be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE complaint_status ADD VALUE IF NOT EXISTS 'Updated';")


def downgrade() -> None:
    op.execute("""
    ALTER TYPE complaint_status RENAME TO complaint_status_old;
    """)

    op.execute("""
    CREATE TYPE complaint_status AS ENUM ('Sent', 'Received', 'Solved');
    """)

    op.execute("""
    ALTER TABLE complaints
    ALTER COLUMN status
    TYPE complaint_status
    USING status::text::complaint_status;
    """)

    op.execute("""
    DROP TYPE complaint_status;
    """)