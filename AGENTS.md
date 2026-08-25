# AGENTS.md

## Project overview
Build a very simple CRUD API with FastAPI for pets. Keep the codebase small, readable, and easy to extend.

## Domain
- Model pets with a minimal schema: `id`, `name`, `type`, `age`
- Keep the first version focused on basic CRUD only
- Prefer simple values and validations over extra features

## Goals
- Implement clear REST endpoints for create, read, update, and delete operations
- Keep validation strict and responses predictable
- Favor simple, maintainable code over premature abstraction
- Write code that is easy to test and document

## Recommended stack
- Python 3.14
- FastAPI
- Uvicorn
- Pydantic
- SQLModel
- SQLite
- Ruff
- uv

## Project structure
- `app/routes/` for HTTP endpoints only
- `app/services/` for business logic
- `app/repositories/` for persistence or in-memory storage
- `app/schemas/` for Pydantic models
- `app/main.py` for app setup and router wiring

## General rules
- Follow existing project conventions first
- Keep functions small and focused
- Use type hints everywhere practical
- Avoid duplicated logic; extract shared helpers when it improves clarity
- Do not add dependencies unless they solve a real need
- Prefer explicit error handling over silent failure
- Keep API responses consistent across endpoints

## API design
- Use RESTful route naming
- Return appropriate HTTP status codes
- Validate request bodies with Pydantic models
- Separate create/update schemas from read schemas when needed
- Include sensible error messages for invalid input and missing resources
- Keep routes thin; put business rules in services and data access in repositories

## Data and persistence
- Start simple; use in-memory storage unless persistence is needed
- Keep repository code isolated from route handlers
- Use migrations if schema changes are introduced
- Never hardcode secrets or environment-specific values

## Testing
- Add tests for success and failure cases
- Cover validation, not-found behavior, and edge cases
- Prefer targeted tests for changed endpoints or models
- Keep tests deterministic and independent

## Commands
- Install dependencies with `uv sync`
- Run the app with `fastapi dev`
- Run tests with `pytest`
- Run linting with `ruff check .`

## Documentation
- Update README when setup or usage changes
- Document endpoints and expected payloads if they are not obvious
- Keep examples accurate and runnable

## When making changes
- Make the smallest change that fully solves the task
- Preserve existing behavior unless the task explicitly changes it
- If a requirement is unclear, ask before guessing
- Verify the implementation before considering it done
