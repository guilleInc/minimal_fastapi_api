class UserServiceError(Exception):
    """Base exception for user service operations."""

    ...


class UserNotFoundError(UserServiceError):
    """Raised when a user is not found."""

    ...
