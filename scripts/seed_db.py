import asyncio
import json
import os
from typing import Any

from sqlalchemy.dialects.sqlite import insert

from app.database import SessionLocal, engine, settings
from app.domain.pets import PetCreate
from app.models import PetModel, UserModel
from app.models.base import Base
from app.security.password_hasher import PasswordHasher

DATA_FILE = "data/data.json"

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

    return [PetCreate.model_validate(record).model_dump() for record in records]


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
