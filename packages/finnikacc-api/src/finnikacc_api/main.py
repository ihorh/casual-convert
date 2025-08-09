from fastapi import FastAPI

from finnikacc_api.app_webapi.main import app_webapi

app = FastAPI()


@app.get("/status")
async def get_status() -> dict[str, str]:
    return {"status": "Happy Finnika! :-)"}


app_api = FastAPI()

app.mount("/api-web-app", app_webapi)
app.mount("/api", app_api)
