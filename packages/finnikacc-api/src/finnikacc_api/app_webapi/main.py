import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field

from finnikacc_api.app_webapi.middleware import apply_middleware

LOG = logging.getLogger(__name__)

app_webapi = FastAPI()
apply_middleware(app_webapi)

CurrencyConvertRateType = Literal["recent", "average"]
CurrencyConvertRateAge = Literal["1h", "1d", "2d", "outdated"]


class BaseConvertModel(BaseModel):
    pass


class CurrencyConvertRateModel(BaseConvertModel):
    model_config = ConfigDict(validate_by_name=True)

    base_currency: Annotated[str, Field(alias="baseCurrency")]
    quote_currency: Annotated[str, Field(alias="quoteCurrency")]
    convert_rate: Annotated[Decimal, Field(alias="convertRate")]
    rate_type: Annotated[CurrencyConvertRateType, Field(alias="rateType")]
    rate_age: Annotated[CurrencyConvertRateAge, Field(alias="rateAge")]
    rate_at: Annotated[datetime, Field(alias="rateAt")]


_COMMON_ARGS = {
    "base_currency": "USD",
    "rate_type": "recent",
    "rate_age": "outdated",
    "rate_at": datetime.now(UTC) - timedelta(weeks=10),
}

_DEFAULT_MAIN_BASE_CURRENCY = "USD"
_CURRENCIES = ["EUR", "GBP", "PLN", "UAH"]
_DATA = [
    CurrencyConvertRateModel(**_COMMON_ARGS, quote_currency="USD", convert_rate=Decimal("1.0")),
    CurrencyConvertRateModel(**_COMMON_ARGS, quote_currency="EUR", convert_rate=Decimal("0.86")),
    CurrencyConvertRateModel(**_COMMON_ARGS, quote_currency="GBP", convert_rate=Decimal("0.75")),
    CurrencyConvertRateModel(**_COMMON_ARGS, quote_currency="PLN", convert_rate=Decimal("3.7")),
    CurrencyConvertRateModel(**_COMMON_ARGS, quote_currency="UAH", convert_rate=Decimal("41.71")),
]


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
