from fastapi.testclient import TestClient


class TestPetRouterAuthentication:
    """Tests for pet router authentication."""

    def test_invalid_access_token(
        self,
        client: TestClient,
        invalid_headers: dict[str, str],
    ) -> None:
        # Act
        response = client.get("/pets/", headers=invalid_headers)

        # Assert
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"
        assert response.json()["error"] == "INVALID_CREDENTIALS"

    def test_missing_access_token(self, client: TestClient) -> None:
        # Act
        response = client.get("/pets/")

        # Assert
        assert response.status_code == 401


class TestCreatePet:
    """Tests for POST /pets"""

    def test_create_pet_success(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test successfully creating a pet."""
        # Arrange
        payload = {
            "name": "Fluffy",
            "species": "cat",
            "breed": "Persian",
            "color": "white",
            "owner_name": "Alice",
            "age": 3,
        }

        # Act
        response = client.post(
            "/pets/",
            headers=valid_headers,
            json=payload,
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["name"] == "Fluffy"
        assert response.json()["species"] == "cat"
        assert response.json()["breed"] == "Persian"
        assert response.json()["color"] == "white"
        assert response.json()["owner_name"] == "Alice"
        assert response.json()["age"] == 3

    def test_create_pet_invalid_payload(
        self, client: TestClient, valid_headers: dict[str, str]
    ) -> None:
        """Test create_pet with invalid payload."""
        # Arrange
        payload = {"name": "Fluffy"}

        # Act
        response = client.post("/pets/", headers=valid_headers, json=payload)

        # Assert
        assert response.status_code == 422


class TestListPets:
    """Tests for GET /pets"""

    def test_list_pets_success(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test successfully listing pets."""
        # Arrange
        first_pet_payload = {
            "name": "Fluffy",
            "species": "cat",
            "breed": "Persian",
            "color": "white",
            "owner_name": "Alice",
            "age": 3,
        }
        second_pet_payload = {
            "name": "Rex",
            "species": "dog",
            "breed": "Labrador",
            "color": "brown",
            "owner_name": "Bob",
            "age": 5,
        }

        # Act
        client.post(
            "/pets/",
            headers=valid_headers,
            json=first_pet_payload,
        )
        client.post(
            "/pets/",
            headers=valid_headers,
            json=second_pet_payload,
        )
        response = client.get("/pets/", headers=valid_headers)

        # Assert
        assert response.status_code == 200
        pets = response.json()
        assert len(pets) == 2
        assert pets[0]["name"] == "Fluffy"
        assert pets[1]["name"] == "Rex"

    def test_list_pets_empty(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test listing pets when none exist."""
        # Act
        response = client.get("/pets/", headers=valid_headers)

        # Assert
        assert response.status_code == 200
        assert response.json() == []


class TestGetPet:
    """Tests for GET /pets/{pet_id}"""

    def test_get_pet_success(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test successfully getting a pet by ID."""
        # Arrange
        # Create a pet
        payload = {
            "name": "Fluffy",
            "species": "cat",
            "breed": "Persian",
            "color": "white",
            "owner_name": "Alice",
            "age": 3,
        }
        # Act
        create_response = client.post(
            "/pets/",
            headers=valid_headers,
            json=payload,
        )
        pet_id = create_response.json()["id"]
        response = client.get(f"/pets/{pet_id}", headers=valid_headers)

        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == pet_id
        assert response.json()["name"] == "Fluffy"

    def test_get_pet_not_found(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test getting a pet that doesn't exist."""
        # Act
        response = client.get("/pets/999", headers=valid_headers)

        # Assert
        assert response.status_code == 404


class TestUpdatePet:
    """Tests for PATCH /pets/{pet_id}"""

    def test_update_pet_success(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test successfully updating a pet."""
        # Arrange
        # Create a pet
        create_payload = {
            "name": "Fluffy",
            "species": "cat",
            "breed": "Persian",
            "color": "white",
            "owner_name": "Alice",
            "age": 3,
        }

        # Act
        create_response = client.post(
            "/pets/",
            headers=valid_headers,
            json=create_payload,
        )
        pet_id = create_response.json()["id"]
        payload = {"name": "Updated Fluffy", "age": 4}
        response = client.patch(f"/pets/{pet_id}", headers=valid_headers, json=payload)

        # Assert
        assert response.status_code == 200
        assert response.json()["age"] == 4
        assert response.json()["name"] == "Updated Fluffy"

    def test_update_pet_not_found(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test updating a pet that doesn't exist."""
        payload = {"name": "Updated Fluffy", "age": 4}

        # Act
        response = client.patch("/pets/999", headers=valid_headers, json=payload)

        # Assert
        assert response.status_code == 404

    def test_update_pet_partial(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test updating only some pet fields."""
        # Arrange
        # Create a pet
        create_payload = {
            "name": "Fluffy",
            "species": "cat",
            "breed": "Persian",
            "color": "white",
            "owner_name": "Alice",
            "age": 3,
        }

        # Act
        create_response = client.post(
            "/pets/",
            headers=valid_headers,
            json=create_payload,
        )
        pet_id = create_response.json()["id"]
        payload = {"age": 4}
        response = client.patch(f"/pets/{pet_id}", headers=valid_headers, json=payload)

        # Assert
        assert response.status_code == 200
        assert response.json()["age"] == 4

    def test_update_preserves_unmodified_fields(
        self, client: TestClient, valid_headers: dict[str, str]
    ) -> None:
        """Test that updating some fields preserves others."""
        # Arrange
        create_payload = {
            "name": "Shadow",
            "species": "cat",
            "breed": "Siamese",
            "color": "cream",
            "owner_name": "Charlie",
            "age": 5,
        }
        create_response = client.post(
            "/pets/",
            headers=valid_headers,
            json=create_payload,
        )
        pet_id = create_response.json()["id"]
        original_species = create_response.json()["species"]
        original_breed = create_response.json()["breed"]
        original_color = create_response.json()["color"]
        original_owner = create_response.json()["owner_name"]
        payload = {"name": "Whiskers"}

        # Act
        update_response = client.patch(f"/pets/{pet_id}", headers=valid_headers, json=payload)
        # Assert
        assert update_response.status_code == 200
        # Verify other fields are preserved
        get_response = client.get(f"/pets/{pet_id}", headers=valid_headers)
        assert get_response.json()["name"] == "Whiskers"
        assert get_response.json()["species"] == original_species
        assert get_response.json()["breed"] == original_breed
        assert get_response.json()["color"] == original_color
        assert get_response.json()["owner_name"] == original_owner


class TestDeletePet:
    """Tests for DELETE /pets/{pet_id}"""

    def test_delete_pet_success(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test successfully deleting a pet."""
        # Arrange
        # Create a pet
        payload = {
            "name": "Fluffy",
            "species": "cat",
            "breed": "Persian",
            "color": "white",
            "owner_name": "Alice",
            "age": 3,
        }
        create_response = client.post(
            "/pets/",
            headers=valid_headers,
            json=payload,
        )
        pet_id = create_response.json()["id"]

        # Act
        response = client.delete(f"/pets/{pet_id}", headers=valid_headers)

        # Assert
        assert response.status_code == 204

    def test_delete_pet_not_found(self, client: TestClient, valid_headers: dict[str, str]) -> None:
        """Test deleting a pet that doesn't exist."""
        # Act
        response = client.delete("/pets/999", headers=valid_headers)

        # Assert
        assert response.status_code == 404


class TestIntegrationScenarios:
    """Additional integration tests for realistic scenarios."""

    def test_create_and_immediate_retrieval(
        self, client: TestClient, valid_headers: dict[str, str]
    ) -> None:
        """Test that created pet is immediately retrievable within transaction."""
        # Arrange
        payload = {
            "name": "Buddy",
            "species": "dog",
            "breed": "Golden Retriever",
            "color": "golden",
            "owner_name": "David",
            "age": 2,
        }
        create_response = client.post(
            "/pets/",
            headers=valid_headers,
            json=payload,
        )
        pet_id = create_response.json()["id"]

        # Act
        get_response = client.get(f"/pets/{pet_id}", headers=valid_headers)

        # Assert
        assert get_response.status_code == 200
        assert get_response.json()["id"] == pet_id
        assert get_response.json()["name"] == "Buddy"

    def test_complete_crud_lifecycle(
        self, client: TestClient, valid_headers: dict[str, str]
    ) -> None:
        """Test complete CRUD lifecycle: create, read, update, delete."""
        # Arrange
        # Create
        create_payload = {
            "name": "Max",
            "species": "cat",
            "breed": "Tabby",
            "color": "orange",
            "owner_name": "Eve",
            "age": 1,
        }
        create_response = client.post(
            "/pets/",
            headers=valid_headers,
            json=create_payload,
        )
        assert create_response.status_code == 201
        pet_id = create_response.json()["id"]
        update_payload = {"name": "Max Jr", "age": 2}

        # Act
        get_response = client.get(f"/pets/{pet_id}", headers=valid_headers)
        # Assert
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Max"

        # Act
        update_response = client.patch(
            f"/pets/{pet_id}", headers=valid_headers, json=update_payload
        )
        # Assert
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Max Jr"
        assert update_response.json()["age"] == 2

        # Act
        delete_response = client.delete(f"/pets/{pet_id}", headers=valid_headers)
        # Assert
        assert delete_response.status_code == 204

        # Act
        not_found_response = client.get(f"/pets/{pet_id}", headers=valid_headers)
        # Assert
        assert not_found_response.status_code == 404

    def test_multiple_pets_list_and_delete(
        self, client: TestClient, valid_headers: dict[str, str]
    ) -> None:
        """Test listing multiple pets and verifying deletion updates the list."""
        # Arrange
        # Create three pets
        first_pet_payload = {
            "name": "Fluffy",
            "species": "cat",
            "breed": "Persian",
            "color": "white",
            "owner_name": "Alice",
            "age": 2,
        }
        second_pet_payload = {
            "name": "Rex",
            "species": "dog",
            "breed": "Labrador",
            "color": "brown",
            "owner_name": "Bob",
            "age": 4,
        }
        third_pet_payload = {
            "name": "Tweety",
            "species": "bird",
            "breed": "Parrot",
            "color": "green",
            "owner_name": "Frank",
            "age": 1,
        }

        # Act
        pet1 = client.post(
            "/pets/",
            headers=valid_headers,
            json=first_pet_payload,
        )
        pet1_id = pet1.json()["id"]

        pet2 = client.post(
            "/pets/",
            headers=valid_headers,
            json=second_pet_payload,
        )
        pet2_id = pet2.json()["id"]

        pet3 = client.post(
            "/pets/",
            headers=valid_headers,
            json=third_pet_payload,
        )
        pet3_id = pet3.json()["id"]
        list_response = client.get("/pets/", headers=valid_headers)
        # Assert
        assert list_response.status_code == 200
        assert len(list_response.json()) == 3

        # Act
        delete_response = client.delete(f"/pets/{pet2_id}", headers=valid_headers)
        # Assert
        assert delete_response.status_code == 204

        # List should have 2 pets now
        # Act
        list_response = client.get("/pets/", headers=valid_headers)
        # Assert
        assert len(list_response.json()) == 2

        # Verify deleted pet is gone
        # Act
        get_response = client.get(f"/pets/{pet2_id}", headers=valid_headers)
        # Assert
        assert get_response.status_code == 404

        # Verify other pets still exist
        # Act
        get_response1 = client.get(f"/pets/{pet1_id}", headers=valid_headers)
        # Assert
        assert get_response1.status_code == 200
        assert get_response1.json()["name"] == "Fluffy"

        # Act
        get_response3 = client.get(f"/pets/{pet3_id}", headers=valid_headers)
        # Assert
        assert get_response3.status_code == 200
        assert get_response3.json()["name"] == "Tweety"
