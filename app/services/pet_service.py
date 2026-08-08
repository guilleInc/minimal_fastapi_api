from app.repositories.pet_repository import PetRepository
from app.schemas.pet_schema import Pet, PetCreate, PetUpdate


class PetService:
    def __init__(self, repository: PetRepository) -> None:
        self.repository = repository

    def add_pet(self, payload: PetCreate) -> Pet:
        return self.repository.add_pet(payload)

    def get_pets(self) -> list[Pet]:
        return self.repository.get_pets()

    def get_pet(self, pet_id: int) -> Pet:
        pet = self.repository.get_pet(pet_id)
        if pet is None:
            raise ValueError(f"Pet with id {pet_id} not found")
        return pet

    def update_pet(self, pet_id: int, payload: PetUpdate) -> Pet:
        pet = self.repository.update_pet(pet_id, payload)
        if pet is None:
            raise ValueError(f"Pet with id {pet_id} not found")
        return pet

    def delete_pet(self, pet_id: int) -> None:
        if not self.repository.delete_pet(pet_id):
            raise ValueError(f"Pet with id {pet_id} not found")
