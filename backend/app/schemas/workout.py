from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.exercise import ExerciseRead


class WorkoutLogCreate(BaseModel):
    user_id: UUID
    workout_day_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class WorkoutLogUpdate(BaseModel):
    workout_day_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class WorkoutLogRead(BaseModel):
    id: UUID
    user_id: UUID
    workout_day_id: UUID | None
    started_at: datetime
    completed_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SetLogCreate(BaseModel):
    workout_log_id: UUID
    exercise_id: UUID
    set_index: int = Field(gt=0)
    weight_kg: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=2)
    reps: int = Field(gt=0)
    rpe: Decimal | None = Field(default=None, ge=0, le=10, max_digits=3, decimal_places=1)


class SetLogUpdate(BaseModel):
    set_index: int | None = Field(default=None, gt=0)
    weight_kg: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=2)
    reps: int | None = Field(default=None, gt=0)
    rpe: Decimal | None = Field(default=None, ge=0, le=10, max_digits=3, decimal_places=1)


class SetLogRead(SetLogCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SetLogCreateRequest(BaseModel):
    exercise_id: UUID
    set_index: int = Field(gt=0)
    weight_kg: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=2)
    reps: int = Field(gt=0)
    rpe: Decimal | None = Field(default=None, ge=0, le=10, max_digits=3, decimal_places=1)


class WorkoutLogCreateRequest(BaseModel):
    workout_day_id: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None
    set_logs: list[SetLogCreateRequest] = Field(default_factory=list)


class WorkoutLogDetailRead(WorkoutLogRead):
    set_logs: list[SetLogRead] = Field(default_factory=list)


class WorkoutExerciseOverrideCreate(BaseModel):
    exercise_id: UUID


class WorkoutExerciseOverrideRead(BaseModel):
    id: UUID
    user_id: UUID
    workout_exercise_id: UUID
    exercise_id: UUID
    exercise: ExerciseRead
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
