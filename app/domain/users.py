from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password_hash: str
    is_active: bool = True


class User(UserBase):
    id: int


class UserCreate(BaseModel):
    username: str
    password: str


class UserCreateDB(BaseModel):
    username: str
    password_hash: str
    is_active: bool
