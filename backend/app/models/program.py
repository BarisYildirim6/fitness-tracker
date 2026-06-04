from __future__ import annotations

import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Program(TimestampMixin, Base):
    __tablename__ = "programs"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_programs_user_name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="programs")
    workout_days = relationship("WorkoutDay", back_populates="program", cascade="all, delete-orphan")


class WorkoutDay(TimestampMixin, Base):
    __tablename__ = "workout_days"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_workout_days_day_of_week"),
        UniqueConstraint("program_id", "day_of_week", name="uq_workout_days_program_day"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    focus: Mapped[str | None] = mapped_column(String(120))

    program = relationship("Program", back_populates="workout_days")
    workout_exercises = relationship(
        "WorkoutExercise",
        back_populates="workout_day",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order_index",
    )
    workout_logs = relationship("WorkoutLog", back_populates="workout_day")
