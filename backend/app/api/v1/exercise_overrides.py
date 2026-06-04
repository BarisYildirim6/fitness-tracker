from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.constants import SEED_USER_EMAIL
from app.db.session import get_db
from app.models.exercise import Exercise
from app.models.program import Program, WorkoutDay
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutExerciseOverride
from app.schemas.workout import WorkoutExerciseOverrideCreate, WorkoutExerciseOverrideRead

router = APIRouter(prefix="/exercise-overrides", tags=["exercise overrides"])


def get_visible_workout_exercise(db: Session, current_user: User, workout_exercise_id: UUID) -> WorkoutExercise | None:
    return db.scalar(
        select(WorkoutExercise)
        .join(WorkoutDay)
        .join(Program)
        .join(User, Program.user_id == User.id)
        .where(
            WorkoutExercise.id == workout_exercise_id,
            or_(Program.user_id == current_user.id, User.email == SEED_USER_EMAIL),
        )
        .options(selectinload(WorkoutExercise.exercise))
    )


def valid_swap_ids(workout_exercise: WorkoutExercise) -> set[UUID]:
    return {workout_exercise.exercise_id, *[UUID(value) for value in workout_exercise.exercise.alternative_exercise_ids]}


@router.get("", response_model=list[WorkoutExerciseOverrideRead])
def list_exercise_overrides(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[WorkoutExerciseOverride]:
    return db.scalars(
        select(WorkoutExerciseOverride)
        .where(WorkoutExerciseOverride.user_id == current_user.id)
        .options(selectinload(WorkoutExerciseOverride.exercise))
        .order_by(WorkoutExerciseOverride.created_at)
    ).all()


@router.put("/{workout_exercise_id}", response_model=WorkoutExerciseOverrideRead)
def save_exercise_override(
    workout_exercise_id: UUID,
    override_in: WorkoutExerciseOverrideCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WorkoutExerciseOverride:
    workout_exercise = get_visible_workout_exercise(db, current_user, workout_exercise_id)
    if workout_exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout exercise not found")

    if override_in.exercise_id not in valid_swap_ids(workout_exercise):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exercise is not an allowed alternative")

    exercise = db.get(Exercise, override_in.exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    override = db.scalar(
        select(WorkoutExerciseOverride).where(
            WorkoutExerciseOverride.user_id == current_user.id,
            WorkoutExerciseOverride.workout_exercise_id == workout_exercise_id,
        )
    )
    if override is None:
        override = WorkoutExerciseOverride(user_id=current_user.id, workout_exercise_id=workout_exercise_id)
        db.add(override)

    override.exercise_id = override_in.exercise_id
    db.commit()
    return db.scalar(
        select(WorkoutExerciseOverride)
        .where(WorkoutExerciseOverride.id == override.id)
        .options(selectinload(WorkoutExerciseOverride.exercise))
    )


@router.delete("/{workout_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_override(
    workout_exercise_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    override = db.scalar(
        select(WorkoutExerciseOverride).where(
            WorkoutExerciseOverride.user_id == current_user.id,
            WorkoutExerciseOverride.workout_exercise_id == workout_exercise_id,
        )
    )
    if override is not None:
        db.delete(override)
        db.commit()
