import logging
from importlib.metadata import version
from typing import Annotated, Any, Final, Literal

from arq.connections import RedisSettings
from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

logging.basicConfig(level=logging.INFO)

_LOG = logging.getLogger(__name__)

AppEnv = Literal["dev_container", "prod_render", "test_unit"]


class _AppEnvSettings(BaseSettings):
    APP_ENV: AppEnv


_APP_ENV: Final[AppEnv] = _AppEnvSettings().APP_ENV  # pyright: ignore[reportCallIssue]
_LOG.info("Environment: %s", _APP_ENV)

logging.config.fileConfig(  # pyright: ignore[reportAttributeAccessIssue]
    f"config/{_APP_ENV}/logging.conf",
    disable_existing_loggers=False,
)

_APP_VERSION: Final[str] = version(__package__ or __name__)
_LOG.info("App Version: %s", _APP_VERSION)


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"config/{_APP_ENV}/app.env")

    API_WEB_ALLOW_ORIGINS: Annotated[list[str], NoDecode]

    REDIS_CONNECTION_STRING: str | None = None
    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_DB: str | int | None = None

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
    APP_VERSION = _APP_VERSION
    app = _AppSettings()  # pyright: ignore[reportCallIssue]
    secret = _AppSecretSettings()  # pyright: ignore[reportCallIssue]

    def arq_redis_settings(self) -> RedisSettings:
        if self.app.REDIS_CONNECTION_STRING:
            return RedisSettings.from_dsn(self.app.REDIS_CONNECTION_STRING)
        if self.app.REDIS_HOST and self.app.REDIS_PORT:
            return RedisSettings(
                host=self.app.REDIS_HOST,
                port=self.app.REDIS_PORT,
                database=int(self.app.REDIS_DB) if self.app.REDIS_DB else 0,
            )
        msg = "Redis connection details misconfigured"
        raise RuntimeError(msg)


settings: Final = _Settings()
