from datetime import date as DateOnly
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.body_metric import BodyMetric
from app.models.user import User
from app.schemas.body_metric import BodyMetricCreateRequest, BodyMetricRead

router = APIRouter(prefix="/body-metrics", tags=["body metrics"])


@router.post("", response_model=BodyMetricRead, status_code=status.HTTP_201_CREATED)
def create_body_metric(
    metric_in: BodyMetricCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BodyMetric:
    metric = db.scalar(
        select(BodyMetric).where(
            BodyMetric.user_id == current_user.id,
            BodyMetric.date == metric_in.date,
        )
    )
    if metric is None:
        metric = BodyMetric(user_id=current_user.id, **metric_in.model_dump())
        db.add(metric)
    else:
        for field, value in metric_in.model_dump(exclude_unset=True, exclude={"date"}).items():
            setattr(metric, field, value)

    db.commit()
    db.refresh(metric)
    return metric


@router.get("", response_model=list[BodyMetricRead])
def list_body_metrics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    date_from: Annotated[DateOnly | None, Query()] = None,
    date_to: Annotated[DateOnly | None, Query()] = None,
) -> list[BodyMetric]:
    statement = (
        select(BodyMetric)
        .where(BodyMetric.user_id == current_user.id)
        .order_by(BodyMetric.date.desc(), BodyMetric.created_at.desc())
    )
    if date_from is not None:
        statement = statement.where(BodyMetric.date >= date_from)
    if date_to is not None:
        statement = statement.where(BodyMetric.date <= date_to)
    return db.scalars(statement).all()
