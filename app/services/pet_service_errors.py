class PetServiceError(Exception):
    """Base exception for pet service operations."""


class PetNotFoundError(PetServiceError):
    """Raised when a pet is not found."""

