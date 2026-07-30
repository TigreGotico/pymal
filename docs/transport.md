# Transport and HTTP Configuration

## set_delay(seconds)

```python
pymal.set_delay(3.0)
```

Sets the minimum delay between consecutive HTTP requests. The default is 1.5 seconds. MAL rate-limits scrapers and returns 429 or 403 responses if requests arrive too quickly. Use 2 to 3 seconds for bulk fetching. The default works for one-off lookups.

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

When `curl-cffi` is installed, pymal uses it instead of `requests`. `curl-cffi` impersonates the TLS fingerprint of a real browser (Firefox or Chrome), which bypasses MAL's bot detection. Without stealth mode, MAL can return 403 for pages that inspect TLS fingerprints.

pymal selects the best available browser type at session creation time. The install is the only change you need to make.

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

`requests-cache` patches `requests.Session`, so it takes effect automatically. This does not work when `curl-cffi` is the active session backend.

For `curl-cffi` caching, write a wrapper that serializes responses to disk and checks the cache before it calls `get_html`.

---
[← Data models](models.md) · [Home](../README.md) · [Recipes →](recipes.md)
