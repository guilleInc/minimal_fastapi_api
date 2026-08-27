"""Errors for user service operations."""


class UserServiceError(Exception):
    """Base exception for user service operations."""

    pass


class UserNotFoundError(UserServiceError):
    """Raised when a user is not found."""

    pass
