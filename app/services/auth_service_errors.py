class AuthServiceError(Exception):
    """Base exception for authentication service operations."""

    pass


class UserAlreadyExistsError(AuthServiceError):
    """Raised when registering a user that already exists."""

    pass


class InvalidCredentialsError(AuthServiceError):
    """Raised when user credentials are invalid."""

    pass
