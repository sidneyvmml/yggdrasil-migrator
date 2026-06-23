from pathlib import Path
from typing import Optional
from urllib.parse import ParseResult, urlparse, urlunparse

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    redis_user: Optional[str] = Field(None, env="REDIS_USER")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_pass: Optional[str] = Field(None, env="REDIS_PASS")
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")

    sqlite_path: str = Field(
        str(Path(__file__).resolve().parent.parent.parent / "yggdrasil.db"),
        env="SQLITE_PATH",
    )
    mongodb_connect_timeout_ms: int = Field(5000, env="MONGODB_CONNECT_TIMEOUT_MS")

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def computed_redis_url(self) -> str:
        if self.redis_url:
            parsed = urlparse(self.redis_url)
            if parsed.username or parsed.password:
                return self.redis_url

            auth_password = self.redis_password or self.redis_pass
            if auth_password:
                username = parsed.username or (self.redis_user or "")
                host = parsed.hostname or self.redis_host
                port = parsed.port or self.redis_port
                path = parsed.path or f'/{self.redis_db}'
                netloc = f'{username}:{auth_password}@{host}:{port}' if username else f':{auth_password}@{host}:{port}'
                return urlunparse(ParseResult(parsed.scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))

            return self.redis_url

        auth_password = self.redis_password or self.redis_pass
        username = self.redis_user or ""
        if auth_password and username:
            password_segment = f"{username}:{auth_password}@"
        elif auth_password:
            password_segment = f":{auth_password}@"
        else:
            password_segment = ""
        return f"redis://{password_segment}{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
