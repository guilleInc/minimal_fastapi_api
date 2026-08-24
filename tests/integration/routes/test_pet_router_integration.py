"""Integration tests for pet routes with real database."""

import pytest


class TestCreateAndRetrievePet:
    """Integration test: create a pet and immediately retrieve it."""

    @pytest.mark.asyncio
    async def test_create_pet_then_get(self, client):
        """Test POST creates pet and GET retrieves it in same transaction."""
        # Create pet
        create_response = await client.post(
            "/pets/",
            json={"name": "Fluffy", "type": "cat", "age": 3}
        )
        assert create_response.status_code == 201
        pet = create_response.json()
        pet_id = pet["id"]
        assert pet["name"] == "Fluffy"
        assert pet["type"] == "cat"
        assert pet["age"] == 3

        # Retrieve pet (same test transaction)
        get_response = await client.get(f"/pets/{pet_id}")
        assert get_response.status_code == 200
        retrieved = get_response.json()
        assert retrieved["id"] == pet_id
        assert retrieved["name"] == "Fluffy"


class TestFullPetWorkflow:
    """Integration test: full workflow (create, read, update, delete)."""

    @pytest.mark.asyncio
    async def test_complete_pet_lifecycle(self, client):
        """Test complete workflow: create → read → update → delete."""
        # CREATE
        create_response = await client.post(
            "/pets/",
            json={"name": "Rex", "type": "dog", "age": 2}
        )
        assert create_response.status_code == 201
        pet_id = create_response.json()["id"]

        # READ
        get_response = await client.get(f"/pets/{pet_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Rex"

        # UPDATE
        update_response = await client.put(
            f"/pets/{pet_id}",
            json={"age": 3}
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["age"] == 3
        assert updated["name"] == "Rex"  # Unchanged

        # VERIFY UPDATE
        get_response = await client.get(f"/pets/{pet_id}")
        assert get_response.json()["age"] == 3

        # DELETE
        delete_response = await client.delete(f"/pets/{pet_id}")
        assert delete_response.status_code == 204

        # VERIFY DELETED
        get_response = await client.get(f"/pets/{pet_id}")
        assert get_response.status_code == 404


class TestMultiplePetsInteraction:
    """Integration test: multiple pets in same transaction."""

    @pytest.mark.asyncio
    async def test_create_multiple_and_list(self, client):
        """Test creating multiple pets and listing them."""
        # Create first pet
        response1 = await client.post(
            "/pets/",
            json={"name": "Fluffy", "type": "cat", "age": 3}
        )
        assert response1.status_code == 201

        # Create second pet
        response2 = await client.post(
            "/pets/",
            json={"name": "Rex", "type": "dog", "age": 5}
        )
        assert response2.status_code == 201

        # List pets (should see both)
        list_response = await client.get("/pets/")
        assert list_response.status_code == 200
        pets = list_response.json()
        assert len(pets) == 2
        names = {pet["name"] for pet in pets}
        assert names == {"Fluffy", "Rex"}

    @pytest.mark.asyncio
    async def test_create_and_delete_preserves_others(self, client):
        """Test that deleting one pet doesn't affect others."""
        # Create first pet
        response1 = await client.post(
            "/pets/",
            json={"name": "Fluffy", "type": "cat", "age": 3}
        )
        pet1_id = response1.json()["id"]

        # Create second pet
        response2 = await client.post(
            "/pets/",
            json={"name": "Rex", "type": "dog", "age": 5}
        )
        pet2_id = response2.json()["id"]

        # Delete first pet
        delete_response = await client.delete(f"/pets/{pet1_id}")
        assert delete_response.status_code == 204

        # Verify second pet still exists
        get_response = await client.get(f"/pets/{pet2_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Rex"

        # Verify list has only second pet
        list_response = await client.get("/pets/")
        pets = list_response.json()
        assert len(pets) == 1
        assert pets[0]["name"] == "Rex"


class TestPetValidation:
    """Integration test: validation works with real database."""

    @pytest.mark.asyncio
    async def test_create_pet_invalid_payload(self, client):
        """Test that validation rejects invalid data."""
        response = await client.post(
            "/pets/",
            json={"name": "Fluffy"}  # Missing type and age
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_pet_with_invalid_data(self, client):
        """Test that updates validate input."""
        # Create pet first
        create_response = await client.post(
            "/pets/",
            json={"name": "Fluffy", "type": "cat", "age": 3}
        )
        pet_id = create_response.json()["id"]

        # Try invalid update
        update_response = await client.put(
            f"/pets/{pet_id}",
            json={"age": "not-a-number"}
        )
        assert update_response.status_code == 422


class TestErrorHandling:
    """Integration test: error handling with real database."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_pet(self, client):
        """Test 404 when pet doesn't exist."""
        response = await client.get("/pets/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_nonexistent_pet(self, client):
        """Test 404 when updating non-existent pet."""
        response = await client.put(
            "/pets/999",
            json={"age": 5}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_pet(self, client):
        """Test 404 when deleting non-existent pet."""
        response = await client.delete("/pets/999")
        assert response.status_code == 404
