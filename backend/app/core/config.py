from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fitness-tracker-api"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://fitness:fitness_dev_password@db:5432/fitness_tracker"
    secret_key: str = "change-me-in-development"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()
