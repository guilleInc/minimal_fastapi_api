from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.pet_repository import PetRepository
from app.services.pet_service import PetService


def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db_session)]


def get_pet_repository(session: SessionDep) -> PetRepository:
    return PetRepository(session=session)


PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]


def get_pet_service(repository: PetRepositoryDep) -> PetService:
    return PetService(repository=repository)


PetServiceDep = Annotated[PetService, Depends(get_pet_service)]
