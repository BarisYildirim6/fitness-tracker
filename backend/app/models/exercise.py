from __future__ import annotations

import uuid

from sqlalchemy import JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Exercise(TimestampMixin, Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    primary_muscle: Mapped[str] = mapped_column(String(80), nullable=False)
    secondary_muscles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    equipment: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    difficulty: Mapped[str | None] = mapped_column(String(50))
    instructions: Mapped[str | None] = mapped_column(Text)
    easier_variation_notes: Mapped[str | None] = mapped_column(Text)
    alternative_exercise_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    set_logs = relationship("SetLog", back_populates="exercise")
