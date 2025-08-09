import os

os.environ["APP_ENV"] = "dev_local"

import uvicorn


def main() -> None:
    os.chdir("./packages/finnikacc-api")
    uvicorn.run(
        "finnikacc_api.main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        log_level="info",
        reload=True,
    )
