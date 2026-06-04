from __future__ import annotations

from datetime import date as DateOnly, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BodyMetricCreate(BaseModel):
    user_id: UUID
    date: DateOnly
    weight_kg: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    waist_cm: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    steps: int | None = Field(default=None, ge=0)
    protein_g: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=1)
    calories: int | None = Field(default=None, ge=0)
    nutrition_note: str | None = Field(default=None, max_length=500)
    sleep_hours: Decimal | None = Field(default=None, ge=0, max_digits=3, decimal_places=1)
    mood: str | None = Field(default=None, max_length=80)


class BodyMetricUpdate(BaseModel):
    date: DateOnly | None = None
    weight_kg: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    waist_cm: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    steps: int | None = Field(default=None, ge=0)
    protein_g: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=1)
    calories: int | None = Field(default=None, ge=0)
    nutrition_note: str | None = Field(default=None, max_length=500)
    sleep_hours: Decimal | None = Field(default=None, ge=0, max_digits=3, decimal_places=1)
    mood: str | None = Field(default=None, max_length=80)


class BodyMetricRead(BodyMetricCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BodyMetricCreateRequest(BaseModel):
    date: DateOnly
    weight_kg: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    waist_cm: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    steps: int | None = Field(default=None, ge=0)
    protein_g: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=1)
    calories: int | None = Field(default=None, ge=0)
    nutrition_note: str | None = Field(default=None, max_length=500)
    sleep_hours: Decimal | None = Field(default=None, ge=0, max_digits=3, decimal_places=1)
    mood: str | None = Field(default=None, max_length=80)


class NutritionDailyLogRequest(BaseModel):
    date: DateOnly
    protein_g: Decimal = Field(ge=0, max_digits=6, decimal_places=1)
    calories: int = Field(ge=0)
    nutrition_note: str | None = Field(default=None, max_length=500)
