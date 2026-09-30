from io import BytesIO
from pathlib import Path

import pytest

from app.repositories.image_repository import FileSystemImageRepository


@pytest.fixture
def image_repository(tmp_path: Path) -> FileSystemImageRepository:
    return FileSystemImageRepository(image_upload_dir=str(tmp_path))


@pytest.mark.asyncio
async def test_save_writes_image_to_repository_directory(
    image_repository: FileSystemImageRepository,
) -> None:
    image_data = b"converted-webp-image"

    image_id = await image_repository.save(BytesIO(image_data))

    image_path = image_repository.directory / f"{image_id}.webp"
    assert image_path.read_bytes() == image_data


@pytest.mark.asyncio
async def test_save_rewinds_image_before_writing(
    image_repository: FileSystemImageRepository,
) -> None:
    image = BytesIO(b"converted-webp-image")
    image.seek(5)

    image_id = await image_repository.save(image)

    assert (image_repository.directory / f"{image_id}.webp").read_bytes() == b"converted-webp-image"


@pytest.mark.asyncio
async def test_delete_removes_saved_image(
    image_repository: FileSystemImageRepository,
) -> None:
    image_id = await image_repository.save(BytesIO(b"converted-webp-image"))
    image_path = image_repository.directory / f"{image_id}.webp"

    await image_repository.delete(image_id)

    assert not image_path.exists()
