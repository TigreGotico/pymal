"""HTTP transport for myanimelist.net with optional curl-cffi stealth mode."""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

BASE_URL = "https://myanimelist.net"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://myanimelist.net/",
}

_session: Optional[Any] = None
_last_request: float = 0.0
_min_delay: float = 1.5


def set_delay(seconds: float) -> None:
    """Set the minimum delay between HTTP requests (default: 1.5 s)."""
    global _min_delay
    _min_delay = max(0.0, seconds)


def _make_session() -> Any:
    try:
        from unblock_requests import CloudflareSession  # type: ignore

        session = CloudflareSession(env_prefix="PYMAL", wayback_fallback=True)
        session.headers.update(_HEADERS)
        return session
    except Exception:
        pass

    try:
        import curl_cffi.requests as cffi_requests  # type: ignore
        from curl_cffi import BrowserType

        supported = {e.value for e in BrowserType}
        for candidate in ("firefox120", "firefox135", "chrome124", "chrome136"):
            if candidate in supported:
                impersonate = candidate
                break
        else:
            impersonate = next(iter(supported))
        session = cffi_requests.Session(impersonate=impersonate)
        session.headers.update(_HEADERS)
        return session
    except ImportError:
        import requests

        session = requests.Session()
        session.headers.update(_HEADERS)
        return session


def get_session() -> Any:
    global _session
    if _session is None:
        _session = _make_session()
    return _session


def reset_session() -> None:
    global _session
    _session = None


def _throttle() -> None:
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < _min_delay:
        time.sleep(_min_delay - elapsed)
    _last_request = time.time()


def get_html(path: str, **kwargs: Any) -> str:
    _throttle()
    url = path if path.startswith("http") else f"{BASE_URL}{path}"
    resp = get_session().get(url, **kwargs)
    resp.raise_for_status()
    return resp.text


def get_json(path: str, **kwargs: Any) -> Any:
    _throttle()
    url = path if path.startswith("http") else f"{BASE_URL}{path}"
    resp = get_session().get(url, headers={"Accept": "application/json"}, **kwargs)
    resp.raise_for_status()
    return resp.json()
