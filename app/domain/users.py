from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool


class User(UserBase):
    id: int


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
