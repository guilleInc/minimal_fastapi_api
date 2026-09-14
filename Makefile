.PHONY: install dev run generate-env create-user seed-db test lint format check

install:
	uv sync
	uv run pre-commit install

dev:
	uv run fastapi dev

run:
	uv run fastapi run

generate-env:
	uv run python -m scripts.generate_env

create-user:
	uv run python -m scripts.create_user

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
