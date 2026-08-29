import argparse

from app.dependencies import get_settings, get_token_manager
from app.services.auth_service import AuthService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an API access token.")
    parser.add_argument(
        "--user",
        required=True,
        help="User associated with the access token.",
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
    token = AuthService(token_manager=get_token_manager(get_settings())).create_access_token(
        user=args.user,
        expires_delta=args.expires_minutes,
    )
    print(token.access_token)


if __name__ == "__main__":
    main()
