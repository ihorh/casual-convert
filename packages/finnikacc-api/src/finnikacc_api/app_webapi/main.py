from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

app_webapi = FastAPI()

app_webapi.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return _DATA


@app_webapi.get("/quote_currencies")
async def get_quote_currencies(base_currency: str) -> list[str]:
    return [r.quote_currency for r in _DATA]
