"""Application configuration.

Every setting comes from the environment (via a .env file in development).
Nothing secret is ever written into source code.
"""

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    PROJECT_NAME: str = "Student Clearance Management System"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ---- Database (stored as parts, never as a full URL) ----
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    # ---- Security ----
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- CORS ----
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    # ---- Uploads ----
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024

    @property
    def DATABASE_URL(self) -> str:
        """Build the SQLAlchemy URL, escaping the credentials.

        This is why the password is stored as its own variable rather than
        inside a ready-made URL: a password such as "Kirenga@123" contains an
        "@", which is the character that separates credentials from the host.
        Pasted into a URL raw, it would be parsed as the host and the
        connection would fail with a confusing error. quote_plus turns it into
        "Kirenga%40123" so any password works without manual escaping.
        """
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+psycopg2://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins(self) -> list[str]:
        """Parse the comma-separated origin list into exact origins."""
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached so the .env file is read once per process."""
    return Settings()


settings = get_settings()
