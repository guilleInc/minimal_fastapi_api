from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Protocol

from app.models.pet_model import PetModel
from app.schemas.pet_schema import PetCreate, PetUpdate


class PetRepository(Protocol):
    async def add_pet(self, payload: PetCreate) -> PetModel: ...

    async def get_pets(self) -> list[PetModel]: ...

    async def get_pet(self, pet_id: int) -> PetModel | None: ...

    async def update_pet(self, pet_id: int, payload: PetUpdate) -> PetModel | None: ...

    async def delete_pet(self, pet_id: int) -> bool: ...


class SqlaPetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_pet(self, payload: PetCreate) -> PetModel:
        stmt = insert(PetModel).values(**payload.model_dump()).returning(PetModel)
        pet = await self.session.scalar(stmt)
        await self.session.commit()
        return pet

    async def get_pets(self) -> list[PetModel]:
        stmt = select(PetModel)
        return list(await self.session.scalars(stmt))

    async def get_pet(self, pet_id: int) -> PetModel | None:
        stmt = select(PetModel).where(PetModel.id == pet_id)
        return await self.session.scalar(stmt)

    async def update_pet(self, pet_id: int, payload: PetUpdate) -> PetModel | None:
        pet = await self.get_pet(pet_id)
        if pet is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        stmt = update(PetModel).where(PetModel.id == pet_id).values(**update_data).returning(PetModel)
        updated_pet = await self.session.scalar(stmt)
        await self.session.commit()
        return updated_pet

    async def delete_pet(self, pet_id: int) -> bool:
        stmt = delete(PetModel).where(PetModel.id == pet_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
