from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.pets import Pet, PetCreate, PetUpdate
from app.repositories.pet_repository import PetRepository
from app.services.pet_service_errors import PetNotFoundError, PetServiceError
from app.utils import exception_boundary


class PetService:
    def __init__(self, session: AsyncSession, pet_repository: PetRepository) -> None:
        self.session = session
        self.pet_repository = pet_repository

    @exception_boundary(PetServiceError)
    async def add_pet(self, payload: PetCreate) -> Pet:
        pet = await self.pet_repository.add_pet(payload)
        await self.session.commit()
        return pet

    @exception_boundary(PetServiceError)
    async def get_pets(self) -> list[Pet]:
        return await self.pet_repository.get_pets()

    @exception_boundary(PetServiceError)
    async def get_pet(self, pet_id: int) -> Pet:
        pet = await self.pet_repository.get_pet(pet_id)
        if pet is None:
            raise PetNotFoundError()
        return pet

    @exception_boundary(PetServiceError)
    async def update_pet(self, pet_id: int, payload: PetUpdate) -> Pet:
        pet = await self.pet_repository.update_pet(pet_id, payload)
        if pet is None:
            raise PetNotFoundError()
        await self.session.commit()
        return pet

    @exception_boundary(PetServiceError)
    async def delete_pet(self, pet_id: int) -> None:
        if not await self.pet_repository.delete_pet(pet_id):
            raise PetNotFoundError()
        await self.session.commit()
