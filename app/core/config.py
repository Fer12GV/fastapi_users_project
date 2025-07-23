from pydantic_settings import BaseSettings
from typing import Optional, List
from dotenv import load_dotenv
import os
from enum import Enum

load_dotenv()

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class BaseConfig(BaseSettings):
    """Base configuration class with common settings"""
    
    # App
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI Users API")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DESCRIPTION: str = os.getenv("DESCRIPTION", "API de gestión de usuarios con autenticación JWT")
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Web Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    WEB_PORT: int = int(os.getenv("WEB_PORT", "8000"))
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "*").split(",")
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/fastapi_users_db")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "fastapi_users_db")
    DB_USER: str = os.getenv("DB_USER", "fastapi_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "fastapi_users")
    
    # Application database user (created by init script)
    DB_APP_USER: str = os.getenv("DB_APP_USER", "fastapi_app_user")
    DB_APP_PASSWORD: str = os.getenv("DB_APP_PASSWORD", "app_password")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Gunicorn Configuration (Production Server)
    GUNICORN_WORKERS: int = int(os.getenv("GUNICORN_WORKERS", "4"))
    WORKER_CONNECTIONS: int = int(os.getenv("WORKER_CONNECTIONS", "1000"))
    WORKER_TIMEOUT: int = int(os.getenv("WORKER_TIMEOUT", "30"))
    KEEPALIVE: int = int(os.getenv("KEEPALIVE", "2"))
    MAX_REQUESTS: int = int(os.getenv("MAX_REQUESTS", "1000"))
    MAX_REQUESTS_JITTER: int = int(os.getenv("MAX_REQUESTS_JITTER", "100"))
    GRACEFUL_TIMEOUT: int = int(os.getenv("GRACEFUL_TIMEOUT", "30"))
    
    # Redis Configuration (Optional)
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # SSL Configuration (HTTPS)
    SSL_KEYFILE: Optional[str] = os.getenv("SSL_KEYFILE")
    SSL_CERTFILE: Optional[str] = os.getenv("SSL_CERTFILE")
    SSL_CA_CERTS: Optional[str] = os.getenv("SSL_CA_CERTS")
    SSL_CERT_REQS: int = int(os.getenv("SSL_CERT_REQS", "0"))
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_HEALTH_CHECKS: bool = os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true"
    ENABLE_SECURITY_HEADERS: bool = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Override with environment variables if provided
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
        # Single worker for development
        self.GUNICORN_WORKERS = 1

class StagingConfig(BaseConfig):
    """Staging environment configuration"""
    
    ENVIRONMENT: Environment = Environment.STAGING
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    ENVIRONMENT: Environment = Environment.PRODUCTION
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
        
        # Ensure critical production settings
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-here-change-in-production":
            raise ValueError("SECRET_KEY must be set in production!")
        
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in production!")
        
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long in production!")
        
        # Ensure production-specific configurations
        if self.DEBUG:
            raise ValueError("DEBUG must be False in production!")
        
        if "*" in self.ALLOWED_ORIGINS:
            raise ValueError("ALLOWED_ORIGINS must be restricted in production!")

class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    
    ENVIRONMENT: Environment = Environment.TESTING
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Test database (in-memory SQLite)
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    
    # Fast token expiration for testing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
    
    # Disable external dependencies in tests
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Single worker for testing
    GUNICORN_WORKERS: int = 1

def get_config() -> BaseConfig:
    """Factory function to get configuration based on environment"""
    
    env = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value).lower()
    
    config_mapping = {
        Environment.DEVELOPMENT.value: DevelopmentConfig,
        Environment.STAGING.value: StagingConfig,
        Environment.PRODUCTION.value: ProductionConfig,
        Environment.TESTING.value: TestingConfig,
    }
    
    config_class = config_mapping.get(env, DevelopmentConfig)
    return config_class()

# Global settings instance
settings = get_config()
