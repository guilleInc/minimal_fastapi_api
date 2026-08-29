from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.repositories.pet_repository import PetRepository, SqlaPetRepository
from app.security.token_manager import token_manager
from app.services.auth_service import AuthService
from app.services.pet_service import PetService


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

security = HTTPBearer()
AccessTokenDep = Annotated[
    HTTPAuthorizationCredentials,
    Depends(security),
]


def get_auth_service() -> AuthService:
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
