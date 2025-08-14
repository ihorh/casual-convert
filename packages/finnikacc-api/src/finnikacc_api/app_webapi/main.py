import logging
from typing import Annotated

from fastapi import FastAPI, Query

from finnikacc_api import settings
from finnikacc_api.app_webapi._data_placeholder import _CURRENCIES, _DATA, _DEFAULT_MAIN_BASE_CURRENCY
from finnikacc_api.app_webapi.middleware import apply_middleware
from finnikacc_api.app_webapi.model import CurrencyConvertRateModel

LOG = logging.getLogger(__name__)


app_webapi = FastAPI()
apply_middleware(app_webapi)


@app_webapi.get("/status")
async def get_status() -> dict[str, str]:
    return {"status": "OK", "version": settings.APP_VERSION}


@app_webapi.get("/convert-rates", response_model_by_alias=True)
async def get_convert_rates(
    base_currency: str = "USD",
    quote_currencies: Annotated[list[str] | None, Query()] = None,
) -> list[CurrencyConvertRateModel]:
    if base_currency != _DEFAULT_MAIN_BASE_CURRENCY:
        raise ValueError
    return _DATA


@app_webapi.get("/quote_currencies")
async def get_quote_currencies(base_currency: str) -> list[str]:
    if base_currency != _DEFAULT_MAIN_BASE_CURRENCY:
        raise ValueError
    return [_DEFAULT_MAIN_BASE_CURRENCY, *_CURRENCIES]
