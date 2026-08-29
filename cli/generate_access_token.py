import argparse

from app.security.token_manager import token_manager
from app.services.auth_service import AuthService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an API access token.")
    parser.add_argument(
      "--name", 
      required=True, 
      help="Name associated with the access token."
    )
    parser.add_argument(
        "--expires-minutes",
        type=int,
        choices=range(1, 30000),
        default=30,
        help="Token lifetime in minutes (default: 30).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = AuthService(token_manager=token_manager).create_access_token(
        name=args.name,
        expires_delta=args.expires_minutes,
    )
    print(token.access_token)


if __name__ == "__main__":
    main()
