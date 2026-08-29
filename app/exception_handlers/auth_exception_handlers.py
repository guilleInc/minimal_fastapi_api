from fastapi import Request, status
from fastapi.responses import JSONResponse


async def invalid_credentials_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
        content={
            "error": "INVALID_CREDENTIALS",
            "message": "Invalid or expired access token",
            "details": None,
        },
    )
