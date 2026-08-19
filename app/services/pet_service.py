import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pet_repository import PetRepository, PetRepositoryError
from app.domain.pets import Pet, PetCreate, PetUpdate
from app.services.pet_service_errors import PetNotFoundError, PetServiceError

logger = logging.getLogger(__name__)


class PetService:
    def __init__(self, session: AsyncSession, repository: PetRepository) -> None:
        self.session = session
        self.repository = repository

    async def add_pet(self, payload: PetCreate) -> Pet:
        try:
            pet = await self.repository.add_pet(payload)
            await self.session.commit()
            return pet
        except PetRepositoryError as exc:
            logger.exception("Failed to add pet")
            raise PetServiceError() from exc

    async def get_pets(self) -> list[Pet]:
        try:
            return await self.repository.get_pets()
        except PetRepositoryError as exc:
            logger.exception("Failed to get pets")
            raise PetServiceError() from exc

    async def get_pet(self, pet_id: int) -> Pet:
        try:
            pet = await self.repository.get_pet(pet_id)
            if pet is None:
                raise PetNotFoundError()
            return pet
        except PetRepositoryError as exc:
            logger.exception("Failed to get pet %d", pet_id)
            raise PetServiceError() from exc

    async def update_pet(self, pet_id: int, payload: PetUpdate) -> Pet:
        try:
            pet = await self.repository.update_pet(pet_id, payload)
            if pet is None:
                raise PetNotFoundError()
            await self.session.commit()
            return pet
        except PetRepositoryError as exc:
            logger.exception("Failed to update pet %d", pet_id)
            raise PetServiceError() from exc

    async def delete_pet(self, pet_id: int) -> None:
        try:
            if not await self.repository.delete_pet(pet_id):
                raise PetNotFoundError()
            await self.session.commit()
        except PetRepositoryError as exc:
            logger.exception("Failed to delete pet %d", pet_id)
            raise PetServiceError() from exc
