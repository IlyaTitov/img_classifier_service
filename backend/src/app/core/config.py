import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/img_classifier"
    )
    database_echo: bool = False

    # Files
    upload_dir: str = "/app/uploads"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    # Redis: отдельная БД /1 для кэша
    redis_url: str = "redis://localhost:6379/1"

    # YOLO
    yolo_model_path: str = "yolov8s.pt"

    # CORS
    cors_origins: str = "http://localhost,http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def originals_dir(self) -> str:
        """Каталог для оригинальных загруженных файлов."""
        return os.path.join(self.upload_dir, "originals")

    @property
    def processed_dir(self) -> str:
        """Каталог для файлов с нанесёнными рамками детекций."""
        return os.path.join(self.upload_dir, "processed")


setting = Setting()
