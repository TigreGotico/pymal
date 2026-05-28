# Transport and HTTP Configuration

## set_delay(seconds)

```python
pymal.set_delay(3.0)
```

Sets the minimum delay between consecutive HTTP requests. The default is 1.5 seconds. MAL rate-limits scrapers and will return 429 or 403 responses if requests arrive too quickly. For bulk fetching operations, 2–3 seconds is recommended. For one-off lookups the default is usually fine.

The delay is enforced globally across all pymal functions.

---

## reset_session()

```python
pymal.reset_session()
```

Destroys the current HTTP session and forces a new one to be created on the next request. Use this after receiving a ban response (403/429) to get a fresh session with a new connection pool, or when switching proxy configurations at runtime.

---

## curl-cffi stealth mode

Install the optional dependency:

```bash
pip install pymal[stealth]
```

When `curl-cffi` is installed, pymal automatically uses it instead of `requests`. `curl-cffi` impersonates the TLS fingerprint of a real browser (Firefox or Chrome), which bypasses MAL's bot detection. Without stealth mode, MAL may return 403 for certain pages that inspect TLS fingerprints.

pymal selects the best available browser type at session creation time. No code change is required beyond the install.

---

## Using proxies

pymal does not have a built-in proxy setting. Inject proxies by patching the session after creation:

```python
import pymal
from pymal.transport import get_session

session = get_session()
session.proxies = {
    "http": "http://user:pass@proxy.example.com:8080",
    "https": "http://user:pass@proxy.example.com:8080",
}
```

Call `pymal.reset_session()` before this to ensure a fresh session. Because `get_session()` is lazy, call it once to trigger creation, then mutate the returned object.

---

## Caching responses

Use `requests-cache` to cache responses to disk and avoid re-fetching pages during development:

```bash
pip install requests-cache
```

```python
import requests_cache
import pymal
from pymal.transport import get_session

requests_cache.install_cache("mal_cache", expire_after=3600)
session = get_session()
```

`requests-cache` monkey-patches `requests.Session`, so it takes effect automatically. Note: this does not work when `curl-cffi` is the active session backend.

For `curl-cffi` caching, write a thin wrapper that serializes responses to disk manually and checks before calling `get_html`.
