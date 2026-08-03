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
    if source not in _VALID_SOURCES:
        raise ValueError(f"source must be one of {sorted(_VALID_SOURCES)}")
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
    from pymal.models import ExternalIds

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
