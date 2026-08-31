import asyncio
import json
import os
from typing import Any

from sqlalchemy import insert

from app.database import DATABASE_FILE, SessionLocal, engine
from app.domain.pets import PetCreate
from app.models.base import Base
from app.models.pet_model import PetModel

DATA_FILE = "data/data.json"


async def ensure_database() -> None:
    if os.path.exists(DATABASE_FILE):
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


async def seed_db() -> int:
    await ensure_database()
    pets = load_pets()
    return await insert_pets(pets)


if __name__ == "__main__":
    count = asyncio.run(seed_db())
    print(f"Inserted {count} pets from {DATA_FILE}")
