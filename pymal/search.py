"""Search functions for anime, manga, characters, and people."""
from __future__ import annotations

from typing import List, Optional
from urllib.parse import quote_plus

from pymal._parse import (
    parse_anime_search,
    parse_character_search,
    parse_manga_search,
    parse_people_search,
)
from pymal.models import AnimeCard, CharacterCard, MangaCard, PersonCard
from pymal.transport import BASE_URL, get_html


def search_anime(
    query: str,
    page: int = 1,
    type: int = 0,
    status: int = 0,
    score: int = 0,
) -> List[AnimeCard]:
    offset = (page - 1) * 50 + 1
    url = (
        f"{BASE_URL}/anime.php?q={quote_plus(query)}"
        f"&type={type}&score={score}&status={status}&p={offset}"
    )
    html = get_html(url)
    raw = parse_anime_search(html)
    return [
        AnimeCard(
            mal_id=r["mal_id"], title=r["title"], url=r["url"],
            image_url=r["image_url"], score=r["score"], type=r["type"],
            episodes=r["episodes"], status=r["status"],
            season=r["season"], members=r["members"],
        )
        for r in raw
    ]


def search_manga(
    query: str,
    page: int = 1,
    type: int = 0,
    status: int = 0,
) -> List[MangaCard]:
    offset = (page - 1) * 50 + 1
    url = (
        f"{BASE_URL}/manga.php?q={quote_plus(query)}"
        f"&type={type}&status={status}&p={offset}"
    )
    html = get_html(url)
    raw = parse_manga_search(html)
    return [
        MangaCard(
            mal_id=r["mal_id"], title=r["title"], url=r["url"],
            image_url=r["image_url"], score=r["score"], type=r["type"],
            volumes=r.get("volumes"), chapters=r.get("chapters"),
            status=r["status"], members=r["members"],
        )
        for r in raw
    ]


def search_characters(query: str) -> List[CharacterCard]:
    url = f"{BASE_URL}/character.php?q={quote_plus(query)}"
    html = get_html(url)
    raw = parse_character_search(html)
    return [
        CharacterCard(
            mal_id=r["mal_id"], name=r["name"], url=r["url"],
            image_url=r["image_url"], anime_count=r["anime_count"],
            manga_count=r["manga_count"], favorites=r["favorites"],
        )
        for r in raw
    ]


def search_people(query: str) -> List[PersonCard]:
    url = f"{BASE_URL}/people.php?q={quote_plus(query)}"
    html = get_html(url)
    raw = parse_people_search(html)
    return [
        PersonCard(
            mal_id=r["mal_id"], name=r["name"],
            url=r["url"], image_url=r["image_url"],
        )
        for r in raw
    ]
