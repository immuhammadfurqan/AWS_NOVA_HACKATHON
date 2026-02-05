"""Add Google for Jobs columns to jobs table

Revision ID: f8a3b2c4d5e6
Revises: cbef5bcbfb6f
Create Date: 2026-02-02 19:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f8a3b2c4d5e6"
down_revision: Union[str, None] = "6cb6c0e15219"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add company_description column
    op.add_column("jobs", sa.Column("company_description", sa.Text(), nullable=True))

    # Add jd_approval_status column with default value
    op.add_column(
        "jobs",
        sa.Column(
            "jd_approval_status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
    )

    # Add generated_jd column (JSONB for PostgreSQL)
    op.add_column("jobs", sa.Column("generated_jd", postgresql.JSONB(), nullable=True))

    # Add index on jd_approval_status for efficient public queries
    op.create_index(
        "ix_jobs_approval_status", "jobs", ["jd_approval_status"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_approval_status", table_name="jobs")
    op.drop_column("jobs", "generated_jd")
    op.drop_column("jobs", "jd_approval_status")
    op.drop_column("jobs", "company_description")
