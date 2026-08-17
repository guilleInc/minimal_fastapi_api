from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pet_repository import PetRepository
from app.domain.pets import Pet, PetCreate, PetUpdate


class PetService:
    def __init__(self, session: AsyncSession, repository: PetRepository) -> None:
        self.session = session
        self.repository = repository

    async def add_pet(self, payload: PetCreate) -> Pet:
        pet = await self.repository.add_pet(payload)
        await self.session.commit()
        return pet

    async def get_pets(self) -> list[Pet]:
        return await self.repository.get_pets()

    async def get_pet(self, pet_id: int) -> Pet:
        pet = await self.repository.get_pet(pet_id)
        if pet is None:
            raise ValueError(f"Pet with id {pet_id} not found")
        return pet

    async def update_pet(self, pet_id: int, payload: PetUpdate) -> Pet:
        pet = await self.repository.update_pet(pet_id, payload)
        if pet is None:
            raise ValueError(f"Pet with id {pet_id} not found")
        await self.session.commit()
        return pet

    async def delete_pet(self, pet_id: int) -> None:
        if not await self.repository.delete_pet(pet_id):
            raise ValueError(f"Pet with id {pet_id} not found")
        await self.session.commit()
