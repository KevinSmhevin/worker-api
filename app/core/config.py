from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "worker-api"
    app_env: str = "development"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/worker_api"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    sentry_dsn: str = ""

    storage_backend: str = "local"
    s3_bucket_name: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint_url: str = ""
    local_storage_path: str = "./storage"

    default_request_timeout: int = 30
    max_retries: int = 3
    rate_limit_delay: float = 2.0

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


def get_settings() -> Settings:
    return Settings()
