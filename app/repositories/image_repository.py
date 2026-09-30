from pathlib import Path
from typing import BinaryIO, Protocol
from uuid import UUID, uuid4

from app.utils import exception_boundary

WEBP_EXTENSION = ".webp"


class ImageRepositoryError(Exception):
    """Raised when an image cannot be saved."""


class ImageRepository(Protocol):
    async def save(self, image: BinaryIO) -> str: ...

    async def delete(self, image_id: str) -> None: ...


class FileSystemImageRepository:
    def __init__(self, image_upload_dir: str) -> None:
        self.directory = Path(image_upload_dir)
        self.directory.mkdir(parents=True, exist_ok=True)

    @exception_boundary(ImageRepositoryError)
    async def save(self, image: BinaryIO) -> str:
        image_id = self._generate_id()
        image_path = self._get_image_path(image_id)
        temporary_path = image_path.with_name(f".{image_id}.tmp")

        try:
            image.seek(0)
            with temporary_path.open("wb") as image_file:
                image_file.write(image.read())
            temporary_path.replace(image_path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            image_path.unlink(missing_ok=True)
            raise

        return image_id

    @exception_boundary(ImageRepositoryError)
    async def delete(self, image_id: str) -> None:
        if not self._is_valid_id(image_id):
            raise ImageRepositoryError("Invalid image ID")

        image_path = self._get_image_path(image_id)
        image_path.unlink(missing_ok=True)

    def _get_image_path(self, image_id: str) -> Path:
        return self.directory / f"{image_id}{WEBP_EXTENSION}"

    @staticmethod
    def _is_valid_id(value: str) -> bool:
        try:
            UUID(value)
        except ValueError:
            return False
        return True

    @staticmethod
    def _generate_id() -> str:
        return str(uuid4())
