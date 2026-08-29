class AuthServiceError(Exception):
    """Base exception for authentication service operations."""

class UserAlreadyExistsError(AuthServiceError):
    """Raised when registering a user that already exists."""


class InvalidCredentialsError(AuthServiceError):
    """Raised when user credentials are invalid."""
