from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class BodyMetric(TimestampMixin, Base):
    __tablename__ = "body_metrics"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_body_metrics_user_date"),
        CheckConstraint("weight_kg IS NULL OR weight_kg > 0", name="ck_body_metrics_weight_positive"),
        CheckConstraint("waist_cm IS NULL OR waist_cm > 0", name="ck_body_metrics_waist_positive"),
        CheckConstraint("steps IS NULL OR steps >= 0", name="ck_body_metrics_steps_non_negative"),
        CheckConstraint("protein_g IS NULL OR protein_g >= 0", name="ck_body_metrics_protein_non_negative"),
        CheckConstraint("calories IS NULL OR calories >= 0", name="ck_body_metrics_calories_non_negative"),
        CheckConstraint("sleep_hours IS NULL OR sleep_hours >= 0", name="ck_body_metrics_sleep_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    waist_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    steps: Mapped[int | None]
    protein_g: Mapped[Decimal | None] = mapped_column(Numeric(6, 1))
    calories: Mapped[int | None]
    nutrition_note: Mapped[str | None] = mapped_column(String(500))
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    mood: Mapped[str | None] = mapped_column(String(80))

    user = relationship("User", back_populates="body_metrics")
