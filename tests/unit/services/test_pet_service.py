"""Unit tests for PetService."""


import pytest

from app.domain.pets import Pet, PetCreate, PetUpdate
from app.repositories.pet_repository import PetRepositoryError
from app.services.pet_service_errors import PetNotFoundError, PetServiceError


class TestAddPet:
    """Tests for PetService.add_pet()"""

    @pytest.mark.asyncio
    async def test_add_pet_success(self, service, mock_repository, mock_session):
        """Test successfully adding a pet."""
        pet_create = PetCreate(name="Fluffy", type="cat", age=3)
        expected_pet = Pet(id=1, name="Fluffy", type="cat", age=3)
        mock_repository.add_pet.return_value = expected_pet
        
        result = await service.add_pet(pet_create)
        
        assert result == expected_pet
        mock_repository.add_pet.assert_called_once_with(pet_create)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_pet_repository_error(self, service, mock_repository):
        """Test add_pet when repository raises PetRepositoryError."""
        pet_create = PetCreate(name="Fluffy", type="cat", age=3)
        mock_repository.add_pet.side_effect = PetRepositoryError("DB error")
        
        with pytest.raises(PetServiceError):
            await service.add_pet(pet_create)
        
        mock_repository.add_pet.assert_called_once_with(pet_create)

    @pytest.mark.asyncio
    async def test_add_pet_commit_called(self, service, mock_repository, mock_session):
        """Test that session.commit() is called after adding a pet."""
        pet_create = PetCreate(name="Fluffy", type="cat", age=3)
        expected_pet = Pet(id=1, name="Fluffy", type="cat", age=3)
        mock_repository.add_pet.return_value = expected_pet
        
        await service.add_pet(pet_create)
        
        mock_session.commit.assert_called_once()


class TestGetPets:
    """Tests for PetService.get_pets()"""

    @pytest.mark.asyncio
    async def test_get_pets_success_with_pets(self, service, mock_repository):
        """Test successfully retrieving a list of pets."""
        pet1 = Pet(id=1, name="Fluffy", type="cat", age=3)
        pet2 = Pet(id=2, name="Whiskers", type="cat", age=5)
        pets = [pet1, pet2]
        mock_repository.get_pets.return_value = pets
        
        result = await service.get_pets()
        
        assert result == pets
        assert len(result) == 2
        mock_repository.get_pets.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pets_success_empty_list(self, service, mock_repository):
        """Test retrieving an empty list of pets."""
        mock_repository.get_pets.return_value = []
        
        result = await service.get_pets()
        
        assert result == []
        mock_repository.get_pets.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pets_repository_error(self, service, mock_repository):
        """Test get_pets when repository raises PetRepositoryError."""
        mock_repository.get_pets.side_effect = PetRepositoryError("DB error")
        
        with pytest.raises(PetServiceError):
            await service.get_pets()
        
        mock_repository.get_pets.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pets_no_commit(self, service, mock_repository, mock_session):
        """Test that session.commit() is NOT called for read operation."""
        pet = Pet(id=1, name="Fluffy", type="cat", age=3)
        mock_repository.get_pets.return_value = [pet]
        
        await service.get_pets()
        
        mock_session.commit.assert_not_called()


class TestGetPet:
    """Tests for PetService.get_pet()"""

    @pytest.mark.asyncio
    async def test_get_pet_success(self, service, mock_repository):
        """Test successfully retrieving a pet by ID."""
        pet = Pet(id=1, name="Fluffy", type="cat", age=3)
        mock_repository.get_pet.return_value = pet
        
        result = await service.get_pet(pet_id=1)
        
        assert result == pet
        mock_repository.get_pet.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_pet_not_found(self, service, mock_repository):
        """Test get_pet raises PetNotFoundError when pet does not exist."""
        mock_repository.get_pet.return_value = None
        
        with pytest.raises(PetNotFoundError):
            await service.get_pet(pet_id=999)
        
        mock_repository.get_pet.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_get_pet_repository_error(self, service, mock_repository):
        """Test get_pet when repository raises PetRepositoryError."""
        mock_repository.get_pet.side_effect = PetRepositoryError("DB error")
        
        with pytest.raises(PetServiceError):
            await service.get_pet(pet_id=1)
        
        mock_repository.get_pet.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_pet_no_commit(self, service, mock_repository, mock_session):
        """Test that session.commit() is NOT called for read operation."""
        pet = Pet(id=1, name="Fluffy", type="cat", age=3)
        mock_repository.get_pet.return_value = pet
        
        await service.get_pet(pet_id=1)
        
        mock_session.commit.assert_not_called()


class TestUpdatePet:
    """Tests for PetService.update_pet()"""

    @pytest.mark.asyncio
    async def test_update_pet_success(self, service, mock_repository, mock_session):
        """Test successfully updating a pet."""
        pet_update = PetUpdate(name="Updated Fluffy", age=4)
        updated_pet = Pet(id=1, name="Updated Fluffy", type="cat", age=4)
        mock_repository.update_pet.return_value = updated_pet
        
        result = await service.update_pet(pet_id=1, payload=pet_update)
        
        assert result == updated_pet
        mock_repository.update_pet.assert_called_once_with(1, pet_update)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_pet_not_found(self, service, mock_repository):
        """Test update_pet raises PetNotFoundError when pet does not exist."""
        pet_update = PetUpdate(name="Updated Fluffy", age=4)
        mock_repository.update_pet.return_value = None
        
        with pytest.raises(PetNotFoundError):
            await service.update_pet(pet_id=999, payload=pet_update)
        
        mock_repository.update_pet.assert_called_once_with(999, pet_update)

    @pytest.mark.asyncio
    async def test_update_pet_repository_error(self, service, mock_repository):
        """Test update_pet when repository raises PetRepositoryError."""
        pet_update = PetUpdate(name="Updated Fluffy", age=4)
        mock_repository.update_pet.side_effect = PetRepositoryError("DB error")
        
        with pytest.raises(PetServiceError):
            await service.update_pet(pet_id=1, payload=pet_update)
        
        mock_repository.update_pet.assert_called_once_with(1, pet_update)

    @pytest.mark.asyncio
    async def test_update_pet_commit_called(self, service, mock_repository, mock_session):
        """Test that session.commit() is called after updating a pet."""
        pet_update = PetUpdate(name="Updated Fluffy", age=4)
        updated_pet = Pet(id=1, name="Updated Fluffy", type="cat", age=4)
        mock_repository.update_pet.return_value = updated_pet
        
        await service.update_pet(pet_id=1, payload=pet_update)
        
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_pet_no_commit_on_not_found(self, service, mock_repository, mock_session):
        """Test that session.commit() is NOT called when pet not found."""
        pet_update = PetUpdate(name="Updated Fluffy", age=4)
        mock_repository.update_pet.return_value = None
        
        with pytest.raises(PetNotFoundError):
            await service.update_pet(pet_id=999, payload=pet_update)
        
        mock_session.commit.assert_not_called()


class TestDeletePet:
    """Tests for PetService.delete_pet()"""

    @pytest.mark.asyncio
    async def test_delete_pet_success(self, service, mock_repository, mock_session):
        """Test successfully deleting a pet."""
        mock_repository.delete_pet.return_value = True
        
        await service.delete_pet(pet_id=1)
        
        mock_repository.delete_pet.assert_called_once_with(1)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_pet_not_found(self, service, mock_repository):
        """Test delete_pet raises PetNotFoundError when pet does not exist."""
        mock_repository.delete_pet.return_value = False
        
        with pytest.raises(PetNotFoundError):
            await service.delete_pet(pet_id=999)
        
        mock_repository.delete_pet.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_delete_pet_repository_error(self, service, mock_repository):
        """Test delete_pet when repository raises PetRepositoryError."""
        mock_repository.delete_pet.side_effect = PetRepositoryError("DB error")
        
        with pytest.raises(PetServiceError):
            await service.delete_pet(pet_id=1)
        
        mock_repository.delete_pet.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_pet_commit_called(self, service, mock_repository, mock_session):
        """Test that session.commit() is called after deleting a pet."""
        mock_repository.delete_pet.return_value = True
        
        await service.delete_pet(pet_id=1)
        
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_pet_no_commit_on_not_found(self, service, mock_repository, mock_session):
        """Test that session.commit() is NOT called when pet not found."""
        mock_repository.delete_pet.return_value = False
        
        with pytest.raises(PetNotFoundError):
            await service.delete_pet(pet_id=999)
        
        mock_session.commit.assert_not_called()

