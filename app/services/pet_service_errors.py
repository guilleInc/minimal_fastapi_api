class PetServiceError(Exception):
    """Base exception for pet service operations."""

    pass


class PetNotFoundError(PetServiceError):
    """Raised when a pet is not found."""

    pass
