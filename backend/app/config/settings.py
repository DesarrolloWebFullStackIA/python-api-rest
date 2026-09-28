from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or defaults.
    """
    APP_NAME: str = "Video Games API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "A professional REST API for managing Video Games and Categories "
        "with Steam integration using FastAPI and SQLite."
    )
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./app.db"

    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = "*"

    # External APIs Configuration
    STEAM_API_TIMEOUT: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """
        Parse CORS origins into a list of allowed origin strings.
        """
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS


settings = Settings()
