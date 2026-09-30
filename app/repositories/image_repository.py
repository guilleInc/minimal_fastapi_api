from pathlib import Path
from typing import BinaryIO, Protocol
from uuid import UUID, uuid4

from fastapi import UploadFile
from PIL import Image, ImageOps
from PIL.Image import DecompressionBombError, UnidentifiedImageError

from app.utils import exception_boundary

CONTENT_TYPE_TO_FORMATS = {
    "image/jpeg": {"JPEG"},
    "image/jpg": {"JPEG"},
    "image/png": {"PNG"},
    "image/webp": {"WEBP"},
}
WEBP_EXTENSION = ".webp"


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
        image_max_input_dimension: int = 4096,
        image_max_output_dimension: int = 2048,
    ) -> None:
        self.directory = Path(image_upload_dir)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = image_max_size_bytes
        self.max_input_dimension = image_max_input_dimension
        self.max_output_dimension = image_max_output_dimension

    @exception_boundary(ImageRepositoryError)
    async def save(self, upload: UploadFile) -> str:
        if upload.content_type not in CONTENT_TYPE_TO_FORMATS:
            raise ImageRepositoryError("Unsupported image type")
        if upload.size is None:
            raise ImageRepositoryError("Unable to determine image size")
        if upload.size > self.max_size_bytes:
            raise ImageRepositoryError("Image exceeds the maximum allowed size")

        image_id = self._generate_id()
        image_path = self._get_image_path(image_id)
        temporary_path = image_path.with_name(f".{image_id}.tmp")

        try:
            await upload.seek(0)
            self._save_normalized_image(
                upload.file,
                temporary_path,
                CONTENT_TYPE_TO_FORMATS[upload.content_type],
            )
            temporary_path.replace(image_path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
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

    def _save_normalized_image(
        self,
        image_file: BinaryIO,
        image_path: Path,
        expected_formats: set[str],
    ) -> None:
        try:
            with Image.open(image_file) as image:
                if image.format not in expected_formats:
                    raise ImageRepositoryError("Unsupported image type")
                image.verify()

            image_file.seek(0)
            with Image.open(image_file) as image:
                width, height = image.size
                if width > self.max_input_dimension or height > self.max_input_dimension:
                    raise ImageRepositoryError("Image dimensions exceed the maximum allowed size")

                normalized_image = ImageOps.exif_transpose(image)
                try:
                    normalized_image.thumbnail(
                        (self.max_output_dimension, self.max_output_dimension),
                        Image.Resampling.LANCZOS,
                    )
                    output_mode = (
                        "RGBA"
                        if "A" in normalized_image.getbands()
                        or "transparency" in normalized_image.info
                        else "RGB"
                    )
                    with normalized_image.convert(output_mode) as output_image:
                        output_image.save(
                            image_path,
                            format="WEBP",
                        )
                finally:
                    if normalized_image is not image:
                        normalized_image.close()
        except (DecompressionBombError, OSError, UnidentifiedImageError, ValueError) as exc:
            raise ImageRepositoryError("Invalid image content") from exc

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
