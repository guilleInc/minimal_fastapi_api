from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.repositories.pet_repository import PetRepository, SqlaPetRepository
from app.security.token_manager import TokenManager
from app.services.auth_service import AuthService
from app.services.pet_service import PetService
from app.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

security = HTTPBearer()
AccessTokenDep = Annotated[
    HTTPAuthorizationCredentials,
    Depends(security),
]


def get_token_manager(settings: SettingsDep) -> TokenManager:
    return TokenManager(secret_key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


TokenManagerDep = Annotated[TokenManager, Depends(get_token_manager)]


def get_auth_service(token_manager: TokenManagerDep) -> AuthService:
    return AuthService(token_manager=token_manager)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def verify_access_token(
    access_token: AccessTokenDep,
    service: AuthServiceDep,
) -> str:
    return service.verify_access_token(access_token.credentials)


AuthorizationDep = Annotated[str, Depends(verify_access_token)]


def get_pet_repository(session: SessionDep) -> PetRepository:
    return SqlaPetRepository(session=session)


PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]


def get_pet_service(session: SessionDep, repository: PetRepositoryDep) -> PetService:
    return PetService(session=session, pet_repository=repository)


PetServiceDep = Annotated[PetService, Depends(get_pet_service)]
