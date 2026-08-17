import pytest
import pytest_asyncio
from sqlalchemy import delete

from app.models.pet_model import PetModel
from app.repositories.pet_repository import SqlaPetRepository
from app.domain.pets import PetCreate, PetUpdate


@pytest_asyncio.fixture(autouse=True)
async def clean_pets(session):
    yield

    await session.execute(delete(PetModel))
    await session.commit()


@pytest.mark.asyncio
async def test_add_pet_persists_and_returns_pet(repository: SqlaPetRepository) -> None:
    # Arrange
    payload = PetCreate(name="Milo", type="cat", age=3)

    # Act
    pet = await repository.add_pet(payload)

    # Assert
    assert pet.id is not None
    assert pet.name == "Milo"
    assert pet.type == "cat"
    assert pet.age == 3


@pytest.mark.asyncio
async def test_get_pets_returns_all_pets(repository: SqlaPetRepository) -> None:
    # Arrange
    await repository.add_pet(PetCreate(name="Milo", type="cat", age=3))
    await repository.add_pet(PetCreate(name="Bolt", type="dog", age=5))

    # Act
    pets = await repository.get_pets()

    # Assert
    assert len(pets) == 2
    assert {pet.name for pet in pets} == {"Milo", "Bolt"}


@pytest.mark.asyncio
async def test_get_pet_returns_matching_pet(repository: SqlaPetRepository) -> None:
    # Arrange
    created_pet = await repository.add_pet(PetCreate(name="Milo", type="cat", age=3))

    # Act
    pet = await repository.get_pet(created_pet.id)

    # Assert
    assert pet is not None
    assert pet.id == created_pet.id
    assert pet.name == "Milo"


@pytest.mark.asyncio
async def test_get_pet_returns_none_when_missing(repository: SqlaPetRepository) -> None:
    # Arrange
    missing_pet_id = 999

    # Act
    pet = await repository.get_pet(missing_pet_id)

    # Assert
    assert pet is None


@pytest.mark.asyncio
async def test_update_pet_updates_only_provided_fields(repository: SqlaPetRepository) -> None:
    # Arrange
    created_pet = await repository.add_pet(PetCreate(name="Milo", type="cat", age=3))
    payload = PetUpdate(age=4)

    # Act
    updated_pet = await repository.update_pet(created_pet.id, payload)

    # Assert
    assert updated_pet is not None
    assert updated_pet.id == created_pet.id
    assert updated_pet.name == "Milo"
    assert updated_pet.type == "cat"
    assert updated_pet.age == 4


@pytest.mark.asyncio
async def test_update_pet_returns_none_when_missing(repository: SqlaPetRepository) -> None:
    # Arrange
    missing_pet_id = 999
    payload = PetUpdate(name="Ghost")

    # Act
    updated_pet = await repository.update_pet(missing_pet_id, payload)

    # Assert
    assert updated_pet is None


@pytest.mark.asyncio
async def test_delete_pet_removes_existing_pet(repository: SqlaPetRepository) -> None:
    # Arrange
    created_pet = await repository.add_pet(PetCreate(name="Milo", type="cat", age=3))

    # Act
    deleted = await repository.delete_pet(created_pet.id)
    pet = await repository.get_pet(created_pet.id)

    # Assert
    assert deleted is True
    assert pet is None


@pytest.mark.asyncio
async def test_delete_pet_returns_false_when_missing(repository: SqlaPetRepository) -> None:
    # Arrange
    missing_pet_id = 999

    # Act
    deleted = await repository.delete_pet(missing_pet_id)

    # Assert
    assert deleted is False
