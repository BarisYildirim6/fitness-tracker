from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    profile: Mapped[UserProfile | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    programs = relationship("Program", back_populates="user", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog", back_populates="user", cascade="all, delete-orphan")
    body_metrics = relationship("BodyMetric", back_populates="user", cascade="all, delete-orphan")


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("height_cm > 0", name="ck_user_profiles_height_positive"),
        CheckConstraint("current_weight_kg > 0", name="ck_user_profiles_weight_positive"),
        CheckConstraint(
            "target_weekly_weight_loss_kg >= 0",
            name="ck_user_profiles_target_loss_non_negative",
        ),
        CheckConstraint("preferred_mode IN ('home', 'gym')", name="ck_user_profiles_preferred_mode"),
        CheckConstraint(
            "target_protein_g IS NULL OR target_protein_g >= 0",
            name="ck_user_profiles_target_protein_non_negative",
        ),
        CheckConstraint(
            "target_calories IS NULL OR target_calories >= 0",
            name="ck_user_profiles_target_calories_non_negative",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    current_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    goal: Mapped[str | None] = mapped_column(String(120))
    training_level: Mapped[str | None] = mapped_column(String(50))
    preferred_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="home")
    target_weekly_weight_loss_kg: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    target_protein_g: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    target_calories: Mapped[int | None]

    user: Mapped[User] = relationship(back_populates="profile")
