"""add workout exercise overrides

Revision ID: 202606040220
Revises: 202606040120
Create Date: 2026-06-04 02:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606040220"
down_revision: Union[str, None] = "202606040120"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workout_exercise_overrides",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("workout_exercise_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "workout_exercise_id", name="uq_workout_exercise_overrides_user_workout_exercise"),
    )
    op.create_index("ix_workout_exercise_overrides_exercise_id", "workout_exercise_overrides", ["exercise_id"])
    op.create_index("ix_workout_exercise_overrides_user_id", "workout_exercise_overrides", ["user_id"])
    op.create_index("ix_workout_exercise_overrides_workout_exercise_id", "workout_exercise_overrides", ["workout_exercise_id"])


def downgrade() -> None:
    op.drop_index("ix_workout_exercise_overrides_workout_exercise_id", table_name="workout_exercise_overrides")
    op.drop_index("ix_workout_exercise_overrides_user_id", table_name="workout_exercise_overrides")
    op.drop_index("ix_workout_exercise_overrides_exercise_id", table_name="workout_exercise_overrides")
    op.drop_table("workout_exercise_overrides")
