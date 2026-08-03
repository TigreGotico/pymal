# ARM cross-reference (`pymal.arm`)

[ARM](https://arm.haglund.dev) maps a title's ID across MyAnimeList, AniList,
AniDB, Kitsu, TheTVDB, TMDB, IMDb, and several smaller trackers. `pymal.arm`
is a thin client for it — useful when you have a MAL ID and need the matching
ID on another service, or vice versa.

This module talks to `arm.haglund.dev`, not `myanimelist.net`; it is not
subject to `pymal.set_delay()` and does not go through `pymal.transport`.

## Functions

### `get_ids(mal_id)`

Look up by MAL ID. Shorthand for `get_ids_by("myanimelist", str(mal_id))`.

```python
from pymal import arm

ids = arm.get_ids(1)   # Cowboy Bebop
print(ids["anilist"], ids["anidb"])
```

### `get_ids_by(source, id)`

Look up by any supported source. Raises `ValueError` if `source` is not one
of: `myanimelist`, `anilist`, `anidb`, `kitsu`, `thetvdb`, `themoviedb`,
`imdb`, `simkl`, `livechart`, `animenewsnetwork`, `anisearch`.

```python
ids = arm.get_ids_by("anilist", "1")
print(ids["myanimelist"])
```

Results are cached in-process, keyed by every `(source, id)` pair the
response covers, so a lookup by one source also warms the cache for the
others.

### `to_external_ids(arm_data)`

Convert a raw ARM response dict into an `ExternalIds` dataclass
(`pymal.models.ExternalIds`).

```python
from pymal import arm

ids = arm.to_external_ids(arm.get_ids(1))
print(ids.anilist_id, ids.imdb, ids.as_dict)
```

### `enrich_external_ids(ids)`

Given an `ExternalIds` instance that already has at least one of `mal_id`,
`anilist_id`, `anidb_id`, or a `kitsu` entry in `.extra`, calls ARM using
whichever it finds first and returns the raw response dict (or `None` if
none of those are set, or the lookup failed).

```python
from pymal.models import ExternalIds
from pymal import arm

partial = ExternalIds(anilist_id=1)
data = arm.enrich_external_ids(partial)
if data:
    full = arm.to_external_ids(data)
    print(full.mal_id)
```
