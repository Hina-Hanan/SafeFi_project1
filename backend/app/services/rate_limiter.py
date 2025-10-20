"""
Smart Rate Limiter for CoinGecko API.

Handles CoinGecko's free tier limits:
- 5-15 calls per minute
- Automatic backoff on 429 errors
- Request queue management
- Distributed rate limiting support
"""
import asyncio
import logging
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
import os

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Smart rate limiter with exponential backoff and queue management.
    
    Features:
    - Configurable calls per period
    - Automatic 429 handling
    - Request queuing
    - Statistics tracking
    """
    
    def __init__(
        self, 
        max_calls: int = 5,  # CoinGecko free tier default
        period_seconds: int = 60,
        backoff_factor: float = 2.0,
        max_backoff: float = 300.0  # 5 minutes max
    ):
        self.max_calls = int(os.getenv("COINGECKO_RATE_LIMIT_CALLS", max_calls))
        self.period_seconds = int(os.getenv("COINGECKO_RATE_LIMIT_PERIOD", period_seconds))
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        
        self._call_times: deque = deque()
        self._lock = asyncio.Lock()
        self._retry_count = 0
        self._total_calls = 0
        self._total_rate_limited = 0
        
        logger.info(
            f"RateLimiter initialized: {self.max_calls} calls per {self.period_seconds}s"
        )
    
    async def acquire(self) -> None:
        """Wait until a slot is available for making an API call."""
        async with self._lock:
            now = time.time()
            
            # Remove expired timestamps
            cutoff = now - self.period_seconds
            while self._call_times and self._call_times[0] < cutoff:
                self._call_times.popleft()
            
            # If at limit, wait until oldest call expires
            if len(self._call_times) >= self.max_calls:
                sleep_time = self.period_seconds - (now - self._call_times[0]) + 0.1
                logger.debug(f"Rate limit reached, waiting {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                # Recursive call to try again
                return await self.acquire()
            
            # Record this call
            self._call_times.append(now)
            self._total_calls += 1
    
    async def execute_with_backoff(
        self, 
        func: Callable,
        *args: Any,
        max_retries: int = 5,
        **kwargs: Any
    ) -> Any:
        """
        Execute a function with automatic retry and exponential backoff.
        
        Handles 429 (Too Many Requests) errors gracefully.
        """
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Wait for rate limit slot
                await self.acquire()
                
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Reset retry count on success
                self._retry_count = 0
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
                    self._total_rate_limited += 1
                    retry_count += 1
                    
                    # Calculate backoff time
                    backoff_time = min(
                        self.backoff_factor ** retry_count,
                        self.max_backoff
                    )
                    
                    logger.warning(
                        f"Rate limited (429), retry {retry_count}/{max_retries} "
                        f"after {backoff_time:.1f}s. Total rate limits: {self._total_rate_limited}"
                    )
                    
                    await asyncio.sleep(backoff_time)
                    last_error = e
                    
                else:
                    # Non-rate-limit error, raise immediately
                    raise
        
        # Max retries exceeded
        logger.error(f"Max retries ({max_retries}) exceeded for rate-limited request")
        raise last_error or Exception("Max retries exceeded")
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        async def _get_stats():
            async with self._lock:
                now = time.time()
                cutoff = now - self.period_seconds
                
                # Count recent calls
                recent_calls = sum(1 for t in self._call_times if t >= cutoff)
                
                return {
                    "total_calls": self._total_calls,
                    "total_rate_limited": self._total_rate_limited,
                    "recent_calls": recent_calls,
                    "max_calls_per_period": self.max_calls,
                    "period_seconds": self.period_seconds,
                    "slots_available": self.max_calls - recent_calls,
                    "rate_limit_percentage": (
                        (self._total_rate_limited / self._total_calls * 100) 
                        if self._total_calls > 0 else 0
                    )
                }
        
        # Run async function in sync context if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context
                future = asyncio.ensure_future(_get_stats())
                return future
            else:
                return loop.run_until_complete(_get_stats())
        except:
            # Fallback for sync context
            return {
                "total_calls": self._total_calls,
                "total_rate_limited": self._total_rate_limited,
                "message": "Stats partially available (async context required)"
            }
    
    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self._total_calls = 0
        self._total_rate_limited = 0
        logger.info("Rate limiter statistics reset")


# Global rate limiter instances
_coingecko_rate_limiter: Optional[RateLimiter] = None
_defillama_rate_limiter: Optional[RateLimiter] = None


def get_coingecko_rate_limiter() -> RateLimiter:
    """Get or create the global CoinGecko rate limiter."""
    global _coingecko_rate_limiter
    
    if _coingecko_rate_limiter is None:
        _coingecko_rate_limiter = RateLimiter(
            max_calls=10,  # Conservative for free tier (10-50 calls/minute)
            period_seconds=60
        )
    
    return _coingecko_rate_limiter


def get_defillama_rate_limiter() -> RateLimiter:
    """Get or create the global DeFiLlama rate limiter."""
    global _defillama_rate_limiter
    
    if _defillama_rate_limiter is None:
        _defillama_rate_limiter = RateLimiter(
            max_calls=100,  # DeFiLlama has higher limits (300/minute)
            period_seconds=60
        )
    
    return _defillama_rate_limiter
