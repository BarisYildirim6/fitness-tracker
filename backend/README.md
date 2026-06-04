# Backend

FastAPI backend for the fitness tracker app.

## Migrations

Alembic is configured to read `DATABASE_URL` from the backend settings and to use the SQLAlchemy model metadata in `app.models`.

Run migrations inside Docker:

```bash
docker compose run --rm backend sh -c "python -m app.wait_for_db && alembic upgrade head"
```

Create a new migration after changing models:

```bash
docker compose run --rm backend alembic revision --autogenerate -m "describe change"
```

The `make migrate` command runs `alembic upgrade head` through Docker Compose.

## Seeding

Seed the default workout plan inside Docker:

```bash
docker compose run --rm backend sh -c "python -m app.wait_for_db && python -m app.seed"
```

The `make seed` command runs migrations first, then executes the seed script. The seed script is idempotent.
