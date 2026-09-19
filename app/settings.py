from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    environment: str = "development"
    database_path: str = "./pets.db"
    image_upload_dir: str = "uploads/pets"
    image_max_size_bytes: int = 5 * 1024 * 1024

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.database_path}"
