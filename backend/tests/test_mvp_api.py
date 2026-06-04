from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.program import Program, WorkoutDay
from app.models.user import User
from app.models.workout import WorkoutExercise


def auth_headers(client: TestClient, email: str = "mvp@example.com") -> dict[str, str]:
    password = "strong-password"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_user(db: Session, email: str = "mvp@example.com") -> User:
    return db.query(User).filter(User.email == email).one()


def create_program_fixture(db: Session, user: User) -> tuple[Exercise, Program, WorkoutDay]:
    exercise = Exercise(
        name="Goblet Squat",
        primary_muscle="quads",
        secondary_muscles=["glutes", "core"],
        equipment=["adjustable dumbbell"],
        difficulty="beginner",
        instructions="Hold a dumbbell at the chest and squat with control.",
        easier_variation_notes="Use bodyweight or squat to a box.",
        alternative_exercise_ids=[],
    )
    program = Program(
        user_id=user.id,
        name="Test Home Plan",
        description="A test plan",
        is_active=True,
    )
    db.add_all([exercise, program])
    db.flush()

    workout_day = WorkoutDay(
        program_id=program.id,
        day_of_week=1,
        title="Monday Lower",
        focus="Legs",
    )
    db.add(workout_day)
    db.flush()

    db.add(
        WorkoutExercise(
            workout_day_id=workout_day.id,
            exercise_id=exercise.id,
            order_index=0,
            sets=3,
            rep_min=8,
            rep_max=12,
            rest_seconds=90,
        )
    )
    db.commit()
    return exercise, program, workout_day


def test_exercises_are_protected_and_filterable(client: TestClient, db_session: Session) -> None:
    headers = auth_headers(client)
    user = get_user(db_session)
    exercise, _, _ = create_program_fixture(db_session, user)

    unauthorized_response = client.get("/api/v1/exercises")
    assert unauthorized_response.status_code == 401

    list_response = client.get("/api/v1/exercises?muscle=quads&equipment=dumbbell", headers=headers)
    assert list_response.status_code == 200
    assert [item["name"] for item in list_response.json()] == ["Goblet Squat"]

    detail_response = client.get(f"/api/v1/exercises/{exercise.id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["easier_variation_notes"] == "Use bodyweight or squat to a box."


def test_programs_active_and_workout_day_detail(client: TestClient, db_session: Session) -> None:
    headers = auth_headers(client)
    user = get_user(db_session)
    _, program, workout_day = create_program_fixture(db_session, user)

    programs_response = client.get("/api/v1/programs", headers=headers)
    assert programs_response.status_code == 200
    assert programs_response.json()[0]["id"] == str(program.id)
    assert programs_response.json()[0]["workout_days"][0]["workout_exercises"][0]["exercise"]["name"] == "Goblet Squat"

    active_response = client.get("/api/v1/programs/active", headers=headers)
    assert active_response.status_code == 200
    assert active_response.json()["name"] == "Test Home Plan"

    day_response = client.get(f"/api/v1/workout-days/{workout_day.id}", headers=headers)
    assert day_response.status_code == 200
    assert day_response.json()["title"] == "Monday Lower"


def test_workout_log_create_list_detail_with_date_filter(client: TestClient, db_session: Session) -> None:
    headers = auth_headers(client)
    user = get_user(db_session)
    exercise, _, workout_day = create_program_fixture(db_session, user)

    started_at = "2026-06-01T08:00:00Z"
    create_response = client.post(
        "/api/v1/workout-logs",
        headers=headers,
        json={
            "workout_day_id": str(workout_day.id),
            "started_at": started_at,
            "completed_at": "2026-06-01T09:00:00Z",
            "notes": "Solid session",
            "set_logs": [
                {
                    "exercise_id": str(exercise.id),
                    "set_index": 1,
                    "weight_kg": "20.00",
                    "reps": 10,
                    "rpe": "8.0",
                }
            ],
        },
    )
    assert create_response.status_code == 201
    log_id = create_response.json()["id"]
    assert create_response.json()["set_logs"][0]["reps"] == 10

    list_response = client.get("/api/v1/workout-logs?date_from=2026-06-01&date_to=2026-06-01", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    empty_response = client.get("/api/v1/workout-logs?date_from=2026-06-02", headers=headers)
    assert empty_response.status_code == 200
    assert empty_response.json() == []

    detail_response = client.get(f"/api/v1/workout-logs/{log_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["notes"] == "Solid session"


def test_body_metrics_create_list_with_date_filter(client: TestClient) -> None:
    headers = auth_headers(client, email="metrics@example.com")

    create_response = client.post(
        "/api/v1/body-metrics",
        headers=headers,
        json={
            "date": "2026-06-01",
            "weight_kg": "115.00",
            "waist_cm": "110.00",
            "steps": 8000,
            "protein_g": "160.0",
            "calories": 2300,
            "nutrition_note": "Meal prep day",
            "sleep_hours": "7.5",
            "mood": "good",
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["user_id"]
    assert create_response.json()["nutrition_note"] == "Meal prep day"

    update_response = client.post(
        "/api/v1/body-metrics",
        headers=headers,
        json={"date": "2026-06-01", "weight_kg": "114.50"},
    )
    assert update_response.status_code == 201
    assert update_response.json()["id"] == create_response.json()["id"]
    assert update_response.json()["weight_kg"] == "114.50"
    assert update_response.json()["nutrition_note"] == "Meal prep day"

    list_response = client.get("/api/v1/body-metrics?date_from=2026-06-01&date_to=2026-06-01", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    empty_response = client.get("/api/v1/body-metrics?date_from=2026-06-02", headers=headers)
    assert empty_response.status_code == 200
    assert empty_response.json() == []


def test_daily_nutrition_log_upserts_body_metric_without_losing_body_data(client: TestClient) -> None:
    headers = auth_headers(client, email="nutrition@example.com")

    metric_response = client.post(
        "/api/v1/body-metrics",
        headers=headers,
        json={
            "date": "2026-06-03",
            "weight_kg": "114.50",
            "waist_cm": "109.00",
            "steps": 7500,
        },
    )
    assert metric_response.status_code == 201

    nutrition_response = client.post(
        "/api/v1/nutrition/daily",
        headers=headers,
        json={
            "date": "2026-06-03",
            "protein_g": "175.0",
            "calories": 2400,
            "nutrition_note": "Hit protein target",
        },
    )
    assert nutrition_response.status_code == 200
    nutrition = nutrition_response.json()
    assert nutrition["weight_kg"] == "114.50"
    assert nutrition["protein_g"] == "175.0"
    assert nutrition["calories"] == 2400
    assert nutrition["nutrition_note"] == "Hit protein target"

    updated_response = client.post(
        "/api/v1/nutrition/daily",
        headers=headers,
        json={
            "date": "2026-06-03",
            "protein_g": "180.0",
            "calories": 2300,
            "nutrition_note": None,
        },
    )
    assert updated_response.status_code == 200
    assert updated_response.json()["id"] == nutrition["id"]
    assert updated_response.json()["protein_g"] == "180.0"
    assert updated_response.json()["nutrition_note"] is None


def test_profile_update_saves_nutrition_targets(client: TestClient) -> None:
    headers = auth_headers(client, email="targets@example.com")

    response = client.put(
        "/api/v1/me/profile",
        headers=headers,
        json={
            "preferred_mode": "home",
            "target_protein_g": "180.0",
            "target_calories": 2300,
        },
    )

    assert response.status_code == 200
    profile = response.json()
    assert profile["target_protein_g"] == "180.0"
    assert profile["target_calories"] == 2300


def test_exercise_override_flow(client: TestClient, db_session: Session) -> None:
    headers = auth_headers(client, email="override@example.com")
    user = get_user(db_session, email="override@example.com")
    exercise, _, workout_day = create_program_fixture(db_session, user)
    alternative = Exercise(
        name="Box Squat",
        primary_muscle="quads",
        secondary_muscles=["glutes"],
        equipment=["bodyweight", "box or chair"],
        difficulty="beginner",
        instructions="Squat to a stable box.",
        easier_variation_notes="Use a higher box.",
        alternative_exercise_ids=[],
    )
    invalid_exercise = Exercise(
        name="Hammer Curl",
        primary_muscle="biceps",
        secondary_muscles=["forearms"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Curl with neutral grip.",
        easier_variation_notes="Use lighter dumbbells.",
        alternative_exercise_ids=[],
    )
    db_session.add_all([alternative, invalid_exercise])
    db_session.flush()
    exercise.alternative_exercise_ids = [str(alternative.id)]
    db_session.commit()
    workout_exercise = workout_day.workout_exercises[0]

    invalid_response = client.put(
        f"/api/v1/exercise-overrides/{workout_exercise.id}",
        headers=headers,
        json={"exercise_id": str(invalid_exercise.id)},
    )
    assert invalid_response.status_code == 400

    save_response = client.put(
        f"/api/v1/exercise-overrides/{workout_exercise.id}",
        headers=headers,
        json={"exercise_id": str(alternative.id)},
    )
    assert save_response.status_code == 200
    assert save_response.json()["exercise"]["name"] == "Box Squat"

    list_response = client.get("/api/v1/exercise-overrides", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/api/v1/exercises/{exercise.id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["alternatives"][0]["name"] == "Box Squat"
