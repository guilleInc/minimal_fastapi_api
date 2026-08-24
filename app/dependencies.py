from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal
from app.repositories.pet_repository import PetRepository, SqlaPetRepository
from app.services.pet_service import PetService


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def get_pet_repository(session: SessionDep) -> PetRepository:
    return SqlaPetRepository(session=session)


PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]


def get_pet_service(session: SessionDep, repository: PetRepositoryDep) -> PetService:
    return PetService(session=session, repository=repository)


PetServiceDep = Annotated[PetService, Depends(get_pet_service)]
