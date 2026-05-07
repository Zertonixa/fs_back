from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "recreate_complaints_uuid"
down_revision = "04e55944b2bb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("complaint_files", if_exists=True)
    op.drop_table("complaints", if_exists=True)

    op.execute("""
    DO $$
    BEGIN
        CREATE TYPE complaint_status AS ENUM ('SENT', 'RECEIVED', 'SOLVED');
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$;
    """)

    complaint_status_enum = postgresql.ENUM(
        "SENT",
        "RECEIVED",
        "SOLVED",
        name="complaint_status",
        create_type=False,
    )

    op.create_table(
        "complaints",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "status",
            complaint_status_enum,
            nullable=False,
            server_default="SENT",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_complaints_user_id", "complaints", ["user_id"], unique=False)

    op.create_table(
        "complaint_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bucket", sa.String(length=255), nullable=False),
        sa.Column("object_key", sa.String(length=1024), nullable=False),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )
    op.create_index(
        "ix_complaint_files_complaint_id",
        "complaint_files",
        ["complaint_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_complaint_files_complaint_id", table_name="complaint_files")
    op.drop_table("complaint_files")

    op.drop_index("ix_complaints_user_id", table_name="complaints")
    op.drop_table("complaints")

    op.execute("DROP TYPE IF EXISTS complaint_status;")