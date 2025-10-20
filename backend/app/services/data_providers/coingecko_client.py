import os
import os
import time
import asyncio
import httpx


_RATE_LIMIT_LOCK = asyncio.Lock()
_LAST_CALL_TS: float = 0.0
_MIN_INTERVAL_SEC: float = float(os.getenv("COINGECKO_MIN_INTERVAL_SEC", "0.35"))  # ~3 req/sec


async def _rate_limit() -> None:
    global _LAST_CALL_TS
    async with _RATE_LIMIT_LOCK:
        now = time.monotonic()
        wait = _MIN_INTERVAL_SEC - (now - _LAST_CALL_TS)
        if wait > 0:
            await asyncio.sleep(wait)
        _LAST_CALL_TS = time.monotonic()


class CoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    async def fetch_simple_price(self, ids: str, vs_currencies: str = "usd") -> dict:
        url = f"{self.BASE_URL}/simple/price"
        params = {"ids": ids, "vs_currencies": vs_currencies}
        headers: dict[str, str] = {}
        api_key = os.getenv("COINGECKO_API_KEY") or os.getenv("COINGECKO_PRO_API_KEY")
        if api_key:
            headers["x-cg-pro-api-key"] = api_key
        await _rate_limit()
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()



