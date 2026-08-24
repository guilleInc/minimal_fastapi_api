"""Unit tests for pet routes."""

from app.domain.pets import Pet
from app.services.pet_service_errors import PetNotFoundError, PetServiceError


class TestCreatePet:
    """Tests for POST /pets"""

    def test_create_pet_success(self, client, mock_pet_service):
        """Test successfully creating a pet."""
        pet = Pet(id=1, name="Fluffy", type="cat", age=3)
        mock_pet_service.add_pet.return_value = pet

        response = client.post("/pets", json={"name": "Fluffy", "type": "cat", "age": 3})

        assert response.status_code == 201
        assert response.json()["name"] == "Fluffy"
        assert response.json()["id"] == 1
        mock_pet_service.add_pet.assert_called_once()

    def test_create_pet_service_error(self, client, mock_pet_service):
        """Test create_pet when service raises PetServiceError."""
        mock_pet_service.add_pet.side_effect = PetServiceError()

        response = client.post("/pets", json={"name": "Fluffy", "type": "cat", "age": 3})

        assert response.status_code == 500

    def test_create_pet_invalid_payload(self, client):
        """Test create_pet with invalid payload."""
        response = client.post("/pets", json={"name": "Fluffy"})

        assert response.status_code == 422


class TestListPets:
    """Tests for GET /pets"""

    def test_list_pets_success(self, client, mock_pet_service):
        """Test successfully listing pets."""
        pet1 = Pet(id=1, name="Fluffy", type="cat", age=3)
        pet2 = Pet(id=2, name="Rex", type="dog", age=5)
        mock_pet_service.get_pets.return_value = [pet1, pet2]

        response = client.get("/pets")

        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["name"] == "Fluffy"
        assert response.json()[1]["name"] == "Rex"
        mock_pet_service.get_pets.assert_called_once()

    def test_list_pets_empty(self, client, mock_pet_service):
        """Test listing pets when none exist."""
        mock_pet_service.get_pets.return_value = []

        response = client.get("/pets")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_pets_service_error(self, client, mock_pet_service):
        """Test list_pets when service raises PetServiceError."""
        mock_pet_service.get_pets.side_effect = PetServiceError()

        response = client.get("/pets")

        assert response.status_code == 500


class TestGetPet:
    """Tests for GET /pets/{pet_id}"""

    def test_get_pet_success(self, client, mock_pet_service):
        """Test successfully getting a pet by ID."""
        pet = Pet(id=1, name="Fluffy", type="cat", age=3)
        mock_pet_service.get_pet.return_value = pet

        response = client.get("/pets/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["name"] == "Fluffy"
        mock_pet_service.get_pet.assert_called_once_with(1)

    def test_get_pet_not_found(self, client, mock_pet_service):
        """Test getting a pet that doesn't exist."""
        mock_pet_service.get_pet.side_effect = PetNotFoundError()

        response = client.get("/pets/999")

        assert response.status_code == 404

    def test_get_pet_service_error(self, client, mock_pet_service):
        """Test get_pet when service raises PetServiceError."""
        mock_pet_service.get_pet.side_effect = PetServiceError()

        response = client.get("/pets/1")

        assert response.status_code == 500


class TestUpdatePet:
    """Tests for PUT /pets/{pet_id}"""

    def test_update_pet_success(self, client, mock_pet_service):
        """Test successfully updating a pet."""
        updated_pet = Pet(id=1, name="Updated Fluffy", type="cat", age=4)
        mock_pet_service.update_pet.return_value = updated_pet

        response = client.put("/pets/1", json={"name": "Updated Fluffy", "age": 4})

        assert response.status_code == 200
        assert response.json()["age"] == 4
        assert response.json()["name"] == "Updated Fluffy"
        mock_pet_service.update_pet.assert_called_once()

    def test_update_pet_not_found(self, client, mock_pet_service):
        """Test updating a pet that doesn't exist."""
        mock_pet_service.update_pet.side_effect = PetNotFoundError()

        response = client.put("/pets/999", json={"name": "Updated Fluffy", "age": 4})

        assert response.status_code == 404

    def test_update_pet_service_error(self, client, mock_pet_service):
        """Test update_pet when service raises PetServiceError."""
        mock_pet_service.update_pet.side_effect = PetServiceError()

        response = client.put("/pets/1", json={"name": "Updated Fluffy", "age": 4})

        assert response.status_code == 500

    def test_update_pet_partial(self, client, mock_pet_service):
        """Test updating only some pet fields."""
        updated_pet = Pet(id=1, name="Fluffy", type="cat", age=4)
        mock_pet_service.update_pet.return_value = updated_pet

        response = client.put("/pets/1", json={"age": 4})

        assert response.status_code == 200
        assert response.json()["age"] == 4


class TestDeletePet:
    """Tests for DELETE /pets/{pet_id}"""

    def test_delete_pet_success(self, client, mock_pet_service):
        """Test successfully deleting a pet."""
        mock_pet_service.delete_pet.return_value = None

        response = client.delete("/pets/1")

        assert response.status_code == 204
        mock_pet_service.delete_pet.assert_called_once_with(1)

    def test_delete_pet_not_found(self, client, mock_pet_service):
        """Test deleting a pet that doesn't exist."""
        mock_pet_service.delete_pet.side_effect = PetNotFoundError()

        response = client.delete("/pets/999")

        assert response.status_code == 404

    def test_delete_pet_service_error(self, client, mock_pet_service):
        """Test delete_pet when service raises PetServiceError."""
        mock_pet_service.delete_pet.side_effect = PetServiceError()

        response = client.delete("/pets/1")

        assert response.status_code == 500
