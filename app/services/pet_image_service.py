from io import BytesIO
from typing import BinaryIO

from PIL import Image, ImageOps
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.pets import Pet
from app.repositories.image_repository import ImageRepository
from app.repositories.pet_repository import PetRepository
from app.services.pet_service_errors import PetNotFoundError, PetServiceError
from app.settings import image_settings
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

    def validate_image(self, file: BinaryIO) -> None:
        with Image.open(file) as image:
            if image.format not in image_settings.ALLOWED_FORMATS:
                raise ValueError("Unsupported image format")
            if max(image.size) > image_settings.MAX_INPUT_DIMENSION:
                raise ValueError("Image dimensions are too large")
            image.verify()
        file.seek(0)

    def convert_image(self, file: BinaryIO) -> BinaryIO:
        file.seek(0)
        output = BytesIO()
        with Image.open(file) as opened_image:
            normalized_image = ImageOps.exif_transpose(opened_image)
            try:
                normalized_image.thumbnail(
                    (
                        image_settings.MAX_OUTPUT_DIMENSION,
                        image_settings.MAX_OUTPUT_DIMENSION,
                    ),
                    Image.Resampling.LANCZOS,
                )
                output_mode = (
                    "RGBA"
                    if "A" in normalized_image.getbands() or "transparency" in normalized_image.info
                    else "RGB"
                )
                with normalized_image.convert(output_mode) as converted_image:
                    converted_image.save(output, format="WEBP")
            finally:
                if normalized_image is not opened_image:
                    normalized_image.close()

        output.seek(0)
        return output

    @exception_boundary(PetServiceError)
    async def add_image(self, pet_id: int, image: BinaryIO) -> Pet:
        pet = await self.pet_repository.get_pet(pet_id)
        if pet is None:
            raise PetNotFoundError()

        self.validate_image(image)
        converted_image = self.convert_image(image)
        image_id = await self.image_repository.save(converted_image)

        try:
            updated_pet = await self.pet_repository.update_image_id(pet_id, image_id)
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

        await self.pet_repository.update_image_id(pet_id, None)
        await self.session.commit()
        await self.image_repository.delete(pet.image_id)
