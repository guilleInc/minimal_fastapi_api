from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PetBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    name: str = Field(min_length=1, max_length=100)
    species: str = Field(min_length=1, max_length=50)
    breed: str = Field(min_length=1, max_length=100)
    color: str = Field(min_length=1, max_length=50)
    owner_name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=100)


class PetSchema(PetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=1)


class PetCreateSchema(PetBase): ...


class PetUpdateSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    name: str | None = Field(default=None, min_length=1, max_length=100)
    species: str | None = Field(default=None, min_length=1, max_length=50)
    breed: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=1, max_length=50)
    owner_name: str | None = Field(default=None, min_length=1, max_length=100)
    age: int | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def require_one_update_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for an update")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Update fields must not be null")
        return self
