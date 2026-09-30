from pydantic_settings import BaseSettings, SettingsConfigDict


class ImageSettings:
    MAX_SIZE_BYTES = 5 * 1024 * 1024
    MAX_INPUT_DIMENSION = 4096
    MAX_OUTPUT_DIMENSION = 2048
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
    ALLOWED_FORMATS = {
        "JPEG",
        "PNG",
        "WEBP",
    }


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
    image_url_prefix: str = "/uploads/pets"
    image_max_size_bytes: int = 5 * 1024 * 1024
    image_max_input_dimension: int = 4096
    image_max_output_dimension: int = 2048

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.database_path}"


settings = Settings()
image_settings = ImageSettings()
