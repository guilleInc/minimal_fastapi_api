from app.dependencies import get_settings, get_token_manager
from app.services.auth_service import AuthService

DEFAULT_EXPIRATION_MINUTES = 30


def main() -> None:
    print("Generate API access token")
    user = input("User name: ").strip()

    expiration = input(
        f"Expiration time in minutes (default: {DEFAULT_EXPIRATION_MINUTES}): "
    ).strip()

    if not expiration:
        expires_minutes = DEFAULT_EXPIRATION_MINUTES
    else:
        try:
            expires_minutes = int(expiration)
        except ValueError as exc:
            raise ValueError("Expiration time must be a positive integer") from exc

        if expires_minutes <= 0:
            raise ValueError("Expiration time must be a positive integer")

    token = AuthService(token_manager=get_token_manager(get_settings())).create_access_token(
        user=user,
        expires_delta=expires_minutes,
    )

    print("Access token:")
    print(f"{token.access_token}")


if __name__ == "__main__":
    main()
