.PHONY: install dev run test lint format check

install:
	uv sync
	uv run pre-commit install

dev:
	uv run fastapi dev

run:
	uv run fastapi run

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run pre-commit run --all-files
