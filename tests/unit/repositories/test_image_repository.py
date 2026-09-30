from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile
from PIL import Image
from starlette.datastructures import Headers

from app.repositories.image_repository import (
    FileSystemImageRepository,
    ImageRepositoryError,
)

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def create_image(
    image_format: str,
    size: tuple[int, int],
    mode: str = "RGB",
) -> bytes:
    image = Image.new(mode, size, (255, 0, 0, 128) if mode == "RGBA" else "red")
    output = BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


def create_upload(data: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        file=BytesIO(data),
        filename="pet-image",
        size=len(data),
        headers=Headers({"content-type": content_type}),
    )


@pytest.fixture
def image_repository(tmp_path: Path) -> FileSystemImageRepository:
    return FileSystemImageRepository(
        image_upload_dir=str(tmp_path),
        image_max_size_bytes=MAX_IMAGE_SIZE,
        image_max_input_dimension=4096,
        image_max_output_dimension=2048,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("image_format", "content_type"),
    [
        ("JPEG", "image/jpeg"),
        ("PNG", "image/png"),
        ("WEBP", "image/webp"),
    ],
)
async def test_save_accepts_supported_formats_and_writes_webp(
    image_repository: FileSystemImageRepository,
    image_format: str,
    content_type: str,
) -> None:
    upload = create_upload(create_image(image_format, (100, 50)), content_type)

    image_id = await image_repository.save(upload)

    output_path = image_repository.directory / f"{image_id}.webp"
    assert output_path.is_file()
    with Image.open(output_path) as output:
        assert output.format == "WEBP"
        assert output.size == (100, 50)
    assert upload.file.closed


@pytest.mark.asyncio
async def test_save_resizes_large_images_without_changing_aspect_ratio(
    image_repository: FileSystemImageRepository,
) -> None:
    upload = create_upload(create_image("PNG", (4096, 2048)), "image/png")

    image_id = await image_repository.save(upload)

    with Image.open(image_repository.directory / f"{image_id}.webp") as output:
        assert output.size == (2048, 1024)


@pytest.mark.asyncio
async def test_save_rejects_images_over_input_dimension_limit(
    image_repository: FileSystemImageRepository,
) -> None:
    upload = create_upload(create_image("PNG", (4097, 1)), "image/png")

    with pytest.raises(ImageRepositoryError, match="dimensions"):
        await image_repository.save(upload)

    assert list(image_repository.directory.iterdir()) == []


@pytest.mark.asyncio
async def test_save_rejects_images_over_input_size_limit(
    image_repository: FileSystemImageRepository,
) -> None:
    upload = create_upload(b"x" * (MAX_IMAGE_SIZE + 1), "image/png")

    with pytest.raises(ImageRepositoryError, match="maximum allowed size"):
        await image_repository.save(upload)

    assert list(image_repository.directory.iterdir()) == []


@pytest.mark.asyncio
async def test_save_rejects_uploads_without_size_metadata(
    image_repository: FileSystemImageRepository,
) -> None:
    data = create_image("PNG", (10, 10))
    upload = UploadFile(
        file=BytesIO(data),
        filename="pet-image",
        headers=Headers({"content-type": "image/png"}),
    )

    with pytest.raises(ImageRepositoryError, match="determine image size"):
        await image_repository.save(upload)

    assert list(image_repository.directory.iterdir()) == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("data", "content_type"),
    [
        (b"not an image", "image/png"),
        (create_image("GIF", (10, 10)), "image/gif"),
        (create_image("JPEG", (10, 10)), "image/png"),
    ],
)
async def test_save_rejects_invalid_or_unsupported_images(
    image_repository: FileSystemImageRepository,
    data: bytes,
    content_type: str,
) -> None:
    upload = create_upload(data, content_type)

    with pytest.raises(ImageRepositoryError):
        await image_repository.save(upload)

    assert list(image_repository.directory.iterdir()) == []


@pytest.mark.asyncio
async def test_save_preserves_transparency(
    image_repository: FileSystemImageRepository,
) -> None:
    upload = create_upload(create_image("PNG", (10, 10), mode="RGBA"), "image/png")

    image_id = await image_repository.save(upload)

    with Image.open(image_repository.directory / f"{image_id}.webp") as output:
        assert "A" in output.getbands()


@pytest.mark.asyncio
async def test_delete_removes_saved_image(
    image_repository: FileSystemImageRepository,
) -> None:
    image_id = await image_repository.save(
        create_upload(create_image("JPEG", (10, 10)), "image/jpeg")
    )
    image_path = image_repository.directory / f"{image_id}.webp"

    await image_repository.delete(image_id)

    assert not image_path.exists()
