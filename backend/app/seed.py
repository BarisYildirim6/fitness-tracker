from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.constants import DEMO_USER_EMAIL, DEMO_USER_PASSWORD, SEED_PROGRAM_NAME, SEED_USER_EMAIL
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.body_metric import BodyMetric
from app.models.exercise import Exercise
from app.models.program import Program, WorkoutDay
from app.models.user import User, UserProfile
from app.models.workout import SetLog, WorkoutExercise, WorkoutLog


@dataclass(frozen=True)
class ExerciseSeed:
    name: str
    primary_muscle: str
    equipment: list[str]
    difficulty: str
    instructions: str
    alternatives: list[str]
    easier_variation_notes: str
    secondary_muscles: list[str] | None = None


@dataclass(frozen=True)
class WorkoutExerciseSeed:
    exercise_name: str
    sets: int
    rep_min: int
    rep_max: int
    rest_seconds: int | None = 90
    tempo: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class WorkoutDaySeed:
    day_of_week: int
    title: str
    focus: str
    exercises: list[WorkoutExerciseSeed]


EXERCISES: list[ExerciseSeed] = [
    ExerciseSeed(
        name="Dumbbell Floor Press",
        primary_muscle="chest",
        secondary_muscles=["triceps", "front delts"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Lie on the floor, brace your core, press dumbbells from elbows-on-floor to locked out, then lower under control.",
        alternatives=["Bench Press", "Push-up"],
        easier_variation_notes="Use lighter dumbbells or perform a push-up from an elevated surface.",
    ),
    ExerciseSeed(
        name="Bench Press",
        primary_muscle="chest",
        secondary_muscles=["triceps", "front delts"],
        equipment=["barbell", "bench"],
        difficulty="intermediate",
        instructions="Set shoulder blades, lower the bar to the lower chest, and press up while keeping feet planted.",
        alternatives=["Dumbbell Floor Press", "Push-up"],
        easier_variation_notes="Use dumbbells, reduce load, or shorten range with floor press.",
    ),
    ExerciseSeed(
        name="Push-up",
        primary_muscle="chest",
        secondary_muscles=["triceps", "core"],
        equipment=["bodyweight"],
        difficulty="beginner",
        instructions="Keep a straight line from shoulders to ankles, lower chest toward the floor, then press back up.",
        alternatives=["Dumbbell Floor Press", "Bench Press"],
        easier_variation_notes="Use an incline surface or perform knee push-ups.",
    ),
    ExerciseSeed(
        name="One-arm Dumbbell Row",
        primary_muscle="back",
        secondary_muscles=["biceps", "rear delts"],
        equipment=["adjustable dumbbell"],
        difficulty="beginner",
        instructions="Brace one hand on a stable surface, row the dumbbell toward your hip, and lower with control.",
        alternatives=["Bent-over Dumbbell Row", "Dumbbell Pullover"],
        easier_variation_notes="Use a lighter dumbbell and support your torso with a bench or chair.",
    ),
    ExerciseSeed(
        name="Bent-over Dumbbell Row",
        primary_muscle="back",
        secondary_muscles=["biceps", "rear delts"],
        equipment=["adjustable dumbbells"],
        difficulty="intermediate",
        instructions="Hinge at the hips, keep a neutral back, row both dumbbells toward the ribs, then lower under control.",
        alternatives=["One-arm Dumbbell Row", "Dumbbell Pullover"],
        easier_variation_notes="Row one arm at a time with support from a chair or bench.",
    ),
    ExerciseSeed(
        name="Dumbbell Pullover",
        primary_muscle="lats",
        secondary_muscles=["chest", "serratus"],
        equipment=["adjustable dumbbell", "bench or floor"],
        difficulty="beginner",
        instructions="Hold one dumbbell over the chest, lower it behind the head with soft elbows, then pull back over the chest.",
        alternatives=["One-arm Dumbbell Row", "Bent-over Dumbbell Row"],
        easier_variation_notes="Use a lighter dumbbell and limit the overhead range.",
    ),
    ExerciseSeed(
        name="Standing Dumbbell Shoulder Press",
        primary_muscle="shoulders",
        secondary_muscles=["triceps", "core"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Brace your core, press dumbbells from shoulder height overhead, then lower without leaning back.",
        alternatives=["Arnold Press", "Pike Push-up"],
        easier_variation_notes="Press seated or use one dumbbell at a time.",
    ),
    ExerciseSeed(
        name="Arnold Press",
        primary_muscle="shoulders",
        secondary_muscles=["triceps", "front delts"],
        equipment=["adjustable dumbbells"],
        difficulty="intermediate",
        instructions="Start palms facing you, rotate as you press overhead, then reverse the motion down.",
        alternatives=["Standing Dumbbell Shoulder Press", "Pike Push-up"],
        easier_variation_notes="Use a lighter load or perform a standard seated dumbbell press.",
    ),
    ExerciseSeed(
        name="Pike Push-up",
        primary_muscle="shoulders",
        secondary_muscles=["triceps", "core"],
        equipment=["bodyweight"],
        difficulty="intermediate",
        instructions="Set hips high, lower the crown of the head toward the floor, then press back up.",
        alternatives=["Standing Dumbbell Shoulder Press", "Arnold Press"],
        easier_variation_notes="Place hands on an elevated surface and reduce the range of motion.",
    ),
    ExerciseSeed(
        name="Dumbbell Lateral Raise",
        primary_muscle="side delts",
        secondary_muscles=["upper traps"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Raise dumbbells out to the sides with soft elbows until shoulder height, then lower slowly.",
        alternatives=["Rear Delt Raise", "Arnold Press"],
        easier_variation_notes="Use lighter plates or raise one arm at a time.",
    ),
    ExerciseSeed(
        name="Rear Delt Raise",
        primary_muscle="rear delts",
        secondary_muscles=["upper back"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Hinge at the hips and raise dumbbells out wide while keeping the neck relaxed.",
        alternatives=["Dumbbell Lateral Raise", "Bent-over Dumbbell Row"],
        easier_variation_notes="Use lighter dumbbells and pause with hands supported between reps.",
    ),
    ExerciseSeed(
        name="Barbell/Dumbbell Curl",
        primary_muscle="biceps",
        secondary_muscles=["forearms"],
        equipment=["dumbbells", "barbell"],
        difficulty="beginner",
        instructions="Keep elbows near your sides, curl without swinging, then lower through a full controlled range.",
        alternatives=["Hammer Curl", "Resistance Band Curl"],
        easier_variation_notes="Use lighter dumbbells or alternate arms.",
    ),
    ExerciseSeed(
        name="Hammer Curl",
        primary_muscle="biceps",
        secondary_muscles=["brachialis", "forearms"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Curl dumbbells with palms facing each other and keep the upper arm still.",
        alternatives=["Barbell/Dumbbell Curl", "Resistance Band Curl"],
        easier_variation_notes="Use lighter dumbbells or perform seated alternating reps.",
    ),
    ExerciseSeed(
        name="Resistance Band Curl",
        primary_muscle="biceps",
        secondary_muscles=["forearms"],
        equipment=["resistance band"],
        difficulty="beginner",
        instructions="Stand on the band and curl handles toward shoulders while keeping elbows pinned.",
        alternatives=["Barbell/Dumbbell Curl", "Hammer Curl"],
        easier_variation_notes="Stand with less band tension or use one arm at a time.",
    ),
    ExerciseSeed(
        name="Overhead Dumbbell Triceps Extension",
        primary_muscle="triceps",
        secondary_muscles=["shoulders"],
        equipment=["adjustable dumbbell"],
        difficulty="beginner",
        instructions="Hold one dumbbell overhead, lower behind the head with elbows tucked, then extend fully.",
        alternatives=["Dumbbell Skull Crusher", "Close-grip Push-up"],
        easier_variation_notes="Use one lighter dumbbell or perform the movement seated.",
    ),
    ExerciseSeed(
        name="Dumbbell Skull Crusher",
        primary_muscle="triceps",
        secondary_muscles=["shoulders"],
        equipment=["adjustable dumbbells", "floor or bench"],
        difficulty="beginner",
        instructions="Lie down, keep elbows pointed up, lower dumbbells near the ears, then extend the elbows.",
        alternatives=["Overhead Dumbbell Triceps Extension", "Close-grip Push-up"],
        easier_variation_notes="Use lighter dumbbells and perform from the floor to limit range.",
    ),
    ExerciseSeed(
        name="Close-grip Push-up",
        primary_muscle="triceps",
        secondary_muscles=["chest", "core"],
        equipment=["bodyweight"],
        difficulty="intermediate",
        instructions="Use a narrow hand position, keep elbows close, lower under control, then press up.",
        alternatives=["Overhead Dumbbell Triceps Extension", "Dumbbell Skull Crusher"],
        easier_variation_notes="Use an incline surface or perform knee close-grip push-ups.",
    ),
    ExerciseSeed(
        name="Goblet Squat",
        primary_muscle="quads",
        secondary_muscles=["glutes", "core"],
        equipment=["adjustable dumbbell"],
        difficulty="beginner",
        instructions="Hold a dumbbell at chest height, squat between the knees, keep heels planted, then stand tall.",
        alternatives=["Dumbbell Front Squat", "Box Squat"],
        easier_variation_notes="Squat to a box or use bodyweight only.",
    ),
    ExerciseSeed(
        name="Dumbbell Front Squat",
        primary_muscle="quads",
        secondary_muscles=["glutes", "core"],
        equipment=["adjustable dumbbells"],
        difficulty="intermediate",
        instructions="Hold dumbbells at shoulders, brace, squat down with an upright torso, then drive up.",
        alternatives=["Goblet Squat", "Box Squat"],
        easier_variation_notes="Use a single goblet dumbbell or reduce depth.",
    ),
    ExerciseSeed(
        name="Box Squat",
        primary_muscle="quads",
        secondary_muscles=["glutes"],
        equipment=["bodyweight", "box or chair"],
        difficulty="beginner",
        instructions="Sit back to a stable box or chair, lightly touch, then stand without rocking.",
        alternatives=["Goblet Squat", "Dumbbell Front Squat"],
        easier_variation_notes="Use a higher box or bodyweight only.",
    ),
    ExerciseSeed(
        name="Dumbbell Romanian Deadlift",
        primary_muscle="hamstrings",
        secondary_muscles=["glutes", "lower back"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Hinge at the hips with soft knees, lower dumbbells along the legs, then squeeze glutes to stand.",
        alternatives=["Single-leg Romanian Deadlift", "Glute Bridge"],
        easier_variation_notes="Use lighter dumbbells and reduce range to knee height.",
    ),
    ExerciseSeed(
        name="Single-leg Romanian Deadlift",
        primary_muscle="hamstrings",
        secondary_muscles=["glutes", "balance"],
        equipment=["adjustable dumbbell"],
        difficulty="intermediate",
        instructions="Hold a dumbbell, hinge on one leg, keep hips square, then stand with control.",
        alternatives=["Dumbbell Romanian Deadlift", "Glute Bridge"],
        easier_variation_notes="Use a kickstand stance or hold a wall for support.",
    ),
    ExerciseSeed(
        name="Bulgarian Split Squat",
        primary_muscle="quads",
        secondary_muscles=["glutes", "hamstrings"],
        equipment=["adjustable dumbbells", "bench or chair"],
        difficulty="intermediate",
        instructions="Place rear foot on a bench or chair, lower the back knee, then drive through the front foot.",
        alternatives=["Dumbbell Reverse Lunge", "Split Squat"],
        easier_variation_notes="Do a regular split squat with both feet on the floor.",
    ),
    ExerciseSeed(
        name="Dumbbell Reverse Lunge",
        primary_muscle="quads",
        secondary_muscles=["glutes", "hamstrings"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Step backward, lower under control, then push through the front foot to return.",
        alternatives=["Bulgarian Split Squat", "Split Squat"],
        easier_variation_notes="Use bodyweight only or hold one dumbbell goblet-style.",
    ),
    ExerciseSeed(
        name="Split Squat",
        primary_muscle="quads",
        secondary_muscles=["glutes"],
        equipment=["bodyweight", "dumbbells optional"],
        difficulty="beginner",
        instructions="Use a staggered stance, lower straight down, then press through the front foot.",
        alternatives=["Bulgarian Split Squat", "Dumbbell Reverse Lunge"],
        easier_variation_notes="Use bodyweight and hold a wall for balance.",
    ),
    ExerciseSeed(
        name="Standing Calf Raise",
        primary_muscle="calves",
        secondary_muscles=["ankles"],
        equipment=["bodyweight", "dumbbells optional"],
        difficulty="beginner",
        instructions="Rise onto the balls of the feet, pause, then lower heels slowly.",
        alternatives=["Single-leg Calf Raise", "Seated Calf Raise"],
        easier_variation_notes="Use both legs with bodyweight and hold a wall for support.",
    ),
    ExerciseSeed(
        name="Single-leg Calf Raise",
        primary_muscle="calves",
        secondary_muscles=["ankles"],
        equipment=["bodyweight"],
        difficulty="intermediate",
        instructions="Stand on one leg, rise onto the ball of the foot, pause, then lower slowly.",
        alternatives=["Standing Calf Raise", "Seated Calf Raise"],
        easier_variation_notes="Use both legs or assist with the non-working foot.",
    ),
    ExerciseSeed(
        name="Seated Calf Raise",
        primary_muscle="calves",
        secondary_muscles=["ankles"],
        equipment=["dumbbell", "chair"],
        difficulty="beginner",
        instructions="Sit with a dumbbell on the knees, raise heels, pause, then lower.",
        alternatives=["Standing Calf Raise", "Single-leg Calf Raise"],
        easier_variation_notes="Use no added load and focus on full range.",
    ),
    ExerciseSeed(
        name="Plank",
        primary_muscle="core",
        secondary_muscles=["shoulders", "glutes"],
        equipment=["bodyweight"],
        difficulty="beginner",
        instructions="Brace on elbows and toes, keep ribs down and body straight, and breathe steadily.",
        alternatives=["Side Plank", "Dead Bug"],
        easier_variation_notes="Perform from the knees or use shorter holds.",
    ),
    ExerciseSeed(
        name="Side Plank",
        primary_muscle="obliques",
        secondary_muscles=["core", "shoulders"],
        equipment=["bodyweight"],
        difficulty="beginner",
        instructions="Stack feet or stagger them, brace on one elbow, and hold hips off the floor.",
        alternatives=["Plank", "Russian Twist"],
        easier_variation_notes="Bend the bottom knee and hold for shorter intervals.",
    ),
    ExerciseSeed(
        name="Dead Bug / Leg Raise",
        primary_muscle="core",
        secondary_muscles=["hip flexors"],
        equipment=["bodyweight"],
        difficulty="beginner",
        instructions="Keep the low back controlled while alternating dead bug reps or lowering legs with control.",
        alternatives=["Plank", "Russian Twist"],
        easier_variation_notes="Use dead bugs before progressing to leg raises.",
    ),
    ExerciseSeed(
        name="Russian Twist",
        primary_muscle="obliques",
        secondary_muscles=["core"],
        equipment=["bodyweight", "dumbbell optional"],
        difficulty="beginner",
        instructions="Sit tall, brace, rotate the torso side to side without yanking the neck.",
        alternatives=["Side Plank", "Dead Bug / Leg Raise"],
        easier_variation_notes="Keep heels on the floor and use no weight.",
    ),
    ExerciseSeed(
        name="Brisk Walk",
        primary_muscle="cardio",
        secondary_muscles=["legs"],
        equipment=["walking shoes"],
        difficulty="beginner",
        instructions="Walk at a pace that raises breathing while still allowing short conversation.",
        alternatives=["Long Walk", "Dumbbell Conditioning Circuit"],
        easier_variation_notes="Reduce duration or split the walk into shorter sessions.",
    ),
    ExerciseSeed(
        name="Mobility",
        primary_muscle="mobility",
        secondary_muscles=["hips", "shoulders", "spine"],
        equipment=["bodyweight"],
        difficulty="beginner",
        instructions="Move slowly through hip, thoracic spine, shoulder, and ankle ranges without forcing end positions.",
        alternatives=["Brisk Walk", "Long Walk"],
        easier_variation_notes="Use shorter ranges and spend more time in comfortable positions.",
    ),
    ExerciseSeed(
        name="Dumbbell Hip Thrust / Glute Bridge",
        primary_muscle="glutes",
        secondary_muscles=["hamstrings", "core"],
        equipment=["adjustable dumbbell", "floor or bench"],
        difficulty="beginner",
        instructions="Place weight over the hips, drive through heels, squeeze glutes at the top, then lower under control.",
        alternatives=["Glute Bridge", "Dumbbell Romanian Deadlift"],
        easier_variation_notes="Start with bodyweight glute bridges on the floor.",
    ),
    ExerciseSeed(
        name="Glute Bridge",
        primary_muscle="glutes",
        secondary_muscles=["hamstrings"],
        equipment=["bodyweight"],
        difficulty="beginner",
        instructions="Lie on your back, drive through heels, lift hips, pause, then lower.",
        alternatives=["Dumbbell Hip Thrust / Glute Bridge", "Dumbbell Romanian Deadlift"],
        easier_variation_notes="Use a smaller range and pause between reps.",
    ),
    ExerciseSeed(
        name="Suitcase Carry",
        primary_muscle="core",
        secondary_muscles=["grip", "traps"],
        equipment=["adjustable dumbbell"],
        difficulty="beginner",
        instructions="Hold one dumbbell at your side, walk tall without leaning, then switch hands.",
        alternatives=["Farmer Carry", "Side Plank"],
        easier_variation_notes="Use a lighter dumbbell or shorter walking distance.",
    ),
    ExerciseSeed(
        name="Farmer Carry",
        primary_muscle="grip",
        secondary_muscles=["core", "traps"],
        equipment=["adjustable dumbbells"],
        difficulty="beginner",
        instructions="Hold dumbbells at both sides and walk with tall posture and controlled steps.",
        alternatives=["Suitcase Carry", "Side Plank"],
        easier_variation_notes="Use lighter dumbbells or timed holds instead of walking.",
    ),
    ExerciseSeed(
        name="Long Walk",
        primary_muscle="cardio",
        secondary_muscles=["legs"],
        equipment=["walking shoes"],
        difficulty="beginner",
        instructions="Walk at an easy sustainable pace for a longer duration to build recovery and calorie expenditure.",
        alternatives=["Brisk Walk", "Dumbbell Conditioning Circuit"],
        easier_variation_notes="Shorten the walk or keep the route flat.",
    ),
    ExerciseSeed(
        name="Dumbbell Conditioning Circuit",
        primary_muscle="conditioning",
        secondary_muscles=["full body"],
        equipment=["adjustable dumbbells"],
        difficulty="intermediate",
        instructions="Rotate through light goblet squats, rows, presses, and carries with controlled technique and short rests.",
        alternatives=["Long Walk", "Brisk Walk"],
        easier_variation_notes="Use lighter dumbbells, fewer rounds, and longer rest periods.",
    ),
]


WORKOUT_DAYS: list[WorkoutDaySeed] = [
    WorkoutDaySeed(
        day_of_week=1,
        title="Monday Upper A",
        focus="Upper body strength and hypertrophy",
        exercises=[
            WorkoutExerciseSeed("Dumbbell Floor Press", 3, 8, 12),
            WorkoutExerciseSeed("One-arm Dumbbell Row", 3, 8, 12),
            WorkoutExerciseSeed("Standing Dumbbell Shoulder Press", 3, 8, 10),
            WorkoutExerciseSeed("Dumbbell Lateral Raise", 3, 12, 20, 60),
            WorkoutExerciseSeed("Barbell/Dumbbell Curl", 3, 10, 15, 60),
            WorkoutExerciseSeed("Overhead Dumbbell Triceps Extension", 3, 10, 15, 60),
        ],
    ),
    WorkoutDaySeed(
        day_of_week=2,
        title="Tuesday Lower A + Core",
        focus="Lower body and core",
        exercises=[
            WorkoutExerciseSeed("Goblet Squat", 3, 8, 12),
            WorkoutExerciseSeed("Dumbbell Romanian Deadlift", 3, 8, 12),
            WorkoutExerciseSeed("Bulgarian Split Squat", 3, 8, 10),
            WorkoutExerciseSeed("Standing Calf Raise", 3, 12, 20, 60),
            WorkoutExerciseSeed("Plank", 3, 30, 60, 45, notes="Reps represent seconds held."),
            WorkoutExerciseSeed("Dead Bug / Leg Raise", 3, 8, 12, 45),
        ],
    ),
    WorkoutDaySeed(
        day_of_week=3,
        title="Wednesday Recovery",
        focus="Recovery and mobility",
        exercises=[
            WorkoutExerciseSeed("Brisk Walk", 1, 20, 40, None, notes="Reps represent minutes walked."),
            WorkoutExerciseSeed("Mobility", 1, 10, 20, None, notes="Reps represent minutes of mobility work."),
        ],
    ),
    WorkoutDaySeed(
        day_of_week=4,
        title="Thursday Upper B",
        focus="Upper body variation",
        exercises=[
            WorkoutExerciseSeed("Push-up", 3, 8, 15),
            WorkoutExerciseSeed("Dumbbell Pullover", 3, 10, 15),
            WorkoutExerciseSeed("Bent-over Dumbbell Row", 3, 8, 12),
            WorkoutExerciseSeed("Arnold Press", 3, 8, 12),
            WorkoutExerciseSeed("Hammer Curl", 3, 10, 15, 60),
            WorkoutExerciseSeed("Dumbbell Skull Crusher", 3, 10, 15, 60),
            WorkoutExerciseSeed("Rear Delt Raise", 3, 12, 20, 60),
        ],
    ),
    WorkoutDaySeed(
        day_of_week=5,
        title="Friday Lower B + Core",
        focus="Lower body variation and loaded core",
        exercises=[
            WorkoutExerciseSeed("Dumbbell Front Squat", 3, 8, 12),
            WorkoutExerciseSeed("Dumbbell Reverse Lunge", 3, 8, 12),
            WorkoutExerciseSeed("Single-leg Romanian Deadlift", 3, 8, 10),
            WorkoutExerciseSeed("Dumbbell Hip Thrust / Glute Bridge", 3, 10, 15),
            WorkoutExerciseSeed("Suitcase Carry", 3, 20, 40, 60, notes="Reps represent meters or seconds per side."),
            WorkoutExerciseSeed("Side Plank", 3, 20, 45, 45, notes="Reps represent seconds held per side."),
            WorkoutExerciseSeed("Russian Twist", 3, 12, 20, 45),
        ],
    ),
    WorkoutDaySeed(
        day_of_week=6,
        title="Saturday Cardio/Conditioning",
        focus="Long walk or light conditioning",
        exercises=[
            WorkoutExerciseSeed("Long Walk", 1, 30, 60, None, notes="Reps represent minutes walked."),
            WorkoutExerciseSeed("Dumbbell Conditioning Circuit", 3, 6, 10, 90, notes="Optional circuit if recovery is good."),
        ],
    ),
    WorkoutDaySeed(day_of_week=7, title="Sunday Rest", focus="Rest", exercises=[]),
]


def get_or_create_seed_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == SEED_USER_EMAIL))
    if user is not None:
        return user

    user = User(
        email=SEED_USER_EMAIL,
        hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        is_active=False,
    )
    user.profile = UserProfile(
        height_cm=184,
        current_weight_kg=115,
        goal="fat loss, muscle volume, strength, and sustainable weekly tracking",
        training_level="beginner",
        preferred_mode="home",
        target_weekly_weight_loss_kg=0.5,
    )
    db.add(user)
    db.flush()
    return user


def upsert_exercises(db: Session) -> dict[str, Exercise]:
    exercises_by_name = {exercise.name: exercise for exercise in db.scalars(select(Exercise)).all()}

    for seed in EXERCISES:
        exercise = exercises_by_name.get(seed.name)
        if exercise is None:
            exercise = Exercise(name=seed.name)
            db.add(exercise)
            exercises_by_name[seed.name] = exercise

        exercise.primary_muscle = seed.primary_muscle
        exercise.secondary_muscles = seed.secondary_muscles or []
        exercise.equipment = seed.equipment
        exercise.difficulty = seed.difficulty
        exercise.instructions = seed.instructions
        exercise.easier_variation_notes = seed.easier_variation_notes

    db.flush()

    for seed in EXERCISES:
        exercise = exercises_by_name[seed.name]
        exercise.alternative_exercise_ids = [
            str(exercises_by_name[alternative_name].id)
            for alternative_name in seed.alternatives
            if alternative_name in exercises_by_name
        ]

    db.flush()
    return exercises_by_name


def upsert_program(db: Session, user: User, exercises_by_name: dict[str, Exercise]) -> Program:
    program = db.scalar(select(Program).where(Program.user_id == user.id, Program.name == SEED_PROGRAM_NAME))
    if program is None:
        program = Program(user_id=user.id, name=SEED_PROGRAM_NAME)
        db.add(program)
        db.flush()

    program.description = "Default home training week seeded from AGENTS.md."
    program.is_active = True

    existing_days = {day.day_of_week: day for day in program.workout_days}

    for day_seed in WORKOUT_DAYS:
        workout_day = existing_days.get(day_seed.day_of_week)
        if workout_day is None:
            workout_day = WorkoutDay(program_id=program.id, day_of_week=day_seed.day_of_week)
            db.add(workout_day)

        workout_day.title = day_seed.title
        workout_day.focus = day_seed.focus
        db.flush()
        upsert_workout_exercises(db, workout_day, day_seed.exercises, exercises_by_name)

    db.flush()
    return program


def upsert_workout_exercises(
    db: Session,
    workout_day: WorkoutDay,
    exercise_seeds: list[WorkoutExerciseSeed],
    exercises_by_name: dict[str, Exercise],
) -> None:
    existing_by_order = {workout_exercise.order_index: workout_exercise for workout_exercise in workout_day.workout_exercises}
    expected_orders = set(range(len(exercise_seeds)))

    for workout_exercise in list(workout_day.workout_exercises):
        if workout_exercise.order_index not in expected_orders:
            db.delete(workout_exercise)

    for order_index, seed in enumerate(exercise_seeds):
        workout_exercise = existing_by_order.get(order_index)
        if workout_exercise is None:
            workout_exercise = WorkoutExercise(workout_day_id=workout_day.id, order_index=order_index)
            db.add(workout_exercise)

        workout_exercise.exercise_id = exercises_by_name[seed.exercise_name].id
        workout_exercise.sets = seed.sets
        workout_exercise.rep_min = seed.rep_min
        workout_exercise.rep_max = seed.rep_max
        workout_exercise.rest_seconds = seed.rest_seconds
        workout_exercise.tempo = seed.tempo
        workout_exercise.notes = seed.notes


def get_or_create_demo_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == DEMO_USER_EMAIL))
    if user is None:
        user = User(
            email=DEMO_USER_EMAIL,
            hashed_password=get_password_hash(DEMO_USER_PASSWORD),
            is_active=True,
        )
        db.add(user)
        db.flush()

    user.is_active = True
    if user.profile is None:
        user.profile = UserProfile(user_id=user.id)

    user.profile.height_cm = Decimal("184.00")
    user.profile.current_weight_kg = Decimal("115.00")
    user.profile.goal = "fat loss, strength, and sustainable weekly tracking"
    user.profile.training_level = "beginner"
    user.profile.preferred_mode = "home"
    user.profile.target_weekly_weight_loss_kg = Decimal("0.50")
    user.profile.target_protein_g = Decimal("180.0")
    user.profile.target_calories = 2300
    db.flush()
    return user


def upsert_demo_metrics(db: Session, user: User) -> None:
    today = date.today()
    sample_dates = {today - timedelta(days=days_ago) for days_ago in range(14)}
    metrics = [
        (13, "115.80", "111.20", 6200, "152.0", 2480, "6.4", "starting point"),
        (12, "115.70", "111.00", 7100, "165.0", 2360, "7.1", "solid meals"),
        (11, "115.30", "110.80", 6800, "174.0", 2290, "6.8", "late walk"),
        (10, "115.10", "110.60", 8400, "181.0", 2310, "7.4", "good rhythm"),
        (9, "114.90", "110.60", 9100, "176.0", 2260, "7.0", "meal prep"),
        (8, "114.70", "110.40", 7600, "168.0", 2380, "6.6", "busy day"),
        (7, "114.40", "110.30", 8800, "185.0", 2240, "7.5", "hit protein"),
        (6, "114.50", "110.10", 9300, "178.0", 2320, "7.2", "steady"),
        (5, "114.20", "110.00", 10500, "182.0", 2280, "7.7", "long walk"),
        (4, "114.10", "109.80", 7900, "170.0", 2350, "6.9", "normal day"),
        (3, "113.90", "109.70", 8600, "188.0", 2250, "7.3", "good session"),
        (2, "113.80", "109.50", 9900, "179.0", 2300, "7.0", "consistent"),
        (1, "113.60", "109.40", 7200, "172.0", 2370, "6.7", "recovery"),
        (0, "113.50", "109.20", 8400, "183.0", 2290, "7.4", "on target"),
    ]

    existing_metrics = {
        metric.date: metric
        for metric in db.scalars(select(BodyMetric).where(BodyMetric.user_id == user.id)).all()
    }
    for metric_date, metric in existing_metrics.items():
        if metric_date not in sample_dates and metric.nutrition_note in {
            "starting point",
            "solid meals",
            "late walk",
            "good rhythm",
            "meal prep",
            "busy day",
            "hit protein",
            "steady",
            "long walk",
            "normal day",
            "good session",
            "consistent",
            "recovery",
            "on target",
        }:
            db.delete(metric)

    for days_ago, weight, waist, steps, protein, calories, sleep, note in metrics:
        metric_date = today - timedelta(days=days_ago)
        metric = existing_metrics.get(metric_date)
        if metric is None:
            metric = BodyMetric(user_id=user.id, date=metric_date)
            db.add(metric)

        metric.weight_kg = Decimal(weight)
        metric.waist_cm = Decimal(waist)
        metric.steps = steps
        metric.protein_g = Decimal(protein)
        metric.calories = calories
        metric.nutrition_note = note
        metric.sleep_hours = Decimal(sleep)
        metric.mood = "good" if days_ago % 3 != 1 else "okay"


def upsert_demo_workout_logs(db: Session, user: User, program: Program) -> None:
    today = date.today()
    workout_days = db.scalars(
        select(WorkoutDay)
        .where(WorkoutDay.program_id == program.id)
        .order_by(WorkoutDay.day_of_week)
    )
    training_days = [day for day in workout_days if day.workout_exercises]
    if not training_days:
        return

    existing_logs = {
        log.started_at: log
        for log in db.scalars(select(WorkoutLog).where(WorkoutLog.user_id == user.id)).all()
    }
    sample_days = [training_days[0], training_days[1], training_days[3], training_days[4]]
    sample_starts = {
        datetime.combine(today - timedelta(days=6 - index * 2), time(hour=18, minute=30), tzinfo=UTC)
        for index in range(len(sample_days))
    }

    for log in list(existing_logs.values()):
        if log.notes and log.notes.startswith("Demo log:") and log.started_at not in sample_starts:
            db.delete(log)

    for index, workout_day in enumerate(sample_days):
        log_date = today - timedelta(days=6 - index * 2)
        started_at = datetime.combine(log_date, time(hour=18, minute=30), tzinfo=UTC)
        completed_at = started_at + timedelta(minutes=48)
        log = existing_logs.get(started_at)
        if log is None:
            log = WorkoutLog(user_id=user.id, started_at=started_at)
            db.add(log)
            db.flush()

        log.workout_day_id = workout_day.id
        log.completed_at = completed_at
        log.notes = f"Demo log: {workout_day.title}"

        for set_log in list(log.set_logs):
            db.delete(set_log)
        db.flush()

        for exercise_index, workout_exercise in enumerate(workout_day.workout_exercises[:3]):
            for set_index in range(1, min(workout_exercise.sets, 3) + 1):
                db.add(
                    SetLog(
                        workout_log_id=log.id,
                        exercise_id=workout_exercise.exercise_id,
                        set_index=set_index,
                        reps=workout_exercise.rep_min + min(set_index, 2),
                        weight_kg=Decimal(12 + exercise_index * 4 + index * 2),
                        rpe=Decimal("7.5") if set_index < 3 else Decimal("8.0"),
                    )
                )


def seed_database() -> None:
    with SessionLocal() as db:
        seed_user = get_or_create_seed_user(db)
        exercises_by_name = upsert_exercises(db)
        program = upsert_program(db, seed_user, exercises_by_name)
        demo_user = get_or_create_demo_user(db)
        upsert_demo_metrics(db, demo_user)
        upsert_demo_workout_logs(db, demo_user, program)
        db.commit()

        workout_day_count = db.scalar(select(func.count()).select_from(WorkoutDay).where(WorkoutDay.program_id == program.id))
        workout_exercise_count = db.scalar(
            select(func.count()).select_from(WorkoutExercise).join(WorkoutDay).where(WorkoutDay.program_id == program.id)
        )
        print(
            "Seed complete: "
            f"{len(EXERCISES)} exercises, "
            f"{workout_day_count} workout days, "
            f"{workout_exercise_count} workout exercises, "
            f"demo user {DEMO_USER_EMAIL}."
        )


def main() -> None:
    seed_database()


if __name__ == "__main__":
    main()
