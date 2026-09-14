from fastapi import APIRouter, status

from app.dependencies import AuthServiceDep, PasswordRequestForm
from app.domain.users import UserIn
from app.security.token_manager import Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"},
    },
)


@router.post("/token", response_model=Token)
async def login(
    service: AuthServiceDep,
    form_data: PasswordRequestForm,
) -> Token:
    user_in = UserIn(username=form_data.username, password=form_data.password)
    return await service.authenticate_user(user_in)
