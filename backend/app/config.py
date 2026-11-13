from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration managed through environment variables
    with sensible defaults.
    """
    APP_NAME: str = "GitSummarizer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # External APIs
    GITHUB_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Database
    DATABASE_URL: str = "sqlite:///./git_summarizer.db"

    # Security & CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    
    # Request & LLM Limits
    REQUEST_TIMEOUT_SECONDS: float = 15.0
    MAX_README_CHARS: int = 15000
    MAX_DIFF_CHARS: int = 12000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

