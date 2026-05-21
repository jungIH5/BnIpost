from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "BnIpost Python Server"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://bnipost:bnipost@db:5432/bnipost"

    # JWT (same secret as Java server for verification)
    jwt_secret: str = "change-this-secret-key-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"

    # Internal API key (for calling Java server)
    internal_api_key: str = "internal-secret"
    java_server_url: str = "http://java:8080"

    # Claude API
    anthropic_api_key: str

    # Redis
    redis_url: str = "redis://redis:6379"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
