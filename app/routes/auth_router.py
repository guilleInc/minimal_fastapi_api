from fastapi import APIRouter, status

from app.dependencies import AuthServiceDep
from app.domain.users import UserIn
from app.schemas.user_schema import UserInSchema
from app.security.token_manager import Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"},
    },
)


@router.post("/login", response_model=Token)
async def login(payload: UserInSchema, service: AuthServiceDep) -> Token:
    user_in = UserIn.model_validate(payload.model_dump())
    return await service.authenticate_user(user_in)
