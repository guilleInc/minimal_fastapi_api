from pathlib import Path
from secrets import token_urlsafe

ENV_FILE = Path(".env")
ENVIRONMENT_VARIABLES = [
    "ENVIRONMENT=development",
    f"JWT_SECRET_KEY={token_urlsafe(32)}",
    "JWT_ALGORITHM=HS256",
    "DATABASE_PATH=./pets.db",
    "IMAGE_URL_PREFIX=/uploads/pets",
]


def main() -> None:
    if ENV_FILE.exists():
        print(f"{ENV_FILE} already exists; skipping generation")
        return

    ENV_FILE.write_text(
        "\n".join([*ENVIRONMENT_VARIABLES, ""]),
        encoding="utf-8",
    )
    print(f"Created {ENV_FILE}")


if __name__ == "__main__":
    main()
