.PHONY: install dev run generate-env generate-access-token seed-db test lint format check

install:
	uv sync
	uv run pre-commit install

dev:
	uv run fastapi dev

run:
	uv run fastapi run

generate-env:
	uv run python -m scripts.generate_env

generate-access-token:
	uv run python -m scripts.generate_access_token --user "$(user)" --expires-minutes "$(expires_minutes)"

seed-db:
	uv run python -m scripts.seed_db

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run pre-commit run --all-files
