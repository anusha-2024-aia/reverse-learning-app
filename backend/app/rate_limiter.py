import os
import sys
import time
from collections import defaultdict
from threading import Lock
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status, Depends
from app.models import User
from app.auth import get_current_user

def is_testing_mode() -> bool:
    if os.getenv("FORCE_RATE_LIMIT") == "True":
        return False
    return (
        os.getenv("TESTING") == "True" or
        os.getenv("ENVIRONMENT") == "testing" or
        os.getenv("DISABLE_RATE_LIMIT") == "True"
    )

_LIMITERS = []

class InMemoryRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Tracks timestamp lists per client/user key.
    """
    def __init__(self, requests_per_window: int = 5, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
        _LIMITERS.append(self)

    def clear(self):
        with self.lock:
            self.requests.clear()

    def is_rate_limited(self, key: str) -> Tuple[bool, int, int]:
        """
        Returns (is_limited, retry_after_seconds, remaining_requests)
        """
        if is_testing_mode():
            return False, 0, self.requests_per_window

        now = time.time()
        cutoff = now - self.window_seconds
        with self.lock:
            # Filter timestamps within current window
            timestamps = [t for t in self.requests[key] if t > cutoff]
            self.requests[key] = timestamps
            
            if len(timestamps) >= self.requests_per_window:
                oldest = timestamps[0]
                retry_after = int(max(1, oldest + self.window_seconds - now))
                return True, retry_after, 0
            else:
                self.requests[key].append(now)
                remaining = self.requests_per_window - len(self.requests[key])
                return False, 0, remaining

def reset_all_limiters():
    for limiter in _LIMITERS:
        limiter.clear()

def parse_env_limit(env_var_name: Optional[str], default_limit: int) -> int:
    if not env_var_name:
        return default_limit
    env_val = os.getenv(env_var_name)
    if not env_val:
        return default_limit
    try:
        env_val = env_val.strip()
        if "/" in env_val:
            return int(env_val.split("/")[0])
        return int(env_val)
    except Exception:
        return default_limit

def rate_limit_authenticated(
    default_limit: int = 5,
    window_seconds: int = 60,
    env_var_name: Optional[str] = None
):
    """
    Dependency factory for authenticated endpoints. Limits per user.id.
    Executes rate check AFTER get_current_user authentication and BEFORE route logic.
    """
    effective_limit = parse_env_limit(env_var_name, default_limit)
    limiter = InMemoryRateLimiter(requests_per_window=effective_limit, window_seconds=window_seconds)

    async def dependency(request: Request, current_user: User = Depends(get_current_user)):
        key = f"user:{current_user.id}"
        is_limited, retry_after, remaining = limiter.is_rate_limited(key)
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(effective_limit),
                    "X-RateLimit-Remaining": "0"
                }
            )
        return current_user

    return dependency

def rate_limit_ip(
    default_limit: int = 10,
    window_seconds: int = 60,
    env_var_name: Optional[str] = None
):
    """
    Dependency factory for unauthenticated endpoints. Limits per client IP address.
    """
    effective_limit = parse_env_limit(env_var_name, default_limit)
    limiter = InMemoryRateLimiter(requests_per_window=effective_limit, window_seconds=window_seconds)

    async def dependency(request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"ip:{client_ip}"
        is_limited, retry_after, remaining = limiter.is_rate_limited(key)
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(effective_limit),
                    "X-RateLimit-Remaining": "0"
                }
            )

    return dependency
