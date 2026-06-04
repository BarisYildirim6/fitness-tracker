from datetime import date as DateOnly, datetime, time
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.constants import SEED_USER_EMAIL
from app.db.session import get_db
from app.models.program import Program, WorkoutDay
from app.models.user import User
from app.models.workout import SetLog, WorkoutLog
from app.schemas.workout import WorkoutLogCreateRequest, WorkoutLogDetailRead

router = APIRouter(prefix="/workout-logs", tags=["workout logs"])


def start_of_day(value: DateOnly) -> datetime:
    return datetime.combine(value, time.min)


def end_exclusive(value: DateOnly) -> datetime:
    return datetime.combine(value, time.max)


def workout_log_detail_options():
    return selectinload(WorkoutLog.set_logs).selectinload(SetLog.exercise)


def user_can_access_workout_day(db: Session, user: User, workout_day_id: UUID) -> bool:
    return (
        db.scalar(
            select(WorkoutDay.id)
            .join(Program)
            .join(User, Program.user_id == User.id)
            .where(WorkoutDay.id == workout_day_id, or_(Program.user_id == user.id, User.email == SEED_USER_EMAIL))
            .limit(1)
        )
        is not None
    )


@router.post("", response_model=WorkoutLogDetailRead, status_code=status.HTTP_201_CREATED)
def create_workout_log(
    log_in: WorkoutLogCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WorkoutLog:
    if log_in.workout_day_id is not None and not user_can_access_workout_day(db, current_user, log_in.workout_day_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout day not found")

    workout_log = WorkoutLog(
        user_id=current_user.id,
        workout_day_id=log_in.workout_day_id,
        notes=log_in.notes,
    )
    if log_in.started_at is not None:
        workout_log.started_at = log_in.started_at
    if log_in.completed_at is not None:
        workout_log.completed_at = log_in.completed_at

    db.add(workout_log)
    db.flush()

    for set_log_in in log_in.set_logs:
        db.add(SetLog(workout_log_id=workout_log.id, **set_log_in.model_dump()))

    db.commit()
    return db.scalar(
        select(WorkoutLog).where(WorkoutLog.id == workout_log.id).options(workout_log_detail_options())
    )


@router.get("", response_model=list[WorkoutLogDetailRead])
def list_workout_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    date_from: Annotated[DateOnly | None, Query()] = None,
    date_to: Annotated[DateOnly | None, Query()] = None,
) -> list[WorkoutLog]:
    statement = (
        select(WorkoutLog)
        .where(WorkoutLog.user_id == current_user.id)
        .options(workout_log_detail_options())
        .order_by(WorkoutLog.started_at.desc(), WorkoutLog.created_at.desc())
    )

    if date_from is not None:
        statement = statement.where(WorkoutLog.started_at >= start_of_day(date_from))
    if date_to is not None:
        statement = statement.where(WorkoutLog.started_at <= end_exclusive(date_to))

    return db.scalars(statement).all()


@router.get("/{workout_log_id}", response_model=WorkoutLogDetailRead)
def get_workout_log(
    workout_log_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WorkoutLog:
    workout_log = db.scalar(
        select(WorkoutLog)
        .where(WorkoutLog.id == workout_log_id, WorkoutLog.user_id == current_user.id)
        .options(workout_log_detail_options())
    )
    if workout_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
    return workout_log
