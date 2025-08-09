from datetime import UTC, datetime, timedelta
from decimal import Decimal

from finnikacc_api.app_webapi.model import CurrencyConvertRateModel

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
