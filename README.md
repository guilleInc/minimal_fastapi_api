# Pets API

Simple CRUD API for pets built with FastAPI.

## Development

Install dependencies and enable the pre-commit hooks:

```bash
make install
```

After installation, pre-commit runs automatically before each commit and blocks
commits when a check fails. Run the hooks manually across the repository with:

```bash
uv run pre-commit run --all-files
```

Common commands are also available through `make`:

```bash
make install  # Install dependencies
make dev      # Start the development server with auto-reload
make run      # Start the production server
make test     # Run tests
make lint     # Check code with Ruff
make format   # Format code with Ruff
make check    # Run all pre-commit checks
```
