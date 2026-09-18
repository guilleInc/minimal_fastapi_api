FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY --from=ghcr.io/astral-sh/uv:0.10.10 /uv /uvx /bin/
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app
COPY scripts ./scripts

RUN mkdir -p /data /uploads

ENV DATABASE_PATH=/data/pets.db \
    IMAGE_UPLOAD_DIR=/uploads/pets

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
