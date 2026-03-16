from __future__ import annotations

from functools import lru_cache
from threading import Lock
from time import monotonic, sleep

import httpx

from src.config import GEOCODING_PROVIDER, GEOCODING_USER_AGENT


class GeocodingError(RuntimeError):
    """Raised when geocoding fails."""


_RATE_LIMIT_SECONDS = 1.05
_last_request_at = 0.0
_rate_limit_lock = Lock()


def get_geocoding_provider() -> str:
    return GEOCODING_PROVIDER


def _respect_nominatim_rate_limit() -> None:
    global _last_request_at
    with _rate_limit_lock:
        elapsed = monotonic() - _last_request_at
        if elapsed < _RATE_LIMIT_SECONDS:
            sleep(_RATE_LIMIT_SECONDS - elapsed)
        _last_request_at = monotonic()


def geocode_address(query: str) -> dict[str, float | str]:
    provider = get_geocoding_provider()
    if provider == "local":
        raise GeocodingError("目前使用 local provider，僅支援本地地址/地標映射，未啟用真實 geocoding API。")
    if provider == "nominatim":
        return geocode_with_nominatim(query)
    raise GeocodingError(f"不支援的 geocoding provider: {provider}")


@lru_cache(maxsize=256)
def geocode_with_nominatim(query: str) -> dict[str, float | str]:
    _respect_nominatim_rate_limit()
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "jsonv2", "limit": 1}
    headers = {"User-Agent": GEOCODING_USER_AGENT}
    with httpx.Client(timeout=15.0) as client:
        response = client.get(url, params=params, headers=headers)
        response.raise_for_status()
        payload = response.json()

    if not payload:
        raise GeocodingError("查無 geocoding 結果。")

    top = payload[0]
    return {
        "query": query,
        "latitude": float(top["lat"]),
        "longitude": float(top["lon"]),
        "display_name": top.get("display_name", query),
    }
