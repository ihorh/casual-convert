import uvicorn


def main() -> None:
    uvicorn.run(
        "finnikacc_api.main:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        log_level="info",
        reload=True,
        reload_dirs=[
            "packages/finnikacc-api",
        ],
    )
