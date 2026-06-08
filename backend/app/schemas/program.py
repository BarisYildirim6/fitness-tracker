from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.exercise import ExerciseRead


class ProgramCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    is_active: bool = True


class ProgramUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    is_active: bool | None = None


class ProgramRead(ProgramCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutDayCreate(BaseModel):
    program_id: UUID
    day_of_week: int = Field(ge=1, le=7)
    title: str = Field(min_length=1, max_length=160)
    focus: str | None = Field(default=None, max_length=120)


class WorkoutDayUpdate(BaseModel):
    day_of_week: int | None = Field(default=None, ge=1, le=7)
    title: str | None = Field(default=None, min_length=1, max_length=160)
    focus: str | None = Field(default=None, max_length=120)


class WorkoutDayRead(WorkoutDayCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutExerciseCreate(BaseModel):
    workout_day_id: UUID
    exercise_id: UUID
    order_index: int = Field(ge=0)
    sets: int = Field(gt=0)
    rep_min: int = Field(gt=0)
    rep_max: int = Field(gt=0)
    rest_seconds: int | None = Field(default=None, ge=0)
    tempo: str | None = Field(default=None, max_length=40)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_rep_range(self) -> "WorkoutExerciseCreate":
        if self.rep_max < self.rep_min:
            raise ValueError("rep_max must be greater than or equal to rep_min")
        return self


class WorkoutExerciseUpdate(BaseModel):
    exercise_id: UUID | None = None
    order_index: int | None = Field(default=None, ge=0)
    sets: int | None = Field(default=None, gt=0)
    rep_min: int | None = Field(default=None, gt=0)
    rep_max: int | None = Field(default=None, gt=0)
    rest_seconds: int | None = Field(default=None, ge=0)
    tempo: str | None = Field(default=None, max_length=40)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_rep_range(self) -> "WorkoutExerciseUpdate":
        if self.rep_min is not None and self.rep_max is not None and self.rep_max < self.rep_min:
            raise ValueError("rep_max must be greater than or equal to rep_min")
        return self


class WorkoutExerciseRead(WorkoutExerciseCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutExerciseDetailRead(WorkoutExerciseRead):
    exercise: ExerciseRead


class ProgressionSuggestionRead(BaseModel):
    exercise_id: UUID
    last_performed_at: datetime | None = None
    last_weight_kg: Decimal | None = None
    last_reps: list[int] = Field(default_factory=list)
    last_average_rpe: Decimal | None = None
    suggested_weight_kg: Decimal | None = None
    suggested_reps: int
    suggested_reps_text: str
    reason: str

    model_config = ConfigDict(from_attributes=True)


class WorkoutExerciseProgressionRead(WorkoutExerciseDetailRead):
    progression_suggestion: ProgressionSuggestionRead


class WorkoutDayDetailRead(WorkoutDayRead):
    workout_exercises: list[WorkoutExerciseDetailRead] = Field(default_factory=list)


class WorkoutDayProgressionRead(WorkoutDayRead):
    workout_exercises: list[WorkoutExerciseProgressionRead] = Field(default_factory=list)


class ProgramDetailRead(ProgramRead):
    workout_days: list[WorkoutDayDetailRead] = Field(default_factory=list)
