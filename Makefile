.PHONY: up down logs build lint format-check test test-backend test-frontend migrate seed

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

lint:
	docker compose build backend frontend
	docker compose run --rm --no-deps backend sh -c "python scripts/check_format.py --check && python -m compileall -q app tests"
	docker compose run --rm --no-deps frontend npm run lint
	docker compose run --rm --no-deps frontend npm run format:check

format-check:
	docker compose build backend frontend
	docker compose run --rm --no-deps backend python scripts/check_format.py --check
	docker compose run --rm --no-deps frontend npm run format:check

test:
	docker compose build backend frontend
	docker compose run --rm --no-deps backend pytest
	docker compose run --rm --no-deps frontend npm test

test-backend:
	docker compose build backend
	docker compose run --rm --no-deps backend pytest

test-frontend:
	docker compose build frontend
	docker compose run --rm --no-deps frontend npm test

migrate:
	docker compose run --rm backend sh -c "python -m app.wait_for_db && alembic upgrade head"

seed: migrate
	docker compose run --rm backend sh -c "python -m app.wait_for_db && python -m app.seed"
