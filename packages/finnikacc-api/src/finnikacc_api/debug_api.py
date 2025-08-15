import logging
import secrets
from io import StringIO

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import APIKeyHeader

from finnikacc_api.lifecycle.dependencies import CurrRateCacheDep

LOG = logging.getLogger(__name__)

DEBUG_API_TOKEN = secrets.token_urlsafe(32)
# TODO (ihorh): this is intentional to enable quick debug while in "alpha" mode. Risk is moderate but TB removed later.
LOG.info("🔑 Debug API token for this session: %s", DEBUG_API_TOKEN)

app_debug_api = FastAPI()

api_key_header = APIKeyHeader(name="X-Debug-Token", auto_error=False)


def verify_debug_token(token: str = Depends(api_key_header)) -> None:
    if token != DEBUG_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing debug token",
        )


@app_debug_api.get("/debug-info", dependencies=[Depends(verify_debug_token)])
async def get_debug_info(currencies_cache: CurrRateCacheDep) -> Response:
    result = await currencies_cache.scan_hgetall_currencies_all("USD")

    LOG.info("Currencies: %s", result)

    sio = StringIO()
    for r in result:
        print(r, file=sio)

    return Response(content=sio.getvalue(), media_type="text/plain")
