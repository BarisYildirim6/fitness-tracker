"""add exercise easier variation notes

Revision ID: 202606040120
Revises: 202606040020
Create Date: 2026-06-04 01:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606040120"
down_revision: Union[str, None] = "202606040020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("exercises", sa.Column("easier_variation_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("exercises", "easier_variation_notes")

