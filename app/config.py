from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    LOG_LEVEL: str = "INFO"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000",
    ]

    DATABASE_URL: str = "sqlite:///./counterexample_debugger.db"

    # Execution limits
    DEFAULT_EXECUTION_TIMEOUT: float = 2.0  # seconds
    MAX_OUTPUT_BYTES: int = 65536  # 64 KB
    MAX_MEMORY_MB: int = 128  # MB limit for sandboxed process/container
    MAX_CPU_COUNT: float = 1.0

    # Sandbox mode: 'local' (restricted subprocess), 'docker' (Docker container execution)
    SANDBOX_MODE: Literal["local", "docker"] = "local"
    DOCKER_IMAGE: str = "python:3.12-slim"
    ENABLE_DOCKER_FALLBACK: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
