from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Protocol

from app.models.pet_model import PetModel
from app.domain.pets import Pet, PetCreate, PetUpdate


class PetRepositoryError(Exception):
    """Raised when a pet repository operation fails"""
    pass


class PetRepository(Protocol):
    async def add_pet(self, payload: PetCreate) -> Pet: ...

    async def get_pets(self) -> list[Pet]: ...

    async def get_pet(self, pet_id: int) -> Pet | None: ...

    async def update_pet(self, pet_id: int, payload: PetUpdate) -> Pet | None: ...

    async def delete_pet(self, pet_id: int) -> bool: ...


class SqlaPetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_pet(self, payload: PetCreate) -> Pet:
        try:
            stmt = insert(PetModel).values(**payload.model_dump()).returning(PetModel)
            pet = await self.session.scalar(stmt)
            return Pet.model_validate(pet)
        except Exception as exc:
            raise PetRepositoryError from exc

    async def get_pets(self) -> list[Pet]:
        try:
            stmt = select(PetModel)
            pets = await self.session.scalars(stmt)
            return [Pet.model_validate(pet) for pet in pets]
        except Exception as exc:
            raise PetRepositoryError from exc

    async def get_pet(self, pet_id: int) -> Pet | None:
        try:
            stmt = select(PetModel).where(PetModel.id == pet_id)
            pet = await self.session.scalar(stmt)
            return Pet.model_validate(pet) if pet else None
        except Exception as exc:
            raise PetRepositoryError from exc

    async def update_pet(self, pet_id: int, payload: PetUpdate) -> Pet | None:
        try:
            stmt = select(PetModel).where(PetModel.id == pet_id)
            pet_orm = await self.session.scalar(stmt)
            if pet_orm is None:
                return None

            update_data = payload.model_dump(exclude_unset=True)
            stmt = update(PetModel).where(PetModel.id == pet_id).values(**update_data).returning(PetModel)
            updated_pet = await self.session.scalar(stmt)
            return Pet.model_validate(updated_pet)
        except Exception as exc:
            raise PetRepositoryError from exc

    async def delete_pet(self, pet_id: int) -> bool:
        try:
            stmt = delete(PetModel).where(PetModel.id == pet_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0
        except Exception as exc:
            raise PetRepositoryError from exc
