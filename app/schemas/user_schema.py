from pydantic import BaseModel, ConfigDict, Field


class UserInSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)
