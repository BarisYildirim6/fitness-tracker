from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.body_metric import BodyMetric
from app.models.user import User
from app.schemas.body_metric import BodyMetricRead, NutritionDailyLogRequest

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.post("/daily", response_model=BodyMetricRead, status_code=status.HTTP_200_OK)
def log_daily_nutrition(
    nutrition_in: NutritionDailyLogRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BodyMetric:
    metric = db.scalar(
        select(BodyMetric).where(
            BodyMetric.user_id == current_user.id,
            BodyMetric.date == nutrition_in.date,
        )
    )
    if metric is None:
        metric = BodyMetric(user_id=current_user.id, date=nutrition_in.date)
        db.add(metric)

    metric.protein_g = nutrition_in.protein_g
    metric.calories = nutrition_in.calories
    metric.nutrition_note = nutrition_in.nutrition_note

    db.commit()
    db.refresh(metric)
    return metric
