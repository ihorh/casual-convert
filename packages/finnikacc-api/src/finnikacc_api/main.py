import logging

from fastapi import FastAPI

from finnikacc_api import settings
from finnikacc_api.app_webapi.main import app_webapi

logging.config.fileConfig(f"config/{settings.APP_ENV}/logging.conf", disable_existing_loggers=False)  # pyright: ignore[reportAttributeAccessIssue]
app = FastAPI()


@app.get("/status")
async def get_status() -> dict[str, str]:
    return {"status": "Happy Finnika! :-)"}

app_api = FastAPI()

app.mount("/api-web-app", app_webapi)
app.mount("/api", app_api)
