from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.exercise import ExerciseDetailRead, ExerciseRead

router = APIRouter(prefix="/exercises", tags=["exercises"])


HOME_EQUIPMENT_KEYWORDS = {
    "adjustable",
    "bodyweight",
    "barbell",
    "dumbbell",
    "floor",
    "chair",
    "band",
    "walking",
    "shoes",
    "optional",
}


def equipment_compatible(exercise: Exercise, preferred_mode: str | None) -> bool:
    if preferred_mode == "gym":
        return True
    equipment_text = " ".join(exercise.equipment).lower()
    return any(keyword in equipment_text for keyword in HOME_EQUIPMENT_KEYWORDS)


@router.get("", response_model=list[ExerciseRead])
def list_exercises(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    muscle: Annotated[str | None, Query(min_length=1)] = None,
    equipment: Annotated[str | None, Query(min_length=1)] = None,
) -> list[Exercise]:
    del current_user
    exercises = db.scalars(select(Exercise).order_by(Exercise.name)).all()

    if muscle is not None:
        muscle_filter = muscle.strip().lower()
        exercises = [
            exercise
            for exercise in exercises
            if exercise.primary_muscle.lower() == muscle_filter
            or muscle_filter in [secondary.lower() for secondary in exercise.secondary_muscles]
        ]

    if equipment is not None:
        equipment_filter = equipment.strip().lower()
        exercises = [
            exercise
            for exercise in exercises
            if any(equipment_filter in item.lower() for item in exercise.equipment)
        ]

    return list(exercises)


@router.get("/{exercise_id}", response_model=ExerciseDetailRead)
def get_exercise(
    exercise_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ExerciseDetailRead:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    alternative_ids = [UUID(value) for value in exercise.alternative_exercise_ids]
    alternatives = db.scalars(select(Exercise).where(Exercise.id.in_(alternative_ids)).order_by(Exercise.name)).all()
    preferred_mode = current_user.profile.preferred_mode if current_user.profile else "home"
    return ExerciseDetailRead.model_validate(
        {
            **ExerciseRead.model_validate(exercise).model_dump(),
            "alternatives": alternatives,
            "equipment_compatible": equipment_compatible(exercise, preferred_mode),
        }
    )
