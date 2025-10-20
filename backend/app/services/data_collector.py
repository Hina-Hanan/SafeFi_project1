from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session

from app.database.models import Protocol, ProtocolMetric
from app.services.rate_limiter import get_coingecko_rate_limiter, get_defillama_rate_limiter


logger = logging.getLogger("app.services.data_collector")


class _RetryingClient:
    def __init__(self, *, timeout: float = 20.0, max_retries: int = 3, backoff_base: float = 0.5, default_headers: dict[str, str] | None = None) -> None:
        self._client = httpx.AsyncClient(timeout=timeout, headers=default_headers)
        self._max_retries = max_retries
        self._backoff_base = backoff_base

    async def get_json(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        last_exc: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                resp = await self._client.get(url, params=params, headers=headers)
                if resp.status_code == 429:
                    # Rate limited; respect Retry-After when present
                    retry_after = float(resp.headers.get("Retry-After", "0")) or self._backoff_base * (2 ** attempt)
                    await asyncio.sleep(min(retry_after, 10))
                    continue
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_exc = exc
                await asyncio.sleep(self._backoff_base * (2 ** attempt))
        if last_exc:
            raise last_exc

    async def aclose(self) -> None:
        await self._client.aclose()


class CoinGeckoClient:
    BASE = "https://api.coingecko.com/api/v3"

    def __init__(self, http: _RetryingClient) -> None:
        self._http = http
        self._id_cache: dict[str, str] = {}
        self._rate_limiter = get_coingecko_rate_limiter()
        self._platform_map: dict[str, str] = {
            "ethereum": "ethereum",
            "eth": "ethereum",
            "arbitrum": "arbitrum-one",
            "arbitrum-one": "arbitrum-one",
            "optimism": "optimistic-ethereum",
            "polygon": "polygon-pos",
            "polygon-pos": "polygon-pos",
            "bsc": "binance-smart-chain",
            "binance-smart-chain": "binance-smart-chain",
            "avalanche": "avalanche",
        }

    async def resolve_asset_id_from_contract(self, chain: str, address: str) -> Optional[str]:
        platform = self._platform_map.get(chain.lower())
        if not platform or not address:
            return None
        try:
            await self._rate_limiter.acquire()  # Rate limit before API call
            data = await self._http.get_json(f"{self.BASE}/coins/{platform}/contract/{address}")
            coin_id = data.get("id")
            return coin_id
        except Exception:
            return None

    async def resolve_asset_id(self, name: str, symbol: Optional[str]) -> Optional[str]:
        cache_key = f"{name.lower()}:{(symbol or '').lower()}"
        if cache_key in self._id_cache:
            return self._id_cache[cache_key]
        await self._rate_limiter.acquire()  # Rate limit before API call
        data = await self._http.get_json(f"{self.BASE}/search", params={"query": symbol or name})
        for c in data.get("coins", []):
            if symbol and c.get("symbol", "").lower() == symbol.lower():
                self._id_cache[cache_key] = c.get("id")
                return self._id_cache[cache_key]
            if c.get("name", "").lower() == name.lower():
                self._id_cache[cache_key] = c.get("id")
                return self._id_cache[cache_key]
        return None

    async def fetch_market_snapshot(self, asset_id: str) -> dict[str, Any] | None:
        # Use markets for concise current snapshot
        await self._rate_limiter.acquire()  # Rate limit before API call
        data = await self._http.get_json(
            f"{self.BASE}/coins/markets",
            params={"vs_currency": "usd", "ids": asset_id, "price_change_percentage": "24h"},
        )
        if not data:
            return None
        row = data[0]
        return {
            "price": row.get("current_price"),
            "market_cap": row.get("market_cap"),
            "price_change_24h": row.get("price_change_percentage_24h_in_currency"),
        }


class DeFiLlamaClient:
    BASE = "https://api.llama.fi"

    def __init__(self, http: _RetryingClient) -> None:
        self._http = http
        self._slug_cache: dict[str, str] = {}
        self._rate_limiter = get_defillama_rate_limiter()

    async def resolve_protocol_slug(self, name: str) -> Optional[str]:
        key = name.lower()
        if key in self._slug_cache:
            return self._slug_cache[key]
        await self._rate_limiter.acquire()  # Rate limit before API call
        all_protocols = await self._http.get_json(f"{self.BASE}/protocols")
        # simple exact or case-insensitive match
        for p in all_protocols:
            if p.get("name", "").lower() == key:
                self._slug_cache[key] = p.get("slug") or p.get("name")
                return self._slug_cache[key]
        # fallback: first protocol whose name contains our key
        for p in all_protocols:
            if key in p.get("name", "").lower():
                self._slug_cache[key] = p.get("slug") or p.get("name")
                return self._slug_cache[key]
        return None

    async def fetch_tvl_snapshot(self, slug: str) -> dict[str, Any] | None:
        await self._rate_limiter.acquire()  # Rate limit before API call
        data = await self._http.get_json(f"{self.BASE}/protocol/{slug}")
        if not data:
            return None
        tvl = data.get("tvl")
        current_tvl = None
        if isinstance(tvl, list) and tvl:
            # Last entry is the latest
            current_tvl = tvl[-1].get("totalLiquidityUSD") or tvl[-1].get("totalLiquidityUsd") or tvl[-1].get("tvl")
        return {"tvl": current_tvl}


class DataCollectorService:
    """Service for collecting protocol data from external sources with real integrations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def collect(self, source: str, protocol_ids: list[str] | None) -> int:
        src = source.lower().strip()
        if src not in {"coingecko", "defillama"}:
            raise ValueError("source must be 'coingecko' or 'defillama'")

        protocols: list[Protocol]
        if protocol_ids:
            protocols = (
                self.db.query(Protocol)  # type: ignore[attr-defined]
                .filter(Protocol.id.in_(protocol_ids))
                .all()
            )
        else:
            protocols = self.db.query(Protocol).filter_by(is_active=True).all()  # type: ignore[attr-defined]

        if not protocols:
            return 0

        # Attach CoinGecko API key if present (required by CoinGecko now)
        default_headers: dict[str, str] | None = None
        cg_key = os.getenv("COINGECKO_API_KEY") or os.getenv("COINGECKO_PRO_API_KEY")
        if cg_key:
            default_headers = {"x-cg-pro-api-key": cg_key}

        http = _RetryingClient(timeout=25.0, max_retries=4, backoff_base=0.5, default_headers=default_headers)
        try:
            if src == "coingecko":
                cg = CoinGeckoClient(http)
                tasks = [self._collect_from_cg(cg, p) for p in protocols]
            else:
                ll = DeFiLlamaClient(http)
                tasks = [self._collect_from_llama(ll, p) for p in protocols]

            results = await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            await http.aclose()

        processed = 0
        for r in results:
            if isinstance(r, Exception):
                logger.warning("Collection task failed: %s", r)
            else:
                processed += int(bool(r))
        return processed

    async def _collect_from_cg(self, cg: CoinGeckoClient, protocol: Protocol) -> bool:
        try:
            asset_id: Optional[str] = None
            # Prefer contract-based resolution when available
            if protocol.contract_address:
                asset_id = await cg.resolve_asset_id_from_contract(protocol.chain or "ethereum", protocol.contract_address)
            if not asset_id:
                asset_id = await cg.resolve_asset_id(protocol.name, protocol.symbol)
            if not asset_id:
                logger.info("CoinGecko id not found for protocol=%s (symbol=%s)", protocol.name, protocol.symbol)
                return False
            snap = await cg.fetch_market_snapshot(asset_id)
            if not snap:
                return False
            now = _utcnow()
            metric = ProtocolMetric(
                protocol_id=protocol.id,
                tvl=None,
                volume_24h=None,
                price=_to_float(snap.get("price")),
                market_cap=_to_float(snap.get("market_cap")),
                price_change_24h=_to_float(snap.get("price_change_24h")),
                timestamp=now,
            )
            self.db.add(metric)
            return True
        except Exception as exc:  # pragma: no cover
            logger.exception("CoinGecko collection failed for %s: %s", protocol.name, exc)
            return False

    async def _collect_from_llama(self, ll: DeFiLlamaClient, protocol: Protocol) -> bool:
        try:
            slug = await ll.resolve_protocol_slug(protocol.name)
            if not slug:
                logger.info("DeFiLlama slug not found for protocol=%s", protocol.name)
                return False
            snap = await ll.fetch_tvl_snapshot(slug)
            if not snap:
                return False
            now = _utcnow()
            metric = ProtocolMetric(
                protocol_id=protocol.id,
                tvl=_to_float(snap.get("tvl")),
                volume_24h=None,
                price=None,
                market_cap=None,
                price_change_24h=None,
                timestamp=now,
            )
            self.db.add(metric)
            return True
        except Exception as exc:  # pragma: no cover
            logger.exception("DeFiLlama collection failed for %s: %s", protocol.name, exc)
            return False


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _utcnow():
    import datetime as _dt

    return _dt.datetime.utcnow().replace(tzinfo=_dt.timezone.utc)


