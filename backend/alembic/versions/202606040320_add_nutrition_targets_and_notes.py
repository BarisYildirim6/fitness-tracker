"""add nutrition targets and notes

Revision ID: 202606040320
Revises: 202606040220
Create Date: 2026-06-04 03:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606040320"
down_revision: Union[str, None] = "202606040220"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("body_metrics", sa.Column("nutrition_note", sa.String(length=500), nullable=True))
    op.add_column("user_profiles", sa.Column("target_protein_g", sa.Numeric(6, 1), nullable=True))
    op.add_column("user_profiles", sa.Column("target_calories", sa.Integer(), nullable=True))
    op.create_check_constraint(
        "ck_user_profiles_target_protein_non_negative",
        "user_profiles",
        "target_protein_g IS NULL OR target_protein_g >= 0",
    )
    op.create_check_constraint(
        "ck_user_profiles_target_calories_non_negative",
        "user_profiles",
        "target_calories IS NULL OR target_calories >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_user_profiles_target_calories_non_negative", "user_profiles", type_="check")
    op.drop_constraint("ck_user_profiles_target_protein_non_negative", "user_profiles", type_="check")
    op.drop_column("user_profiles", "target_calories")
    op.drop_column("user_profiles", "target_protein_g")
    op.drop_column("body_metrics", "nutrition_note")
