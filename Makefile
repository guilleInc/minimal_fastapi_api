.PHONY: install dev run generate-access-token test lint format check

install:
	uv sync
	uv run pre-commit install

dev:
	uv run fastapi dev

run:
	uv run fastapi run

generate-access-token:
	uv run python -m cli.generate_access_token --name "$(name)" --expires-minutes "$(expires_minutes)"

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run pre-commit run --all-files
