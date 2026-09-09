from pathlib import Path
from typing import Protocol
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.utils import exception_boundary

CHUNK_SIZE = 64 * 1024
IMAGE_FORMAT = ("image/webp", b"RIFF", ".webp")


class ImageRepositoryError(Exception):
    """Raised when an image cannot be saved."""


class ImageRepository(Protocol):
    async def save(self, upload: UploadFile) -> str: ...

    async def delete(self, image_id: str) -> None: ...


class FileSystemImageRepository:
    def __init__(
        self,
        image_upload_dir: str,
        image_max_size_bytes: int,
    ) -> None:
        self.directory = Path(image_upload_dir)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = image_max_size_bytes

    @exception_boundary(ImageRepositoryError)
    async def save(self, upload: UploadFile) -> str:
        if upload.content_type != IMAGE_FORMAT[0]:
            raise ImageRepositoryError("Unsupported image type")

        image_id = self._generate_id()
        image_path = self._get_image_path(image_id)
        total_size = 0

        try:
            with image_path.open("wb") as image_file:
                chunk = await upload.read(CHUNK_SIZE)

                if not self._has_valid_signature(chunk):
                    raise ImageRepositoryError("Invalid image content")

                while chunk:
                    total_size += len(chunk)
                    if total_size > self.max_size_bytes:
                        raise ImageRepositoryError("Image exceeds the maximum allowed size")
                    image_file.write(chunk)
                    chunk = await upload.read(CHUNK_SIZE)

        except Exception:
            image_path.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

        return image_id

    @exception_boundary(ImageRepositoryError)
    async def delete(self, image_id: str) -> None:
        if not self._is_valid_id(image_id):
            raise ImageRepositoryError("Invalid image ID")

        image_path = self._get_image_path(image_id)
        image_path.unlink(missing_ok=True)

    def _get_image_path(self, image_id: str) -> Path:
        return self.directory / f"{image_id}{IMAGE_FORMAT[2]}"

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

    @staticmethod
    def _has_valid_signature(chunk: bytes) -> bool:
        return chunk.startswith(b"RIFF") and chunk[8:12] == b"WEBP"
