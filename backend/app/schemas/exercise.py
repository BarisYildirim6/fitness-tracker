from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ExerciseDifficulty = Literal["beginner", "intermediate", "advanced"]


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    primary_muscle: str = Field(min_length=1, max_length=80)
    secondary_muscles: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    difficulty: ExerciseDifficulty | None = None
    instructions: str | None = None
    easier_variation_notes: str | None = None
    alternative_exercise_ids: list[UUID] = Field(default_factory=list)


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    primary_muscle: str | None = Field(default=None, min_length=1, max_length=80)
    secondary_muscles: list[str] | None = None
    equipment: list[str] | None = None
    difficulty: ExerciseDifficulty | None = None
    instructions: str | None = None
    easier_variation_notes: str | None = None
    alternative_exercise_ids: list[UUID] | None = None


class ExerciseRead(ExerciseCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseDetailRead(ExerciseRead):
    alternatives: list[ExerciseRead] = Field(default_factory=list)
    equipment_compatible: bool = True
