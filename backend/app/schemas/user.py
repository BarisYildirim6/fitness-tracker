from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=72)
    is_active: bool | None = None


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileCreate(BaseModel):
    height_cm: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    current_weight_kg: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    goal: str | None = Field(default=None, max_length=120)
    training_level: str | None = Field(default=None, max_length=50)
    preferred_mode: Literal["home", "gym"] = "home"
    target_weekly_weight_loss_kg: Decimal | None = Field(default=None, ge=0, max_digits=4, decimal_places=2)
    target_protein_g: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=1)
    target_calories: int | None = Field(default=None, ge=0)


class UserProfileUpdate(BaseModel):
    height_cm: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    current_weight_kg: Decimal | None = Field(default=None, gt=0, max_digits=5, decimal_places=2)
    goal: str | None = Field(default=None, max_length=120)
    training_level: str | None = Field(default=None, max_length=50)
    preferred_mode: Literal["home", "gym"] | None = None
    target_weekly_weight_loss_kg: Decimal | None = Field(default=None, ge=0, max_digits=4, decimal_places=2)
    target_protein_g: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=1)
    target_calories: int | None = Field(default=None, ge=0)


class UserProfileRead(UserProfileCreate):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRegister(UserCreate):
    profile: UserProfileCreate | None = None


class UserWithProfileRead(UserRead):
    profile: UserProfileRead | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
