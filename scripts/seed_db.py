import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy.dialects.sqlite import insert

from app.database import SessionLocal, engine, settings
from app.domain.pets import PetCreate
from app.models import PetModel, UserModel
from app.models.base import Base
from app.security.password_hasher import PasswordHasher

DATA_FILE = "data/data.json"
IMAGE_DATA_DIR = Path("data/pet_images")

password_hasher = PasswordHasher()


async def ensure_database() -> None:
    if os.path.exists(settings.database_path):
        return

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


def load_pets() -> list[dict[str, Any]]:
    with open(DATA_FILE, encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"{DATA_FILE} must contain a JSON array")

    pets = []
    for record in records:
        image_filename = record.pop("image", None)
        pet = PetCreate.model_validate(record).model_dump()

        if image_filename is not None:
            image_id = copy_seed_image(image_filename)
            pet["image_id"] = image_id

        pets.append(pet)

    return pets


def copy_seed_image(filename: str) -> str:
    image_path = Path(filename)
    if image_path.name != filename or image_path.suffix.lower() != ".webp":
        raise ValueError(f"Invalid seed image filename: {filename}")

    source_path = IMAGE_DATA_DIR / image_path
    if not source_path.is_file():
        raise FileNotFoundError(f"Seed image not found: {source_path}")

    image_id = str(uuid5(NAMESPACE_URL, f"minimal-pets-api/{filename}"))
    destination_dir = Path(settings.image_upload_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, destination_dir / f"{image_id}.webp")
    return image_id


async def insert_pets(pets: list[dict[str, Any]]) -> int:
    async with SessionLocal.begin() as session:
        await session.execute(insert(PetModel), pets)

    return len(pets)


async def create_admin_user() -> None:
    password = "admin"

    async with SessionLocal.begin() as session:
        stmt = insert(UserModel).values(
            username="admin",
            password_hash=password_hasher.hash(password),
            is_active=True,
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["username"])
        await session.execute(stmt)


async def seed_db() -> int:
    await ensure_database()
    await create_admin_user()
    pets = load_pets()
    return await insert_pets(pets)


if __name__ == "__main__":
    count = asyncio.run(seed_db())
    print(f"Inserted {count} pets from {DATA_FILE}")
