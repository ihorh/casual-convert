from typing import Annotated, Any, Final, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

AppEnv = Literal["dev_container", "prod_render"]


class _AppEnvSettings(BaseSettings):
    APP_ENV: str


_APP_ENV = _AppEnvSettings().APP_ENV  # pyright: ignore[reportCallIssue]


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"config/{_APP_ENV}/app.env")

    API_WEB_ALLOW_ORIGINS: Annotated[list[str], NoDecode]

    @field_validator("API_WEB_ALLOW_ORIGINS", mode="before")
    @classmethod
    def split_urls(cls, v: Any) -> Any:  # noqa: ANN401
        if isinstance(v, str):
            return [u.strip() for u in v.split(",") if u.strip()]
        return v


class _AppSecretSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"config/{_APP_ENV}/app.secret.env")
    pass


class _Settings:
    APP_ENV = _APP_ENV
    app = _AppSettings() # pyright: ignore[reportCallIssue]
    secret = _AppSecretSettings()


settings: Final = _Settings()
