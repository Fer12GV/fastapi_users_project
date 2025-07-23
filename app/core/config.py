from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl
from typing import Optional, List
from enum import Enum
from pathlib import Path
import os

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


def detect_env_file() -> str:
    """Detect whether to use .env or .env.docker based on environment or Docker context."""
    if Path("/.dockerenv").exists():
        return ".env.docker"
    return os.getenv("ENV_FILE", ".env")


class BaseConfig(BaseSettings):
    # === Application ===
    APP_NAME: str = "FastAPI Users API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API de gestión de usuarios con autenticación JWT"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    # === Web Server ===
    HOST: str = "0.0.0.0"
    WEB_PORT: int = 8000

    # === JWT ===
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === CORS ===
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["*"])
    ALLOWED_ORIGINS: List[AnyHttpUrl] = Field(default_factory=lambda: [])

    # === Database ===
    DATABASE_URL: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SCHEMA: str = "fastapi_users"
    DB_APP_USER: str
    DB_APP_PASSWORD: str

    # === Logging ===
    LOG_LEVEL: str = "INFO"

    # === Gunicorn ===
    GUNICORN_WORKERS: int = 2
    WORKER_CONNECTIONS: int = 1000
    WORKER_TIMEOUT: int = 30
    KEEPALIVE: int = 2
    MAX_REQUESTS: int = 1000
    MAX_REQUESTS_JITTER: int = 100
    GRACEFUL_TIMEOUT: int = 30

    # === Redis ===
    REDIS_PORT: int = 6379

    # === SSL ===
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    SSL_CA_CERTS: Optional[str] = None
    SSL_CERT_REQS: Optional[int] = 0

    # === Monitoring ===
    ENABLE_METRICS: bool = True
    ENABLE_HEALTH_CHECKS: bool = True
    ENABLE_SECURITY_HEADERS: bool = True

    class Config:
        env_file = detect_env_file()
        case_sensitive = True


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    GUNICORN_WORKERS: int = 1


class StagingConfig(BaseConfig):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"


class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-here-change-in-production":
            raise ValueError("SECRET_KEY must be set in production!")

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in production!")

        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long in production!")

        if self.DEBUG:
            raise ValueError("DEBUG must be False in production!")

        if "*" in self.ALLOWED_ORIGINS:
            raise ValueError("ALLOWED_ORIGINS must be restricted in production!")


class TestingConfig(BaseConfig):
    ENVIRONMENT: Environment = Environment.TESTING
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
    ALLOWED_ORIGINS: List[str] = ["*"]
    GUNICORN_WORKERS: int = 1


def get_config() -> BaseConfig:
    env = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value).lower()
    config_map = {
        Environment.DEVELOPMENT.value: DevelopmentConfig,
        Environment.STAGING.value: StagingConfig,
        Environment.PRODUCTION.value: ProductionConfig,
        Environment.TESTING.value: TestingConfig,
    }
    return config_map.get(env, DevelopmentConfig)()


settings = get_config()
