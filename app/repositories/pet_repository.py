from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from app.models.pet_model import Pet
from app.schemas.pet_schema import PetCreate, PetUpdate


class PetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_pet(self, payload: PetCreate) -> Pet:
        stmt = insert(Pet).values(**payload.model_dump()).returning(Pet)
        pet = self.session.scalar(stmt)
        self.session.commit()
        return pet

    def get_pets(self) -> list[Pet]:
        stmt = select(Pet)
        return list(self.session.scalars(stmt).all())

    def get_pet(self, pet_id: int) -> Pet | None:
        stmt = select(Pet).where(Pet.id == pet_id)
        return self.session.scalar(stmt)

    def update_pet(self, pet_id: int, payload: PetUpdate) -> Pet | None:
        pet = self.get_pet(pet_id)
        if pet is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        stmt = update(Pet).where(Pet.id == pet_id).values(**update_data).returning(Pet)
        updated_pet = self.session.scalar(stmt)
        self.session.commit()
        return updated_pet

    def delete_pet(self, pet_id: int) -> bool:
        stmt = delete(Pet).where(Pet.id == pet_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0
