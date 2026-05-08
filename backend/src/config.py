from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./tonhao.db"
    cors_origins: str = "http://localhost:5173"
    upload_dir: str = "uploads"
    max_upload_bytes: int = 10 * 1024 * 1024  # 10 MB

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
