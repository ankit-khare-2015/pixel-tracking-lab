from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "pixel-tracking-lab-backend"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://pixel:pixel@postgres:5432/pixel_lab"
    allowed_origins: str = "http://localhost:8080"
    db_connect_retries: int = 20
    db_retry_sleep_seconds: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
