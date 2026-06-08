from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.constants import SEED_USER_EMAIL
from app.db.session import get_db
from app.models.program import Program, WorkoutDay
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutExerciseOverride
from app.schemas.program import (
    ProgramDetailRead,
    WorkoutDayDetailRead,
    WorkoutDayProgressionRead,
    WorkoutExerciseDetailRead,
)
from app.services.progression import get_progression_suggestion

router = APIRouter(tags=["programs"])


def program_detail_options():
    return (
        selectinload(Program.workout_days)
        .selectinload(WorkoutDay.workout_exercises)
        .selectinload(WorkoutExercise.exercise)
    )


def workout_day_detail_options():
    return selectinload(WorkoutDay.workout_exercises).selectinload(WorkoutExercise.exercise)


def visible_program_filter(current_user: User):
    return or_(Program.user_id == current_user.id, User.email == SEED_USER_EMAIL)


@router.get("/programs", response_model=list[ProgramDetailRead])
def list_programs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Program]:
    return db.scalars(
        select(Program)
        .join(User)
        .where(visible_program_filter(current_user))
        .options(program_detail_options())
        .order_by(case((Program.user_id == current_user.id, 0), else_=1), Program.is_active.desc(), Program.name)
    ).all()


@router.get("/programs/active", response_model=ProgramDetailRead)
def get_active_program(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Program:
    program = db.scalar(
        select(Program)
        .join(User)
        .where(visible_program_filter(current_user), Program.is_active.is_(True))
        .options(program_detail_options())
        .order_by(case((Program.user_id == current_user.id, 0), else_=1), Program.updated_at.desc())
        .limit(1)
    )
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active program not found")
    return program


@router.get("/workout-days/{workout_day_id}", response_model=WorkoutDayDetailRead)
def get_workout_day(
    workout_day_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WorkoutDay:
    workout_day = db.scalar(
        select(WorkoutDay)
        .join(Program)
        .join(User)
        .where(WorkoutDay.id == workout_day_id, visible_program_filter(current_user))
        .options(workout_day_detail_options())
    )
    if workout_day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout day not found")
    return workout_day


@router.get("/workout-days/{workout_day_id}/progression", response_model=WorkoutDayProgressionRead)
def get_workout_day_with_progression(
    workout_day_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WorkoutDayProgressionRead:
    workout_day = db.scalar(
        select(WorkoutDay)
        .join(Program)
        .join(User)
        .where(WorkoutDay.id == workout_day_id, visible_program_filter(current_user))
        .options(workout_day_detail_options())
    )
    if workout_day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout day not found")

    workout_exercise_ids = [item.id for item in workout_day.workout_exercises]
    overrides_by_workout_exercise_id = {}
    if workout_exercise_ids:
        overrides_by_workout_exercise_id = {
            override.workout_exercise_id: override
            for override in db.scalars(
                select(WorkoutExerciseOverride).where(
                    WorkoutExerciseOverride.user_id == current_user.id,
                    WorkoutExerciseOverride.workout_exercise_id.in_(workout_exercise_ids),
                )
            ).all()
        }

    return WorkoutDayProgressionRead.model_validate(
        {
            **WorkoutDayDetailRead.model_validate(workout_day).model_dump(),
            "workout_exercises": [
                {
                    **WorkoutExerciseDetailRead.model_validate(item).model_dump(),
                    "progression_suggestion": get_progression_suggestion(
                        db=db,
                        user_id=current_user.id,
                        workout_exercise=item,
                        exercise_id=overrides_by_workout_exercise_id[item.id].exercise_id
                        if item.id in overrides_by_workout_exercise_id
                        else item.exercise_id,
                    ),
                }
                for item in workout_day.workout_exercises
            ],
        }
    )
