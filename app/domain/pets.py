from pydantic import BaseModel, ConfigDict


class PetBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    species: str
    breed: str
    color: str
    owner_name: str
    age: int


class Pet(PetBase):
    id: int


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: str | None = None
    species: str | None = None
    breed: str | None = None
    color: str | None = None
    owner_name: str | None = None
    age: int | None = None
