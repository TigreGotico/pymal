"""People (voice actors / staff) detail and pictures fetchers."""
from __future__ import annotations

from typing import List

from pymal._parse import parse_person_page, parse_pictures_page
from pymal.models import Person, StaffAnimeRole, VARole
from pymal.transport import BASE_URL, get_html


def get_person(mal_id: int) -> Person:
    html = get_html(f"{BASE_URL}/people/{mal_id}")
    data = parse_person_page(html, mal_id)

    va_roles = [
        VARole(
            character_name=r["character_name"], character_url=r["character_url"],
            anime_title=r["anime_title"], anime_url=r["anime_url"],
            role=r["role"],
        )
        for r in data["va_roles"]
    ]
    staff_roles = [
        StaffAnimeRole(
            anime_title=r["anime_title"], anime_url=r["anime_url"],
            role=r["role"],
        )
        for r in data["staff_roles"]
    ]

    return Person(
        mal_id=data["mal_id"],
        name=data["name"],
        url=data["url"],
        japanese_name=data["japanese_name"],
        birthday=data["birthday"],
        hometown=data["hometown"],
        about=data["about"],
        image_url=data["image_url"],
        va_roles=va_roles,
        staff_roles=staff_roles,
    )


def get_person_pictures(mal_id: int) -> List[str]:
    """Return all full-size image URLs from /people/{id}/pictures."""
    html = get_html(f"{BASE_URL}/people/{mal_id}/pictures")
    return parse_pictures_page(html)
