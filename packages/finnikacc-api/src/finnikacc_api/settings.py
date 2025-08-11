import logging
from typing import Annotated, Any, Final, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

LOG = logging.getLogger(__name__)

AppEnv = Literal["dev_container", "prod_render", "test_unit"]


class _AppEnvSettings(BaseSettings):
    APP_ENV: AppEnv


_APP_ENV = _AppEnvSettings().APP_ENV  # pyright: ignore[reportCallIssue]

LOG.info("Environment: %s", _APP_ENV)


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"config/{_APP_ENV}/app.env")

    API_WEB_ALLOW_ORIGINS: Annotated[list[str], NoDecode]

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: str | int

    OEX_RATES_BASE_URL: str
    OEX_CACHE_DB_NAME: str
    OEX_CACHE_EXPIRE_AFTER_SEC: int

    @field_validator("API_WEB_ALLOW_ORIGINS", mode="before")
    @classmethod
    def split_urls(cls, v: Any) -> Any:  # noqa: ANN401
        if isinstance(v, str):
            return [u.strip() for u in v.split(",") if u.strip()]
        return v


class _AppSecretSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"config/{_APP_ENV}/app.secret.env")

    OEX_RATES_APP_ID: str


class _Settings:
    APP_ENV = _APP_ENV
    app = _AppSettings()  # pyright: ignore[reportCallIssue]
    secret = _AppSecretSettings() # pyright: ignore[reportCallIssue]


settings: Final = _Settings()
