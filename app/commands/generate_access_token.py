import argparse
import os
from datetime import timedelta

from app.security.token_manager import TokenManager
from app.services.auth_service import AuthService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an API access token.")
    parser.add_argument("--name", required=True, help="Name associated with the access token.")
    parser.add_argument(
        "--expires-minutes",
        type=int,
        default=30,
        help="Token lifetime in minutes (default: 30).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.expires_minutes <= 0:
        raise ValueError("Token expiration must be greater than zero")

    secret_key = os.environ.get("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY environment variable is required")

    service = AuthService(
        token_manager=TokenManager(
            secret_key=secret_key,
            algorithm=os.environ.get("JWT_ALGORITHM", "HS256"),
        )
    )
    token = service.create_access_token(
        name=args.name,
        expires_delta=timedelta(minutes=args.expires_minutes),
    )
    print(token.access_token)


if __name__ == "__main__":
    main()
