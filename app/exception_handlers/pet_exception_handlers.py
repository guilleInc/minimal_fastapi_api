"""Exception handlers for pet service errors."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.services.pet_service_errors import PetNotFoundError


async def pet_service_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all PetServiceError exceptions."""

    # Check specific exception types
    if isinstance(exc, PetNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "PET_NOT_FOUND",
                "message": "Pet not found",
                "details": None,
            },
        )

    # Default handler for generic PetServiceError
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Internal server error",
            "details": None,
        },
    )
