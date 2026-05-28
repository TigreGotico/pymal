"""ARM cross-reference client — anime ID cross-referencing in one call.

ARM (https://arm.haglund.dev) maps between MyAnimeList, AniList, AniDB,
Kitsu, TheTVDB, TMDB, IMDb, and several others for every anime title.

Supported source names: myanimelist, anilist, anidb, kitsu, thetvdb,
themoviedb, imdb, simkl, livechart, animenewsnetwork, anisearch.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

LOG = logging.getLogger("pymal.arm")

_ARM_URL = "https://arm.haglund.dev/api/v2/ids"
_HEADERS = {"User-Agent": "metadatarr/0.1"}

# Cache keyed by (source, id) so all lookup directions are cached
_CACHE: Dict[Tuple[str, str], dict] = {}

_VALID_SOURCES = frozenset({
    "myanimelist", "anilist", "anidb", "kitsu", "thetvdb",
    "themoviedb", "imdb", "simkl", "livechart", "animenewsnetwork", "anisearch",
})


def get_ids(mal_id: int) -> dict:
    """Look up by MAL ID. Shorthand for get_ids_by(source='myanimelist', id=mal_id)."""
    return get_ids_by("myanimelist", str(mal_id))


def get_ids_by(source: str, id: str) -> dict:
    """Call ARM with any supported source + id, return raw response dict.

    source: one of myanimelist, anilist, anidb, kitsu, thetvdb, themoviedb,
            imdb, simkl, livechart, animenewsnetwork, anisearch
    id: the ID value as a string (MAL uses integers; IMDb uses 'tt...' strings)
    """
    key = (source, str(id))
    if key in _CACHE:
        return _CACHE[key]
    try:
        import requests
        resp = requests.get(
            _ARM_URL,
            params={"source": source, "id": id},
            headers=_HEADERS,
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        # cross-populate cache: once we have the full map, cache all directions
        _CACHE[key] = data
        if data.get("myanimelist"):
            _CACHE[("myanimelist", str(data["myanimelist"]))] = data
        if data.get("anilist"):
            _CACHE[("anilist", str(data["anilist"]))] = data
        if data.get("anidb"):
            _CACHE[("anidb", str(data["anidb"]))] = data
        return data
    except Exception as exc:
        LOG.warning("ARM lookup failed for %s=%s: %s", source, id, exc)
        return {}


def to_external_ids(arm_data: dict):
    """Convert ARM response dict to an ExternalIds instance.

    Always includes mal_id when present in the ARM response, so callers
    that looked up by anilist_id or anidb_id also get mal_id back.
    """
    from mediavocab.models import ExternalIds

    if not arm_data:
        return ExternalIds()

    extra: dict = {}
    for key in ("kitsu", "simkl", "livechart", "anime-planet", "animenewsnetwork",
                "anisearch", "animecountdown"):
        val = arm_data.get(key)
        if val is not None:
            extra[key] = str(val)

    return ExternalIds(
        mal_id=arm_data.get("myanimelist") or None,
        anilist_id=arm_data.get("anilist") or None,
        anidb_id=arm_data.get("anidb") or None,
        imdb=arm_data.get("imdb") or None,
        tmdb_tv=arm_data.get("themoviedb") or None,
        tvdb=arm_data.get("thetvdb") or None,
        extra=extra if extra else {},
    )


def _tvmaze_title(imdb_id: str):
    """Return (title, year) for an IMDb ID via TVmaze, or ('', None) on failure."""
    try:
        import requests
        r = requests.get(
            f"https://api.tvmaze.com/lookup/shows?imdb={imdb_id}",
            headers={"User-Agent": "metadatarr/0.1"},
            timeout=8,
        )
        if not r.ok:
            return "", None
        data = r.json()
        title = data.get("name", "")
        premiered = data.get("premiered") or ""
        year = int(premiered[:4]) if premiered and len(premiered) >= 4 else None
        return title, year
    except Exception as exc:
        LOG.warning("TVmaze lookup failed for imdb=%s: %s", imdb_id, exc)
        return "", None


def _anilist_search(title: str, year: Optional[int] = None):
    """Search AniList GraphQL for an anime title, return (anilist_id, mal_id).

    AniList's idMal field is the canonical MyAnimeList ID so this gives us
    the MAL ID without touching MAL's unreliable text search.
    """
    QUERY = """
    query($search: String) {
      Media(type: ANIME, search: $search, sort: SEARCH_MATCH) {
        id
        idMal
        startDate { year }
      }
    }
    """
    try:
        import requests
        r = requests.post(
            "https://graphql.anilist.co",
            json={"query": QUERY, "variables": {"search": title}},
            headers={"Content-Type": "application/json", "User-Agent": "metadatarr/0.1"},
            timeout=8,
        )
        r.raise_for_status()
        media = (r.json().get("data") or {}).get("Media") or {}
        anilist_id = media.get("id")
        mal_id = media.get("idMal")
        # Year filter: if hint provided and result year is off by more than 1, reject
        if year and anilist_id:
            result_year = (media.get("startDate") or {}).get("year")
            if result_year and abs(result_year - year) > 1:
                return None, None
        return anilist_id, mal_id
    except Exception as exc:
        LOG.warning("AniList search failed for title=%r: %s", title, exc)
        return None, None


def get_ids_from_imdb(imdb_id: str) -> dict:
    """Map an IMDb ID to all anime ID systems via TVmaze + AniList + ARM.

    Chain:
      1. TVmaze  — imdb_id → title, year
      2. AniList — title   → anilist_id, mal_id (idMal field)
      3. ARM     — mal_id  → full cross-reference dict

    Returns the ARM response dict (keys: myanimelist, anilist, anidb, imdb,
    thetvdb, themoviedb, kitsu, …), or an empty dict on failure.
    """
    # Check cache first
    key = ("imdb", imdb_id)
    if key in _CACHE:
        return _CACHE[key]

    title, year = _tvmaze_title(imdb_id)
    if not title:
        LOG.warning("get_ids_from_imdb: TVmaze could not resolve title for %s", imdb_id)
        return {}

    anilist_id, mal_id = _anilist_search(title, year)
    if not mal_id and not anilist_id:
        LOG.warning("get_ids_from_imdb: AniList found nothing for title=%r", title)
        return {}

    if mal_id:
        data = get_ids_by("myanimelist", str(mal_id))
    else:
        data = get_ids_by("anilist", str(anilist_id))

    if data:
        _CACHE[key] = data
    return data


def enrich_external_ids(ids) -> Optional[dict]:
    """Given any ExternalIds, call ARM using whichever ID it supports as a source.

    ARM supports lookup by: myanimelist, anilist, anidb, kitsu.
    TVDB and IMDb are returned by ARM but cannot be used as lookup keys.
    """
    if ids.mal_id:
        data = get_ids_by("myanimelist", str(ids.mal_id))
        if data:
            return data
    if ids.anilist_id:
        data = get_ids_by("anilist", str(ids.anilist_id))
        if data:
            return data
    if ids.anidb_id:
        data = get_ids_by("anidb", str(ids.anidb_id))
        if data:
            return data
    # kitsu is in extra dict
    kitsu = (ids.extra or {}).get("kitsu")
    if kitsu:
        data = get_ids_by("kitsu", str(kitsu))
        if data:
            return data
    return None
