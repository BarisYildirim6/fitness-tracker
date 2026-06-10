# AGENTS.md — Fitness Tracker Web App

## Project Goal

Build a fully Dockerized gym/fitness tracking web app for a personal home/gym training workflow.

The app should support:
- User profile and fitness goals
- Exercise library with alternatives
- Weekly workout plan templates
- Workout logging with sets, reps, weight, and RPE
- Body progress tracking: weight, waist, steps, protein, calories, sleep
- Dashboard analytics: weekly weight average, workout adherence, volume trends, PRs
- Equipment-aware exercise alternatives
- CSV export later

This is a portfolio-quality project, not a throwaway prototype.

## Current User Context

The primary user is 184 cm, 115 kg, training at home with:
- Adjustable dumbbell/barbell set
- 4x5 kg plates
- 4x2.5 kg plates
- Two half-barbell handles that can combine into a 2 kg bar

Training goals:
- Fat loss
- Muscle volume
- Strength
- Sustainable weekly tracking

The app should support both home and gym modes.

## Required Stack

Use this stack unless explicitly changed:

Frontend:
- React
- TypeScript
- Vite
- React Router
- React Hook Form
- Zod
- Recharts
- TanStack Query if useful

Backend:
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- PostgreSQL
- JWT authentication

DevOps:
- Docker
- Docker Compose
- Separate frontend/backend/db containers
- .env.example
- Health checks where reasonable
- Makefile for common commands

Testing:
- Backend: pytest
- Frontend: basic unit/component structure if feasible
- Add smoke tests for critical backend endpoints

## Non-negotiable Docker Requirement

The project must run with:

docker compose up --build

The app should expose:
- Frontend on http://localhost:5173
- Backend API on http://localhost:8000
- API docs on http://localhost:8000/docs
- PostgreSQL on internal Docker network only unless explicitly needed

Do not require local Python, Node, or PostgreSQL installation to run the app.

## Security Requirements

- Never hardcode secrets.
- Use .env.example.
- Keep .env gitignored.
- Hash passwords using a proper password hashing library.
- Validate request bodies with Pydantic/Zod.
- Use CORS narrowly for local frontend/backend dev.
- Avoid leaking stack traces in production mode.
- Add basic input validation and sensible database constraints.
- Do not log passwords, tokens, or sensitive body metrics.

## Coding Standards

- Prefer clear, boring, maintainable code.
- Use typed models and schemas.
- Keep backend layers separated:
  - routers
  - models
  - schemas
  - services
  - database/session
  - auth
- Keep frontend organized:
  - pages
  - components
  - api
  - hooks
  - types
  - lib
- Add comments only where they explain non-obvious logic.
- Avoid overengineering the MVP.

## Data Model Priorities

Start with these entities:

### User

- id
- email
- hashed_password
- created_at

### UserProfile

- user_id
- height_cm
- current_weight_kg
- goal
- training_level
- preferred_mode: home/gym
- target_weekly_weight_loss_kg

### Exercise

- id
- name
- primary_muscle
- secondary_muscles
- equipment
- difficulty
- instructions
- alternative_exercise_ids

### Program

- id
- user_id
- name
- description
- is_active

### WorkoutDay

- id
- program_id
- day_of_week
- title
- focus

### WorkoutExercise

- id
- workout_day_id
- exercise_id
- order_index
- sets
- rep_min
- rep_max
- rest_seconds
- tempo
- notes

### WorkoutLog

- id
- user_id
- workout_day_id
- started_at
- completed_at
- notes

### SetLog

- id
- workout_log_id
- exercise_id
- set_index
- weight_kg
- reps
- rpe

### BodyMetric

- id
- user_id
- date
- weight_kg
- waist_cm
- steps
- protein_g
- calories
- sleep_hours
- mood

## MVP Screens

1. Login/Register
2. Onboarding/Profile
3. Dashboard
4. Weekly Plan
5. Active Workout Logger
6. Exercise Library
7. Progress Tracker
8. Settings

## Seed Data

Seed the app with a home workout plan based on:

### Monday Upper A

- Dumbbell Floor Press / Bench Press
- One-arm Dumbbell Row
- Standing Dumbbell Shoulder Press
- Dumbbell Lateral Raise
- Barbell/Dumbbell Curl
- Overhead Dumbbell Triceps Extension

### Tuesday Lower A + Core

- Goblet Squat
- Dumbbell Romanian Deadlift
- Bulgarian Split Squat
- Standing Calf Raise
- Plank
- Dead Bug / Leg Raise

### Wednesday Recovery

- Brisk Walk
- Mobility

### Thursday Upper B

- Push-up / Dumbbell Bench Press
- Dumbbell Pullover
- Bent-over Dumbbell Row
- Arnold Press
- Hammer Curl
- Dumbbell Skull Crusher
- Rear Delt Raise

### Friday Lower B + Core

- Dumbbell Front Squat / Goblet Squat
- Dumbbell Reverse Lunge
- Single-leg Romanian Deadlift
- Dumbbell Hip Thrust / Glute Bridge
- Suitcase Carry
- Side Plank / Russian Twist

### Saturday

- Long walk or dumbbell conditioning circuit

### Sunday

- Rest

Each exercise should include at least one alternative and one easier variation.

## Development Behavior

When given a task:

1. Inspect the current repo.
2. Make a small implementation plan.
3. Implement the requested changes.
4. Run relevant tests or at least validation commands.
5. Report what changed and what remains.

Never rewrite the whole project unnecessarily.
Do not delete user work without asking.