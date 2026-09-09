from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.pets import Pet
from app.repositories.image_repository import ImageRepository
from app.repositories.pet_repository import PetRepository
from app.services.pet_service_errors import PetNotFoundError, PetServiceError
from app.utils import exception_boundary


class PetImageService:
    def __init__(
        self,
        session: AsyncSession,
        pet_repository: PetRepository,
        image_repository: ImageRepository,
    ) -> None:
        self.session = session
        self.pet_repository = pet_repository
        self.image_repository = image_repository

    @exception_boundary(PetServiceError)
    async def add_image(self, pet_id: int, upload: UploadFile) -> Pet:
        pet = await self.pet_repository.get_pet(pet_id)
        if pet is None:
            raise PetNotFoundError()

        image_id = await self.image_repository.save(upload)

        try:
            updated_pet = await self.pet_repository.update_image_id(pet_id, image_id)
            if updated_pet is None:
                raise PetNotFoundError()
            await self.session.commit()
        except Exception:
            await self.image_repository.delete(image_id)
            raise

        if pet.image_id is not None:
            await self.image_repository.delete(pet.image_id)
        return updated_pet

    @exception_boundary(PetServiceError)
    async def delete_image(self, pet_id: int) -> None:
        pet = await self.pet_repository.get_pet(pet_id)
        if pet is None:
            raise PetNotFoundError()

        if pet.image_id is None:
            return

        updated_pet = await self.pet_repository.update_image_id(pet_id, None)
        if updated_pet is None:
            raise PetNotFoundError()
        await self.session.commit()
        await self.image_repository.delete(pet.image_id)
