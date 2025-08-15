import logging
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from http import HTTPStatus
from typing import Any

from aiohttp import hdrs
from multidict import CIMultiDictProxy, istr

from finnikacc_api.lifecycle.dependencies import get_ext_deps_from_dict, get_int_deps_from_dict
from finnikacc_api.redis.model import CurrencyRateCacheValueTyped, RequestLastModETagCacheValue
from finnikacc_api.redis.redis_cache import CurrencyRateRedisCache, LastRequestETagRedisCache

LOG = logging.getLogger(__name__)

_ALLOWED_CURRENCIES = ["USD", "EUR", "PLN", "UAH", "GBP", "CHF", "SEK", "NOK"]


async def fetch_conv_rates_oex(ctx: dict) -> None:
    edeps = get_ext_deps_from_dict(ctx)
    ideps = get_int_deps_from_dict(ctx)
    rates_cache = ideps.currency_rate_cache
    etag_cache = ideps.last_request_etag_cache
    endpoint = "latest.json"

    prev_respons_meta = await etag_cache.hget_raw(endpoint)

    async with edeps.oex_client.get(endpoint, headers=_date_etag_to_cc_headers(prev_respons_meta)) as response:
        _log_http_status_and_headers(HTTPStatus(response.status), response.headers, endpoint, "OEX")

        if response.status != HTTPStatus.OK:
            return

        data = await response.json()

        if (base_curr := data["base"]) != "USD":
            LOG.warning("Unexpected base currency '%s'. Skipping.", base_curr)
            return

        await _store_response_etag(etag_cache, endpoint, response.headers)
        await _store_curr_rates(rates_cache, data, response.headers)


def _clean_etag(etag: str) -> str:
    m = re.match(r'(?:W/)?"(.+)"', etag)
    return m.group(1) if m else etag


async def _store_response_etag(
    etag_cache: LastRequestETagRedisCache,
    endpoint: str,
    headers: CIMultiDictProxy[str],
) -> None:
    if (etag := headers.get(hdrs.ETAG)) and (date_rfc_7231 := headers.get(hdrs.DATE)):
        await etag_cache.hset_conv(
            {
                "etag": etag,
                "rq_date": int(parsedate_to_datetime(date_rfc_7231).timestamp()),
                "rq_date_rfc_7231": date_rfc_7231,
            },
            endpoint=endpoint,
        )


async def _store_curr_rates(
    rates_cache: CurrencyRateRedisCache,
    data: Any,  # noqa: ANN401
    headers: CIMultiDictProxy,
) -> None:
    timestamp_fl = data.get("timestamp") or int(datetime.now(UTC).timestamp())
    last_mod_rfc_7231 = headers.get(hdrs.LAST_MODIFIED)
    last_mod_dt = (
        parsedate_to_datetime(last_mod_rfc_7231) if last_mod_rfc_7231 else datetime.fromtimestamp(timestamp_fl, UTC)
    )

    rates_transformed = {
        k: CurrencyRateCacheValueTyped(
            currency=k,
            rate=v,
            request_at=timestamp_fl,
            last_modified=int(last_mod_dt.timestamp()),
        )
        for k, v in data["rates"].items()
        if k in _ALLOWED_CURRENCIES
    }

    await rates_cache.hset_m_conv(rates_transformed, base_currency="USD")


def _date_etag_to_cc_headers(prev_meta: RequestLastModETagCacheValue | None) -> dict[istr, str] | None:
    if prev_meta and (date_rfc_7231 := prev_meta.get("rq_date_rfc_7231")) and (etag := prev_meta.get("etag")):
        h = {hdrs.IF_NONE_MATCH: etag, hdrs.IF_MODIFIED_SINCE: date_rfc_7231}
        LOG.info("passing cache control headers: %s", h)
        return h
    return None


def _log_http_status_and_headers(status: HTTPStatus, headers: CIMultiDictProxy, endpoint: str, provider: str) -> None:
    log_msg = f"HTTP Status: {status.value} {status.phrase}. Endpoint: '{endpoint}' @ {provider}"
    if status in (HTTPStatus.OK, HTTPStatus.NOT_MODIFIED):
        LOG.info(log_msg)
    else:
        LOG.warning(log_msg)

    for k, v in headers.items():
        LOG.debug("header - %s: %s", k, v)
