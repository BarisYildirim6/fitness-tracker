"""initial database layer

Revision ID: 202606040020
Revises:
Create Date: 2026-06-04 00:20:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606040020"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "exercises",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("primary_muscle", sa.String(length=80), nullable=False),
        sa.Column("secondary_muscles", sa.JSON(), nullable=False),
        sa.Column("equipment", sa.JSON(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("alternative_exercise_ids", sa.JSON(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercises_name", "exercises", ["name"], unique=True)

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("height_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("current_weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("goal", sa.String(length=120), nullable=True),
        sa.Column("training_level", sa.String(length=50), nullable=True),
        sa.Column("preferred_mode", sa.String(length=20), nullable=False),
        sa.Column("target_weekly_weight_loss_kg", sa.Numeric(4, 2), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("height_cm > 0", name="ck_user_profiles_height_positive"),
        sa.CheckConstraint("current_weight_kg > 0", name="ck_user_profiles_weight_positive"),
        sa.CheckConstraint("preferred_mode IN ('home', 'gym')", name="ck_user_profiles_preferred_mode"),
        sa.CheckConstraint(
            "target_weekly_weight_loss_kg >= 0",
            name="ck_user_profiles_target_loss_non_negative",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "programs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_programs_user_name"),
    )
    op.create_index("ix_programs_user_id", "programs", ["user_id"])

    op.create_table(
        "body_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(5, 2), nullable=True),
        sa.Column("waist_cm", sa.Numeric(5, 2), nullable=True),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("protein_g", sa.Numeric(6, 1), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=True),
        sa.Column("sleep_hours", sa.Numeric(3, 1), nullable=True),
        sa.Column("mood", sa.String(length=80), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("calories IS NULL OR calories >= 0", name="ck_body_metrics_calories_non_negative"),
        sa.CheckConstraint("protein_g IS NULL OR protein_g >= 0", name="ck_body_metrics_protein_non_negative"),
        sa.CheckConstraint("sleep_hours IS NULL OR sleep_hours >= 0", name="ck_body_metrics_sleep_non_negative"),
        sa.CheckConstraint("steps IS NULL OR steps >= 0", name="ck_body_metrics_steps_non_negative"),
        sa.CheckConstraint("waist_cm IS NULL OR waist_cm > 0", name="ck_body_metrics_waist_positive"),
        sa.CheckConstraint("weight_kg IS NULL OR weight_kg > 0", name="ck_body_metrics_weight_positive"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_body_metrics_user_date"),
    )
    op.create_index("ix_body_metrics_user_id", "body_metrics", ["user_id"])

    op.create_table(
        "workout_days",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("program_id", sa.Uuid(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("focus", sa.String(length=120), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_workout_days_day_of_week"),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("program_id", "day_of_week", name="uq_workout_days_program_day"),
    )
    op.create_index("ix_workout_days_program_id", "workout_days", ["program_id"])

    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workout_day_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=False),
        sa.Column("rep_min", sa.Integer(), nullable=False),
        sa.Column("rep_max", sa.Integer(), nullable=False),
        sa.Column("rest_seconds", sa.Integer(), nullable=True),
        sa.Column("tempo", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("order_index >= 0", name="ck_workout_exercises_order_non_negative"),
        sa.CheckConstraint("rep_max >= rep_min", name="ck_workout_exercises_rep_range"),
        sa.CheckConstraint("rep_min > 0", name="ck_workout_exercises_rep_min_positive"),
        sa.CheckConstraint(
            "rest_seconds IS NULL OR rest_seconds >= 0",
            name="ck_workout_exercises_rest_non_negative",
        ),
        sa.CheckConstraint("sets > 0", name="ck_workout_exercises_sets_positive"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["workout_day_id"], ["workout_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workout_day_id", "order_index", name="uq_workout_exercises_day_order"),
    )
    op.create_index("ix_workout_exercises_exercise_id", "workout_exercises", ["exercise_id"])
    op.create_index("ix_workout_exercises_workout_day_id", "workout_exercises", ["workout_day_id"])

    op.create_table(
        "workout_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("workout_day_id", sa.Uuid(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="ck_workout_logs_completed_after_started",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workout_day_id"], ["workout_days.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workout_logs_user_id", "workout_logs", ["user_id"])
    op.create_index("ix_workout_logs_workout_day_id", "workout_logs", ["workout_day_id"])

    op.create_table(
        "set_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workout_log_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("set_index", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("rpe", sa.Numeric(3, 1), nullable=True),
        *timestamp_columns(),
        sa.CheckConstraint("reps > 0", name="ck_set_logs_reps_positive"),
        sa.CheckConstraint("rpe IS NULL OR (rpe >= 0 AND rpe <= 10)", name="ck_set_logs_rpe_range"),
        sa.CheckConstraint("set_index > 0", name="ck_set_logs_set_index_positive"),
        sa.CheckConstraint("weight_kg IS NULL OR weight_kg >= 0", name="ck_set_logs_weight_non_negative"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["workout_log_id"], ["workout_logs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workout_log_id", "exercise_id", "set_index", name="uq_set_logs_workout_exercise_set"),
    )
    op.create_index("ix_set_logs_exercise_id", "set_logs", ["exercise_id"])
    op.create_index("ix_set_logs_workout_log_id", "set_logs", ["workout_log_id"])


def downgrade() -> None:
    op.drop_index("ix_set_logs_workout_log_id", table_name="set_logs")
    op.drop_index("ix_set_logs_exercise_id", table_name="set_logs")
    op.drop_table("set_logs")

    op.drop_index("ix_workout_logs_workout_day_id", table_name="workout_logs")
    op.drop_index("ix_workout_logs_user_id", table_name="workout_logs")
    op.drop_table("workout_logs")

    op.drop_index("ix_workout_exercises_workout_day_id", table_name="workout_exercises")
    op.drop_index("ix_workout_exercises_exercise_id", table_name="workout_exercises")
    op.drop_table("workout_exercises")

    op.drop_index("ix_workout_days_program_id", table_name="workout_days")
    op.drop_table("workout_days")

    op.drop_index("ix_body_metrics_user_id", table_name="body_metrics")
    op.drop_table("body_metrics")

    op.drop_index("ix_programs_user_id", table_name="programs")
    op.drop_table("programs")

    op.drop_table("user_profiles")

    op.drop_index("ix_exercises_name", table_name="exercises")
    op.drop_table("exercises")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

