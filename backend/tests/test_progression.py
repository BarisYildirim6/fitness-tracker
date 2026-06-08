from decimal import Decimal
from uuid import uuid4

from app.models.workout import WorkoutExercise
from app.services.progression import SetPerformance, calculate_progression_suggestion


def workout_exercise() -> WorkoutExercise:
    return WorkoutExercise(
        workout_day_id=uuid4(),
        exercise_id=uuid4(),
        order_index=0,
        sets=3,
        rep_min=8,
        rep_max=12,
        rest_seconds=90,
    )


def test_progression_uses_programmed_target_without_history() -> None:
    suggestion = calculate_progression_suggestion(workout_exercise(), [])

    assert suggestion.last_reps == []
    assert suggestion.suggested_weight_kg is None
    assert suggestion.suggested_reps == 8
    assert suggestion.suggested_reps_text == "8-12 reps"


def test_progression_increases_weight_after_all_sets_at_rep_max_with_manageable_rpe() -> None:
    suggestion = calculate_progression_suggestion(
        workout_exercise(),
        [
            SetPerformance(weight_kg=Decimal("20.00"), reps=12, rpe=Decimal("8.0")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=12, rpe=Decimal("8.5")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=12, rpe=Decimal("8.0")),
        ],
    )

    assert suggestion.last_average_rpe == Decimal("8.2")
    assert suggestion.suggested_weight_kg == Decimal("22.50")
    assert suggestion.suggested_reps == 8
    assert "Increase weight" in suggestion.reason


def test_progression_keeps_weight_and_adds_reps_inside_range() -> None:
    suggestion = calculate_progression_suggestion(
        workout_exercise(),
        [
            SetPerformance(weight_kg=Decimal("20.00"), reps=10, rpe=Decimal("8.0")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=9, rpe=Decimal("8.0")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=9, rpe=Decimal("8.5")),
        ],
    )

    assert suggestion.suggested_weight_kg == Decimal("20.00")
    assert suggestion.suggested_reps == 10
    assert "add reps" in suggestion.reason


def test_progression_reduces_weight_after_missing_minimum_at_high_rpe() -> None:
    suggestion = calculate_progression_suggestion(
        workout_exercise(),
        [
            SetPerformance(weight_kg=Decimal("20.00"), reps=8, rpe=Decimal("9.0")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=7, rpe=Decimal("9.5")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=6, rpe=Decimal("9.5")),
        ],
    )

    assert suggestion.suggested_weight_kg == Decimal("17.50")
    assert suggestion.suggested_reps == 8
    assert "reduce weight" in suggestion.reason


def test_progression_pushes_reps_or_weight_when_rpe_is_low() -> None:
    suggestion = calculate_progression_suggestion(
        workout_exercise(),
        [
            SetPerformance(weight_kg=Decimal("20.00"), reps=10, rpe=Decimal("6.0")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=10, rpe=Decimal("5.5")),
            SetPerformance(weight_kg=Decimal("20.00"), reps=10, rpe=Decimal("6.0")),
        ],
    )

    assert suggestion.suggested_weight_kg == Decimal("20.00")
    assert suggestion.suggested_reps == 11
    assert "RPE was low" in suggestion.reason
