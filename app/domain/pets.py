from pydantic import BaseModel, ConfigDict


class PetBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    type: str
    age: int

class Pet(PetBase):
    id: int

class PetCreate(PetBase):
    pass


class PetUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    age: int | None = None