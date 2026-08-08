from pydantic import BaseModel


class PetBase(BaseModel):
    name: str
    type: str
    age: int


class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    age: int | None = None


class Pet(PetBase):
    id: int
