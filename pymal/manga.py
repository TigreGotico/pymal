"""Manga detail, pictures, and news fetchers."""
from __future__ import annotations

from typing import List

from pymal._parse import parse_manga_page, parse_news_page, parse_pictures_page
from pymal.models import AuthorRole, Manga, NewsEntry, RelatedEntry
from pymal.transport import BASE_URL, get_html


def get_manga(mal_id: int) -> Manga:
    html = get_html(f"{BASE_URL}/manga/{mal_id}")
    data = parse_manga_page(html, mal_id)

    authors = [
        AuthorRole(
            mal_id=a["mal_id"], name=a["name"],
            url=a["url"], role=a["role"],
        )
        for a in data["authors"]
    ]

    related = {
        rel_type: [
            RelatedEntry(
                mal_id=e["mal_id"], title=e["title"],
                url=e["url"], entry_type=e["entry_type"],
            )
            for e in entries
        ]
        for rel_type, entries in data["related"].items()
    }

    return Manga(
        mal_id=data["mal_id"],
        title=data["title"],
        url=data["url"],
        image_url=data["image_url"],
        english_title=data["english_title"],
        japanese_title=data["japanese_title"],
        synonyms=data["synonyms"],
        type=data["type"],
        volumes=data["volumes"],
        chapters=data["chapters"],
        status=data["status"],
        published_from=data["published_from"],
        published_to=data["published_to"],
        genres=data["genres"],
        themes=data["themes"],
        demographics=data["demographics"],
        score=data["score"],
        scored_by=data["scored_by"],
        ranked=data["ranked"],
        popularity=data["popularity"],
        members=data["members"],
        favorites=data["favorites"],
        synopsis=data["synopsis"],
        background=data["background"],
        authors=authors,
        author_ids={a["name"]: a["mal_id"] for a in data["authors"]},
        serialization=data["serialization"],
        related=related,
    )


def get_manga_pictures(mal_id: int) -> List[str]:
    """Return all full-size image URLs from /manga/{id}/pics."""
    html = get_html(f"{BASE_URL}/manga/{mal_id}/pics")
    return parse_pictures_page(html)


def get_manga_news(mal_id: int) -> List[NewsEntry]:
    """Fetch news articles linked to a manga from /manga/{id}/news."""
    html = get_html(f"{BASE_URL}/manga/{mal_id}/news")
    return [
        NewsEntry(
            title=r["title"], url=r["url"], author=r["author"],
            date=r["date"], intro=r["intro"], image_url=r["image_url"],
            comments=r["comments"],
        )
        for r in parse_news_page(html)
    ]
