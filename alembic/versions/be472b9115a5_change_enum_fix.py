"""Fix complaint_status enum values

Revision ID: be472b9115a5
Revises: d603f62ad583
Create Date: 2026-04-02 18:47:54.132932

"""
from typing import Sequence, Union
from alembic import op

revision: str = "be472b9115a5"
down_revision: Union[str, None] = "d603f62ad583"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE complaint_status RENAME TO complaint_status_old;")

    op.execute("CREATE TYPE complaint_status AS ENUM ('SENT', 'RECEIVED', 'SOLVED', 'UPDATED');")

    op.execute("ALTER TABLE complaints ALTER COLUMN status DROP DEFAULT;")

    op.execute("""
        ALTER TABLE complaints
        ALTER COLUMN status
        TYPE complaint_status
        USING (
            CASE
                WHEN status::text = 'Updated' THEN 'UPDATED'::complaint_status
                ELSE UPPER(status::text)::complaint_status
            END
        );
    """)

    op.execute("ALTER TABLE complaints ALTER COLUMN status SET DEFAULT 'SENT'::complaint_status;")

    op.execute("DROP TYPE complaint_status_old;")



def downgrade() -> None:
    op.execute("UPDATE complaints SET status = 'SENT' WHERE status::text = 'UPDATED';")

    op.execute("ALTER TYPE complaint_status RENAME TO complaint_status_old;")

    op.execute("CREATE TYPE complaint_status AS ENUM ('SENT', 'RECEIVED', 'SOLVED');")

    op.execute("""
        ALTER TABLE complaints ALTER COLUMN status DROP DEFAULT;

        ALTER TABLE complaints
        ALTER COLUMN status
        TYPE complaint_status
        USING status::text::complaint_status;

        ALTER TABLE complaints ALTER COLUMN status SET DEFAULT 'SENT'::complaint_status;
    """)

    op.execute("DROP TYPE complaint_status_old;")
