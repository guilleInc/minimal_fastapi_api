from fastapi.testclient import TestClient


class TestCreatePet:
    """Tests for POST /pets"""

    def test_create_pet_success(self, client: TestClient) -> None:
        """Test successfully creating a pet."""
        response = client.post(
            "/pets/",
            json={
                "name": "Fluffy",
                "species": "cat",
                "breed": "Persian",
                "color": "white",
                "owner_name": "Alice",
                "age": 3,
            },
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Fluffy"
        assert response.json()["species"] == "cat"
        assert response.json()["breed"] == "Persian"
        assert response.json()["color"] == "white"
        assert response.json()["owner_name"] == "Alice"
        assert response.json()["age"] == 3

    def test_create_pet_invalid_payload(self, client: TestClient) -> None:
        """Test create_pet with invalid payload."""
        response = client.post("/pets/", json={"name": "Fluffy"})

        assert response.status_code == 422


class TestListPets:
    """Tests for GET /pets"""

    def test_list_pets_success(self, client: TestClient) -> None:
        """Test successfully listing pets."""
        # Create two pets
        client.post(
            "/pets/",
            json={
                "name": "Fluffy",
                "species": "cat",
                "breed": "Persian",
                "color": "white",
                "owner_name": "Alice",
                "age": 3,
            },
        )
        client.post(
            "/pets/",
            json={
                "name": "Rex",
                "species": "dog",
                "breed": "Labrador",
                "color": "brown",
                "owner_name": "Bob",
                "age": 5,
            },
        )

        response = client.get("/pets/")

        assert response.status_code == 200
        pets = response.json()
        assert len(pets) == 2
        assert pets[0]["name"] == "Fluffy"
        assert pets[1]["name"] == "Rex"

    def test_list_pets_empty(self, client: TestClient) -> None:
        """Test listing pets when none exist."""
        response = client.get("/pets/")

        assert response.status_code == 200
        assert response.json() == []


class TestGetPet:
    """Tests for GET /pets/{pet_id}"""

    def test_get_pet_success(self, client: TestClient) -> None:
        """Test successfully getting a pet by ID."""
        # Create a pet
        create_response = client.post(
            "/pets/",
            json={
                "name": "Fluffy",
                "species": "cat",
                "breed": "Persian",
                "color": "white",
                "owner_name": "Alice",
                "age": 3,
            },
        )
        pet_id = create_response.json()["id"]

        response = client.get(f"/pets/{pet_id}")

        assert response.status_code == 200
        assert response.json()["id"] == pet_id
        assert response.json()["name"] == "Fluffy"

    def test_get_pet_not_found(self, client: TestClient) -> None:
        """Test getting a pet that doesn't exist."""
        response = client.get("/pets/999")

        assert response.status_code == 404


class TestUpdatePet:
    """Tests for PATCH /pets/{pet_id}"""

    def test_update_pet_success(self, client: TestClient) -> None:
        """Test successfully updating a pet."""
        # Create a pet
        create_response = client.post(
            "/pets/",
            json={
                "name": "Fluffy",
                "species": "cat",
                "breed": "Persian",
                "color": "white",
                "owner_name": "Alice",
                "age": 3,
            },
        )
        pet_id = create_response.json()["id"]

        response = client.patch(f"/pets/{pet_id}", json={"name": "Updated Fluffy", "age": 4})

        assert response.status_code == 200
        assert response.json()["age"] == 4
        assert response.json()["name"] == "Updated Fluffy"

    def test_update_pet_not_found(self, client: TestClient) -> None:
        """Test updating a pet that doesn't exist."""
        response = client.patch("/pets/999", json={"name": "Updated Fluffy", "age": 4})

        assert response.status_code == 404

    def test_update_pet_partial(self, client: TestClient) -> None:
        """Test updating only some pet fields."""
        # Create a pet
        create_response = client.post(
            "/pets/",
            json={
                "name": "Fluffy",
                "species": "cat",
                "breed": "Persian",
                "color": "white",
                "owner_name": "Alice",
                "age": 3,
            },
        )
        pet_id = create_response.json()["id"]

        response = client.patch(f"/pets/{pet_id}", json={"age": 4})

        assert response.status_code == 200
        assert response.json()["age"] == 4

    def test_update_preserves_unmodified_fields(self, client: TestClient) -> None:
        """Test that updating some fields preserves others."""
        create_response = client.post(
            "/pets/",
            json={
                "name": "Shadow",
                "species": "cat",
                "breed": "Siamese",
                "color": "cream",
                "owner_name": "Charlie",
                "age": 5,
            },
        )
        pet_id = create_response.json()["id"]
        original_species = create_response.json()["species"]
        original_breed = create_response.json()["breed"]
        original_color = create_response.json()["color"]
        original_owner = create_response.json()["owner_name"]

        # Update only name
        update_response = client.patch(f"/pets/{pet_id}", json={"name": "Whiskers"})
        assert update_response.status_code == 200

        # Verify other fields are preserved
        get_response = client.get(f"/pets/{pet_id}")
        assert get_response.json()["name"] == "Whiskers"
        assert get_response.json()["species"] == original_species
        assert get_response.json()["breed"] == original_breed
        assert get_response.json()["color"] == original_color
        assert get_response.json()["owner_name"] == original_owner


class TestDeletePet:
    """Tests for DELETE /pets/{pet_id}"""

    def test_delete_pet_success(self, client: TestClient) -> None:
        """Test successfully deleting a pet."""
        # Create a pet
        create_response = client.post(
            "/pets/",
            json={
                "name": "Fluffy",
                "species": "cat",
                "breed": "Persian",
                "color": "white",
                "owner_name": "Alice",
                "age": 3,
            },
        )
        pet_id = create_response.json()["id"]

        response = client.delete(f"/pets/{pet_id}")

        assert response.status_code == 204

    def test_delete_pet_not_found(self, client: TestClient) -> None:
        """Test deleting a pet that doesn't exist."""
        response = client.delete("/pets/999")

        assert response.status_code == 404


class TestIntegrationScenarios:
    """Additional integration tests for realistic scenarios."""

    def test_create_and_immediate_retrieval(self, client: TestClient) -> None:
        """Test that created pet is immediately retrievable within transaction."""
        create_response = client.post(
            "/pets/",
            json={
                "name": "Buddy",
                "species": "dog",
                "breed": "Golden Retriever",
                "color": "golden",
                "owner_name": "David",
                "age": 2,
            },
        )
        pet_id = create_response.json()["id"]

        get_response = client.get(f"/pets/{pet_id}")

        assert get_response.status_code == 200
        assert get_response.json()["id"] == pet_id
        assert get_response.json()["name"] == "Buddy"

    def test_complete_crud_lifecycle(self, client: TestClient) -> None:
        """Test complete CRUD lifecycle: create, read, update, delete."""
        # Create
        create_response = client.post(
            "/pets/",
            json={
                "name": "Max",
                "species": "cat",
                "breed": "Tabby",
                "color": "orange",
                "owner_name": "Eve",
                "age": 1,
            },
        )
        assert create_response.status_code == 201
        pet_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/pets/{pet_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Max"

        # Update
        update_response = client.patch(f"/pets/{pet_id}", json={"name": "Max Jr", "age": 2})
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Max Jr"
        assert update_response.json()["age"] == 2

        # Delete
        delete_response = client.delete(f"/pets/{pet_id}")
        assert delete_response.status_code == 204

        # Verify deleted
        not_found_response = client.get(f"/pets/{pet_id}")
        assert not_found_response.status_code == 404

    def test_multiple_pets_list_and_delete(self, client: TestClient) -> None:
        """Test listing multiple pets and verifying deletion updates the list."""
        # Create three pets
        pet1 = client.post(
            "/pets/",
            json={
                "name": "Fluffy",
                "species": "cat",
                "breed": "Persian",
                "color": "white",
                "owner_name": "Alice",
                "age": 2,
            },
        )
        pet1_id = pet1.json()["id"]

        pet2 = client.post(
            "/pets/",
            json={
                "name": "Rex",
                "species": "dog",
                "breed": "Labrador",
                "color": "brown",
                "owner_name": "Bob",
                "age": 4,
            },
        )
        pet2_id = pet2.json()["id"]

        pet3 = client.post(
            "/pets/",
            json={
                "name": "Tweety",
                "species": "bird",
                "breed": "Parrot",
                "color": "green",
                "owner_name": "Frank",
                "age": 1,
            },
        )
        pet3_id = pet3.json()["id"]

        # List all pets
        list_response = client.get("/pets/")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 3

        # Delete middle pet
        delete_response = client.delete(f"/pets/{pet2_id}")
        assert delete_response.status_code == 204

        # List should have 2 pets now
        list_response = client.get("/pets/")
        assert len(list_response.json()) == 2

        # Verify deleted pet is gone
        get_response = client.get(f"/pets/{pet2_id}")
        assert get_response.status_code == 404

        # Verify other pets still exist
        get_response1 = client.get(f"/pets/{pet1_id}")
        assert get_response1.status_code == 200
        assert get_response1.json()["name"] == "Fluffy"

        get_response3 = client.get(f"/pets/{pet3_id}")
        assert get_response3.status_code == 200
        assert get_response3.json()["name"] == "Tweety"
