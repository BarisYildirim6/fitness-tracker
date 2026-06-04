from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class WorkoutExercise(TimestampMixin, Base):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        CheckConstraint("order_index >= 0", name="ck_workout_exercises_order_non_negative"),
        CheckConstraint("sets > 0", name="ck_workout_exercises_sets_positive"),
        CheckConstraint("rep_min > 0", name="ck_workout_exercises_rep_min_positive"),
        CheckConstraint("rep_max >= rep_min", name="ck_workout_exercises_rep_range"),
        CheckConstraint("rest_seconds IS NULL OR rest_seconds >= 0", name="ck_workout_exercises_rest_non_negative"),
        UniqueConstraint("workout_day_id", "order_index", name="uq_workout_exercises_day_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workout_day_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_days.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(nullable=False)
    sets: Mapped[int] = mapped_column(nullable=False)
    rep_min: Mapped[int] = mapped_column(nullable=False)
    rep_max: Mapped[int] = mapped_column(nullable=False)
    rest_seconds: Mapped[int | None]
    tempo: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)

    workout_day = relationship("WorkoutDay", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    overrides = relationship("WorkoutExerciseOverride", back_populates="workout_exercise", cascade="all, delete-orphan")


class WorkoutExerciseOverride(TimestampMixin, Base):
    __tablename__ = "workout_exercise_overrides"
    __table_args__ = (
        UniqueConstraint("user_id", "workout_exercise_id", name="uq_workout_exercise_overrides_user_workout_exercise"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    workout_exercise = relationship("WorkoutExercise", back_populates="overrides")
    exercise = relationship("Exercise")


class WorkoutLog(TimestampMixin, Base):
    __tablename__ = "workout_logs"
    __table_args__ = (
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="ck_workout_logs_completed_after_started",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    workout_day_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workout_days.id", ondelete="SET NULL"),
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    user = relationship("User", back_populates="workout_logs")
    workout_day = relationship("WorkoutDay", back_populates="workout_logs")
    set_logs = relationship("SetLog", back_populates="workout_log", cascade="all, delete-orphan")


class SetLog(TimestampMixin, Base):
    __tablename__ = "set_logs"
    __table_args__ = (
        CheckConstraint("set_index > 0", name="ck_set_logs_set_index_positive"),
        CheckConstraint("weight_kg IS NULL OR weight_kg >= 0", name="ck_set_logs_weight_non_negative"),
        CheckConstraint("reps > 0", name="ck_set_logs_reps_positive"),
        CheckConstraint("rpe IS NULL OR (rpe >= 0 AND rpe <= 10)", name="ck_set_logs_rpe_range"),
        UniqueConstraint("workout_log_id", "exercise_id", "set_index", name="uq_set_logs_workout_exercise_set"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workout_log_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workout_logs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    set_index: Mapped[int] = mapped_column(nullable=False)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    reps: Mapped[int] = mapped_column(nullable=False)
    rpe: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))

    workout_log = relationship("WorkoutLog", back_populates="set_logs")
    exercise = relationship("Exercise", back_populates="set_logs")
