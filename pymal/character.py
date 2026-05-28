"""Character detail and pictures fetchers."""
from __future__ import annotations

from typing import List

from pymal._parse import parse_character_page, parse_pictures_page
from pymal.models import (
    Character,
    CharacterAnimeRole,
    CharacterMangaRole,
    VoiceActorEntry,
)
from pymal.transport import BASE_URL, get_html


def get_character(mal_id: int) -> Character:
    html = get_html(f"{BASE_URL}/character/{mal_id}")
    data = parse_character_page(html, mal_id)

    anime_roles = [
        CharacterAnimeRole(
            anime_title=r["anime_title"], anime_url=r["anime_url"],
            image_url=r["image_url"], role=r["role"],
        )
        for r in data["anime_roles"]
    ]
    manga_roles = [
        CharacterMangaRole(
            manga_title=r["manga_title"], manga_url=r["manga_url"],
            image_url=r["image_url"], role=r["role"],
        )
        for r in data["manga_roles"]
    ]
    voice_actors = [
        VoiceActorEntry(
            name=v["name"], url=v["url"],
            image_url=v["image_url"], language=v["language"],
        )
        for v in data["voice_actors"]
    ]

    return Character(
        mal_id=data["mal_id"],
        name=data["name"],
        url=data["url"],
        japanese_name=data["japanese_name"],
        about=data["about"],
        image_url=data["image_url"],
        anime_roles=anime_roles,
        manga_roles=manga_roles,
        voice_actors=voice_actors,
    )


def get_character_pictures(mal_id: int) -> List[str]:
    """Return all full-size image URLs from /character/{id}/pictures."""
    html = get_html(f"{BASE_URL}/character/{mal_id}/pictures")
    return parse_pictures_page(html)
