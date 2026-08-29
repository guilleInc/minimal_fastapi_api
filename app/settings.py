from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret_key: str = "key-tests"
    jwt_algorithm: str = "HS256"
