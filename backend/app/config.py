from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pydantic import SecretStr


class Settings(BaseSettings):
    database_url: str = "sqlite:///./patchguard.db"
    cors_origins: str = "http://localhost:5173"
    seed_demo_data: bool = True
    auth_required: bool = False
    auth_admin_password: SecretStr = SecretStr("")
    auth_session_secret: SecretStr = SecretStr("")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


settings = Settings()
