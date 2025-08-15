import logging
from datetime import UTC, datetime
from decimal import Decimal
from sys import exc_info
from typing import TYPE_CHECKING, Annotated, Any, Literal

from fastapi import FastAPI, Query

from finnikacc_api import settings
from finnikacc_api.app_webapi._data_placeholder import _CURRENCIES, _DATA, _DEFAULT_MAIN_BASE_CURRENCY
from finnikacc_api.app_webapi.middleware import apply_middleware
from finnikacc_api.app_webapi.model import CurrencyConvertRateModel
from finnikacc_api.lifecycle.dependencies import CurrRateCacheDep

if TYPE_CHECKING:
    from finnikacc_api.redis.model import CurrencyRateCacheValueTyped

LOG = logging.getLogger(__name__)


app_webapi = FastAPI()
apply_middleware(app_webapi)


@app_webapi.get("/status")
async def get_status() -> dict[str, str]:
    return {"status": "OK", "version": settings.APP_VERSION}


@app_webapi.get("/convert-rates", response_model_by_alias=True)
async def get_convert_rates(
    curr_cache: CurrRateCacheDep,
    base_currency: Literal["USD"] = _DEFAULT_MAIN_BASE_CURRENCY,
    quote_currencies: Annotated[list[str] | None, Query()] = None,
) -> list[CurrencyConvertRateModel]:
    try:
        result: list[CurrencyRateCacheValueTyped]
        if quote_currencies:
            result = await curr_cache.hgetall_currencies(base_currency, quote_currencies)
        else:
            result = await curr_cache.scan_hgetall_currencies_all(base_currency)

        return [
            CurrencyConvertRateModel(
                base_currency=base_currency,
                quote_currency=r["currency"],
                convert_rate=round(Decimal(f"{r["rate"]}"), 3), # TODO (ihorh): meh
                rate_type="recent",
                rate_age="1h", # TODO (ihorh): of course it is not always correct
                rate_at=datetime.fromtimestamp(r["last_modified"], UTC),
            )
            for r in result
        ]
    except:  # noqa: E722 # TODO (ihorh): of course this is temporary until all edgecases are handled
        LOG.warning("Error fetching or converting currency data. Returning default placeholder", exc_info=exc_info())
    return _DATA


@app_webapi.get("/quote-currencies")
async def get_quote_currencies(
    curr_cache: CurrRateCacheDep,
    base_currency: Literal["USD"] = _DEFAULT_MAIN_BASE_CURRENCY,
) -> list[Any]:
    result = [
        r["currency"]
        for r in await curr_cache.scan_hgetall_currencies_all(base_currency)
    ]
    return result or [base_currency, *_CURRENCIES]
