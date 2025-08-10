from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

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
