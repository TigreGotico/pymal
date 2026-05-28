"""User profile and list fetchers."""
from __future__ import annotations

from typing import Iterator, List

from pymal._parse import (
    parse_anime_list_json,
    parse_manga_list_json,
    parse_user_profile,
)
from pymal.models import (
    AnimeListEntry,
    AnimeStats,
    FavoriteAnime,
    FavoriteCharacter,
    FavoriteManga,
    FavoritePerson,
    MangaListEntry,
    MangaStats,
    UserFavorites,
    UserProfile,
)
from pymal.transport import BASE_URL, get_html, get_json

_ANIME_STATUS_ALL = 7
_MANGA_STATUS_ALL = 7
_PAGE_SIZE = 300


def get_user_profile(username: str) -> UserProfile:
    html = get_html(f"{BASE_URL}/profile/{username}")
    data = parse_user_profile(html, username)

    a = data["anime_stats"]
    m = data["manga_stats"]
    f = data["favorites"]

    return UserProfile(
        username=data["username"],
        url=data["url"],
        image_url=data["image_url"],
        about=data["about"],
        last_online=data["last_online"],
        gender=data["gender"],
        birthday=data["birthday"],
        location=data["location"],
        website=data["website"],
        joined=data["joined"],
        anime_stats=AnimeStats(
            watching=a.get("watching", 0),
            completed=a.get("completed", 0),
            on_hold=a.get("on_hold", 0),
            dropped=a.get("dropped", 0),
            plan_to_watch=a.get("plan_to_watch", 0),
            total_entries=a.get("total_entries", 0),
            days_watched=a.get("days_watched", 0.0),
            mean_score=a.get("mean_score", 0.0),
        ),
        manga_stats=MangaStats(
            reading=m.get("reading", 0),
            completed=m.get("completed", 0),
            on_hold=m.get("on_hold", 0),
            dropped=m.get("dropped", 0),
            plan_to_read=m.get("plan_to_read", 0),
            total_entries=m.get("total_entries", 0),
            days_read=m.get("days_read", 0.0),
            mean_score=m.get("mean_score", 0.0),
        ),
        favorites=UserFavorites(
            anime=[
                FavoriteAnime(
                    mal_id=x.get("mal_id", 0),
                    title=x.get("title", ""),
                    url=x.get("url", ""),
                    image_url=x.get("image_url", ""),
                    type=x.get("type", ""),
                    start_year=x.get("start_year"),
                )
                for x in f.get("anime", [])
            ],
            manga=[
                FavoriteManga(
                    mal_id=x.get("mal_id", 0),
                    title=x.get("title", ""),
                    url=x.get("url", ""),
                    image_url=x.get("image_url", ""),
                    type=x.get("type", ""),
                    start_year=x.get("start_year"),
                )
                for x in f.get("manga", [])
            ],
            characters=[
                FavoriteCharacter(
                    mal_id=x.get("mal_id", 0),
                    name=x.get("title", x.get("name", "")),
                    url=x.get("url", ""),
                    image_url=x.get("image_url", ""),
                    anime_title=x.get("anime_title", ""),
                    anime_url=x.get("anime_url", ""),
                )
                for x in f.get("characters", [])
            ],
            people=[
                FavoritePerson(
                    mal_id=x.get("mal_id", 0),
                    name=x.get("title", x.get("name", "")),
                    url=x.get("url", ""),
                    image_url=x.get("image_url", ""),
                )
                for x in f.get("people", [])
            ],
        ),
    )


def get_user_anime_list(
    username: str,
    status: int = _ANIME_STATUS_ALL,
) -> List[AnimeListEntry]:
    return list(iter_user_anime_list(username, status=status))


def get_user_manga_list(
    username: str,
    status: int = _MANGA_STATUS_ALL,
) -> List[MangaListEntry]:
    return list(iter_user_manga_list(username, status=status))


def iter_user_anime_list(
    username: str,
    status: int = _ANIME_STATUS_ALL,
) -> Iterator[AnimeListEntry]:
    offset = 0
    while True:
        url = f"{BASE_URL}/animelist/{username}/load.json?status={status}&offset={offset}"
        data = get_json(url)
        if not data:
            break
        raw = parse_anime_list_json(data)
        for r in raw:
            yield AnimeListEntry(
                mal_id=r["mal_id"], title=r["title"], score=r["score"],
                status=r["status"], episodes_watched=r["episodes_watched"],
                total_episodes=r["total_episodes"],
                image_url=r["image_url"], url=r["url"],
            )
        if len(data) < _PAGE_SIZE:
            break
        offset += _PAGE_SIZE


def iter_user_manga_list(
    username: str,
    status: int = _MANGA_STATUS_ALL,
) -> Iterator[MangaListEntry]:
    offset = 0
    while True:
        url = f"{BASE_URL}/mangalist/{username}/load.json?status={status}&offset={offset}"
        data = get_json(url)
        if not data:
            break
        raw = parse_manga_list_json(data)
        for r in raw:
            yield MangaListEntry(
                mal_id=r["mal_id"], title=r["title"], score=r["score"],
                status=r["status"], chapters_read=r["chapters_read"],
                total_chapters=r["total_chapters"],
                volumes_read=r["volumes_read"], total_volumes=r["total_volumes"],
                image_url=r["image_url"], url=r["url"],
            )
        if len(data) < _PAGE_SIZE:
            break
        offset += _PAGE_SIZE
