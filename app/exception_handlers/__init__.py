from fastapi import FastAPI

from app.exception_handlers.pet_exception_handlers import pet_service_error_handler
from app.services.pet_service_errors import PetServiceError


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(PetServiceError, pet_service_error_handler)
