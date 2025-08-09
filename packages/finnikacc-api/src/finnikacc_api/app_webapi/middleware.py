import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from finnikacc_api import settings

LOG = logging.getLogger(__name__)

_ALLOWED_ORIGINS = settings.app.API_WEB_ALLOW_ORIGINS


def apply_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def _check_origin_referer(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        if origin and origin not in _ALLOWED_ORIGINS:
            LOG.debug("Invalid origin %s", origin)
            return Response(status_code=500)

        if referer and not any(referer.startswith(allowed) for allowed in _ALLOWED_ORIGINS):
            LOG.debug("Invalid refereer %s", referer)
            return Response(status_code=500)

        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
