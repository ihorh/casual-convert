from typing import Any, Literal, TypedDict

CurrencyRateCacheType = Literal["latest", "lastseen"]

class RequestLastModETagCacheValue(TypedDict):
    etag: str
    rq_date: str # * timestamp seconds
    rq_date_rfc_7231: str

class RequestLastModETagCacheValueTyped(TypedDict):
    etag: str
    rq_date: int # * timestamp seconds
    rq_date_rfc_7231: str

class CurrencyRateCacheValue(TypedDict):
    currency: str
    rate: str
    request_at: str # * timestamp seconds
    last_modified: str # * timestamp seconds


class CurrencyRateCacheValueTyped(TypedDict):
    currency: str
    rate: float
    request_at: int  # * timestamp seconds
    last_modified: int  # * timestamp seconds

def _convert_to_untyped_cr(mapping: CurrencyRateCacheValueTyped) -> CurrencyRateCacheValue:
    return {
        "currency": mapping["currency"],
        "rate": f"{mapping['rate']}",
        "request_at": f"{mapping['request_at']}",
        "last_modified": f"{mapping['last_modified']}",
    }


def _convert_to_typed_cr(mapping: CurrencyRateCacheValue) -> CurrencyRateCacheValueTyped:
    return {
        "currency": _convert_bytes_to_str(mapping["currency"]),
        "rate": float(mapping["rate"]),
        "request_at": int(mapping["request_at"]),
        "last_modified": int(mapping["last_modified"]),
    }

def _convert_to_untyped_etag(mapping: RequestLastModETagCacheValueTyped) -> RequestLastModETagCacheValue:
    return {
        "etag": mapping["etag"],
        "rq_date": f"{mapping['rq_date']}",
        "rq_date_rfc_7231": mapping["rq_date_rfc_7231"],
    }

def _convert_to_typed_etag(mapping: RequestLastModETagCacheValue) -> RequestLastModETagCacheValueTyped:
    return {
        "etag": mapping["etag"],
        "rq_date": int(mapping["rq_date"]),
        "rq_date_rfc_7231": mapping["rq_date_rfc_7231"],
    }

def _convert_dict_bytes_to_str(mapping: dict[Any, Any]) -> dict[str, str]:
    return {
        _convert_bytes_to_str(k): _convert_bytes_to_str(v)
        for k, v in mapping.items()
    }

def _convert_bytes_to_str(inp: str | bytes) -> str:
    if isinstance(inp, str):
        return inp
    if isinstance(inp, bytes):
        return inp.decode()
    raise ValueError

