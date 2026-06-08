from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout import SetLog, WorkoutExercise, WorkoutLog

WEIGHT_STEP_KG = Decimal("2.50")


@dataclass(frozen=True)
class SetPerformance:
    reps: int
    weight_kg: Decimal | None = None
    rpe: Decimal | None = None


@dataclass(frozen=True)
class ProgressionSuggestion:
    exercise_id: UUID
    last_performed_at: datetime | None
    last_weight_kg: Decimal | None
    last_reps: list[int]
    last_average_rpe: Decimal | None
    suggested_weight_kg: Decimal | None
    suggested_reps: int
    suggested_reps_text: str
    reason: str


def average_rpe(sets: Sequence[SetPerformance]) -> Decimal | None:
    rpes = [set_log.rpe for set_log in sets if set_log.rpe is not None]
    if not rpes:
        return None
    return (sum(rpes, Decimal("0")) / Decimal(len(rpes))).quantize(Decimal("0.1"))


def representative_weight(sets: Sequence[SetPerformance]) -> Decimal | None:
    weights = [set_log.weight_kg for set_log in sets if set_log.weight_kg is not None]
    if not weights:
        return None
    return max(weights)


def reps_text(reps: int, note: str | None = None) -> str:
    return f"{reps} reps per set{f' {note}' if note else ''}"


def calculate_progression_suggestion(
    workout_exercise: WorkoutExercise,
    previous_sets: Sequence[SetPerformance],
    last_performed_at: datetime | None = None,
    exercise_id: UUID | None = None,
) -> ProgressionSuggestion:
    target_exercise_id = exercise_id or workout_exercise.exercise_id
    if not previous_sets:
        return ProgressionSuggestion(
            exercise_id=target_exercise_id,
            last_performed_at=None,
            last_weight_kg=None,
            last_reps=[],
            last_average_rpe=None,
            suggested_weight_kg=None,
            suggested_reps=workout_exercise.rep_min,
            suggested_reps_text=f"{workout_exercise.rep_min}-{workout_exercise.rep_max} reps",
            reason="No previous log for this exercise. Use the programmed target.",
        )

    prescribed_sets = list(previous_sets[: workout_exercise.sets])
    completed_all_sets = len(prescribed_sets) >= workout_exercise.sets
    last_reps = [set_log.reps for set_log in prescribed_sets]
    last_weight = representative_weight(prescribed_sets)
    avg_rpe = average_rpe(prescribed_sets)
    all_at_rep_max = completed_all_sets and all(reps >= workout_exercise.rep_max for reps in last_reps)
    all_at_or_above_rep_min = completed_all_sets and all(reps >= workout_exercise.rep_min for reps in last_reps)
    missed_rep_min = any(reps < workout_exercise.rep_min for reps in last_reps)

    if all_at_rep_max and avg_rpe is not None and avg_rpe <= Decimal("8.5"):
        suggested_weight = last_weight + WEIGHT_STEP_KG if last_weight is not None else None
        return ProgressionSuggestion(
            exercise_id=target_exercise_id,
            last_performed_at=last_performed_at,
            last_weight_kg=last_weight,
            last_reps=last_reps,
            last_average_rpe=avg_rpe,
            suggested_weight_kg=suggested_weight,
            suggested_reps=workout_exercise.rep_min,
            suggested_reps_text=f"{workout_exercise.rep_min}-{workout_exercise.rep_max} reps after weight increase",
            reason="All prescribed sets reached the top of the rep range with manageable RPE. Increase weight next time.",
        )

    if missed_rep_min and avg_rpe is not None and avg_rpe >= Decimal("9.0"):
        suggested_weight = max(last_weight - WEIGHT_STEP_KG, Decimal("0")) if last_weight is not None else None
        return ProgressionSuggestion(
            exercise_id=target_exercise_id,
            last_performed_at=last_performed_at,
            last_weight_kg=last_weight,
            last_reps=last_reps,
            last_average_rpe=avg_rpe,
            suggested_weight_kg=suggested_weight,
            suggested_reps=workout_exercise.rep_min,
            suggested_reps_text=f"{workout_exercise.rep_min}-{workout_exercise.rep_max} reps",
            reason="One or more sets missed the minimum rep target at high RPE. Repeat or reduce weight slightly.",
        )

    if all_at_or_above_rep_min and avg_rpe is not None and avg_rpe <= Decimal("6.0"):
        next_reps = min(workout_exercise.rep_max, min(last_reps) + 1)
        reason = "RPE was low while reps stayed in range. Add reps; if already near the top, consider a small weight increase."
        suggested_weight = last_weight if next_reps < workout_exercise.rep_max else (last_weight + WEIGHT_STEP_KG if last_weight is not None else None)
        return ProgressionSuggestion(
            exercise_id=target_exercise_id,
            last_performed_at=last_performed_at,
            last_weight_kg=last_weight,
            last_reps=last_reps,
            last_average_rpe=avg_rpe,
            suggested_weight_kg=suggested_weight,
            suggested_reps=next_reps,
            suggested_reps_text=reps_text(next_reps),
            reason=reason,
        )

    if all_at_or_above_rep_min:
        next_reps = min(workout_exercise.rep_max, min(last_reps) + 1)
        reason = "All prescribed sets were within the rep range. Keep weight the same and add reps."
        if all_at_rep_max and avg_rpe is None:
            reason = "All prescribed sets reached the top of the range. Repeat the load and log RPE to confirm a weight increase."
        return ProgressionSuggestion(
            exercise_id=target_exercise_id,
            last_performed_at=last_performed_at,
            last_weight_kg=last_weight,
            last_reps=last_reps,
            last_average_rpe=avg_rpe,
            suggested_weight_kg=last_weight,
            suggested_reps=next_reps,
            suggested_reps_text=reps_text(next_reps),
            reason=reason,
        )

    return ProgressionSuggestion(
        exercise_id=target_exercise_id,
        last_performed_at=last_performed_at,
        last_weight_kg=last_weight,
        last_reps=last_reps,
        last_average_rpe=avg_rpe,
        suggested_weight_kg=last_weight,
        suggested_reps=workout_exercise.rep_min,
        suggested_reps_text=f"{workout_exercise.rep_min}-{workout_exercise.rep_max} reps",
        reason="Previous sets were below the target range. Repeat the load and focus on hitting the minimum reps.",
    )


def latest_set_performances_for_exercise(
    db: Session,
    user_id: UUID,
    exercise_id: UUID,
) -> tuple[list[SetPerformance], datetime | None]:
    latest_log = db.scalar(
        select(WorkoutLog)
        .join(SetLog)
        .where(WorkoutLog.user_id == user_id, SetLog.exercise_id == exercise_id)
        .options(selectinload(WorkoutLog.set_logs))
        .order_by(WorkoutLog.started_at.desc(), WorkoutLog.created_at.desc())
        .limit(1)
    )
    if latest_log is None:
        return [], None

    sets = [
        SetPerformance(reps=set_log.reps, weight_kg=set_log.weight_kg, rpe=set_log.rpe)
        for set_log in sorted(latest_log.set_logs, key=lambda value: value.set_index)
        if set_log.exercise_id == exercise_id
    ]
    return sets, latest_log.started_at


def get_progression_suggestion(
    db: Session,
    user_id: UUID,
    workout_exercise: WorkoutExercise,
    exercise_id: UUID | None = None,
) -> ProgressionSuggestion:
    target_exercise_id = exercise_id or workout_exercise.exercise_id
    sets, last_performed_at = latest_set_performances_for_exercise(db, user_id, target_exercise_id)
    return calculate_progression_suggestion(
        workout_exercise=workout_exercise,
        previous_sets=sets,
        last_performed_at=last_performed_at,
        exercise_id=target_exercise_id,
    )
