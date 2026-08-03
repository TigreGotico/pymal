"""Top lists, seasonal anime, genre/producer/magazine listings, and global feeds."""
from __future__ import annotations

from typing import Iterator, List

from pymal._parse import (
    parse_genre_page,
    parse_global_recommendations,
    parse_global_reviews,
    parse_last_page,
    parse_magazine_page,
    parse_manga_genre_page,
    parse_producer_page,
    parse_seasonal_anime,
    parse_top_anime,
    parse_top_manga,
)
from pymal.models import AnimeCard, MangaCard, SeasonalAnimeCard
from pymal.transport import BASE_URL, get_html

_TOP_ANIME_TYPES = frozenset(
    {"all", "airing", "upcoming", "tv", "movie", "ova", "ona", "special", "bypopularity", "favorite"}
)
_TOP_MANGA_TYPES = frozenset(
    {"all", "manga", "novels", "oneshots", "doujin", "manhwa", "manhua", "bypopularity", "favorite"}
)


# ---------------------------------------------------------------------------
# Top lists
# ---------------------------------------------------------------------------

def top_anime(type: str = "all", page: int = 1) -> List[AnimeCard]:
    """Fetch one page (50 entries) from the anime top list.

    type: all | airing | upcoming | tv | movie | ova | ona | special | bypopularity | favorite
    """
    if type not in _TOP_ANIME_TYPES:
        raise ValueError(f"type must be one of {_TOP_ANIME_TYPES}")
    offset = (page - 1) * 50
    html = get_html(f"{BASE_URL}/topanime.php?type={type}&limit={offset}")
    return [_make_anime_card(r) for r in parse_top_anime(html)]


def iter_top_anime(type: str = "all") -> Iterator[AnimeCard]:
    """Yield every entry in the anime top list, paginating automatically."""
    page = 1
    while True:
        cards = top_anime(type=type, page=page)
        if not cards:
            break
        yield from cards
        page += 1


def top_manga(type: str = "all", page: int = 1) -> List[MangaCard]:
    """Fetch one page (50 entries) from the manga top list.

    type: all | manga | novels | oneshots | doujin | manhwa | manhua | bypopularity | favorite
    """
    if type not in _TOP_MANGA_TYPES:
        raise ValueError(f"type must be one of {_TOP_MANGA_TYPES}")
    offset = (page - 1) * 50
    html = get_html(f"{BASE_URL}/topmanga.php?type={type}&limit={offset}")
    return [_make_manga_card(r) for r in parse_top_manga(html)]


def iter_top_manga(type: str = "all") -> Iterator[MangaCard]:
    """Yield every entry in the manga top list, paginating automatically."""
    page = 1
    while True:
        cards = top_manga(type=type, page=page)
        if not cards:
            break
        yield from cards
        page += 1


# ---------------------------------------------------------------------------
# Seasonal
# ---------------------------------------------------------------------------

def seasonal_anime(year: int, season: str) -> List[SeasonalAnimeCard]:
    """All anime airing in a given season.

    season: spring | summer | fall | winter
    """
    season = season.lower()
    if season not in ("spring", "summer", "fall", "winter"):
        raise ValueError("season must be spring, summer, fall, or winter")
    html = get_html(f"{BASE_URL}/anime/season/{year}/{season}")
    raw = parse_genre_page(html)
    if not raw:
        raw = parse_seasonal_anime(html)
    return [_make_seasonal_card(r) for r in raw]


def season_schedule() -> List[SeasonalAnimeCard]:
    """Upcoming season broadcast schedule."""
    html = get_html(f"{BASE_URL}/anime/season/schedule")
    raw = parse_genre_page(html)
    if not raw:
        raw = parse_seasonal_anime(html)
    return [_make_seasonal_card(r) for r in raw]


# ---------------------------------------------------------------------------
# Genre listings
# ---------------------------------------------------------------------------

def anime_genre(genre_id: int, genre_name: str = "", page: int = 1) -> List[AnimeCard]:
    """Fetch one page (100 entries) of anime for a genre.

    Common genre IDs: 1=Action, 2=Adventure, 4=Comedy, 8=Drama, 9=Ecchi,
    10=Fantasy, 12=Hentai, 14=Horror, 22=Romance, 24=Sci-Fi, 37=Supernatural.
    Full list in docs/anime.md.
    """
    slug = f"{genre_id}/{genre_name}" if genre_name else str(genre_id)
    html = get_html(f"{BASE_URL}/anime/genre/{slug}?p=1&page={page}")
    return [_make_anime_card(r) for r in parse_genre_page(html)]


def iter_anime_genre(genre_id: int, genre_name: str = "") -> Iterator[AnimeCard]:
    """Yield every anime for a genre, paginating automatically until the last page."""
    slug = f"{genre_id}/{genre_name}" if genre_name else str(genre_id)
    page = 1
    last = None
    while True:
        html = get_html(f"{BASE_URL}/anime/genre/{slug}?p=1&page={page}")
        if last is None:
            last = parse_last_page(html)
        raw = parse_genre_page(html)
        if not raw:
            break
        for r in raw:
            yield _make_anime_card(r)
        if page >= last:
            break
        page += 1


def manga_genre(genre_id: int, genre_name: str = "", page: int = 1) -> List[MangaCard]:
    """Fetch one page of manga for a genre."""
    slug = f"{genre_id}/{genre_name}" if genre_name else str(genre_id)
    html = get_html(f"{BASE_URL}/manga/genre/{slug}?p=1&page={page}")
    raw = parse_manga_genre_page(html)
    if not raw:
        raw = parse_top_manga(html)
    if not raw:
        from pymal._parse import parse_manga_search
        raw = parse_manga_search(html)
    return [_make_manga_card(r) for r in raw]


def iter_manga_genre(genre_id: int, genre_name: str = "") -> Iterator[MangaCard]:
    """Yield every manga for a genre, paginating automatically."""
    slug = f"{genre_id}/{genre_name}" if genre_name else str(genre_id)
    page = 1
    last = None
    while True:
        html = get_html(f"{BASE_URL}/manga/genre/{slug}?p=1&page={page}")
        if last is None:
            last = parse_last_page(html)
        raw = parse_manga_genre_page(html)
        if not raw:
            raw = parse_top_manga(html)
        if not raw:
            from pymal._parse import parse_manga_search
            raw = parse_manga_search(html)
        if not raw:
            break
        for r in raw:
            yield _make_manga_card(r)
        if page >= last:
            break
        page += 1


# ---------------------------------------------------------------------------
# Producer / Studio listings  (/anime/producer/{id}/{slug}?p={page})
# ---------------------------------------------------------------------------

def get_producer_anime(producer_id: int, producer_name: str = "", page: int = 1) -> List[AnimeCard]:
    """Fetch one page of anime from a producer/studio page."""
    slug = f"{producer_id}/{producer_name}" if producer_name else str(producer_id)
    html = get_html(f"{BASE_URL}/anime/producer/{slug}?p=1&page={page}")
    raw = parse_genre_page(html)
    if not raw:
        raw = parse_top_anime(html)
    return [_make_anime_card(r) for r in raw]


def iter_producer_anime(producer_id: int, producer_name: str = "") -> Iterator[AnimeCard]:
    """Yield every anime from a producer/studio page, paginating automatically."""
    slug = f"{producer_id}/{producer_name}" if producer_name else str(producer_id)
    page = 1
    last = None
    while True:
        html = get_html(f"{BASE_URL}/anime/producer/{slug}?p=1&page={page}")
        if last is None:
            last = parse_last_page(html)
        raw = parse_genre_page(html)
        if not raw:
            raw = parse_top_anime(html)
        if not raw:
            break
        for r in raw:
            yield _make_anime_card(r)
        if page >= last:
            break
        page += 1


# ---------------------------------------------------------------------------
# Magazine listings  (/manga/magazine/{id}/{slug}?p={page})
# ---------------------------------------------------------------------------

def get_magazine_manga(magazine_id: int, magazine_name: str = "", page: int = 1) -> List[MangaCard]:
    """Fetch one page of manga from a magazine/serialization page."""
    slug = f"{magazine_id}/{magazine_name}" if magazine_name else str(magazine_id)
    html = get_html(f"{BASE_URL}/manga/magazine/{slug}?p={page}")
    return [_make_manga_card(r) for r in parse_magazine_page(html)]


def iter_magazine_manga(magazine_id: int, magazine_name: str = "") -> Iterator[MangaCard]:
    """Yield every manga from a magazine page, paginating automatically."""
    slug = f"{magazine_id}/{magazine_name}" if magazine_name else str(magazine_id)
    page = 1
    last = None
    while True:
        html = get_html(f"{BASE_URL}/manga/magazine/{slug}?p={page}")
        if last is None:
            last = parse_last_page(html)
        raw = parse_magazine_page(html)
        if not raw:
            break
        for r in raw:
            yield _make_manga_card(r)
        if page >= last:
            break
        page += 1


# ---------------------------------------------------------------------------
# Global feeds
# ---------------------------------------------------------------------------

def recent_reviews(type: str = "anime", page: int = 1) -> list:
    """Fetch recent reviews from /reviews.php.

    type: "anime" or "manga"
    Returns raw dicts with keys: author, author_url, score, helpful_count,
    created_at, summary, url.
    """
    if type not in ("anime", "manga"):
        raise ValueError('type must be "anime" or "manga"')
    html = get_html(f"{BASE_URL}/reviews.php?t={type}&p={page}")
    return parse_global_reviews(html)


def recent_recommendations(type: str = "anime", page: int = 1) -> list:
    """Fetch recent recommendations from /recommendations.php.

    type: "anime" or "manga"
    Returns raw dicts with keys: source_id, source_title, source_url,
    rec_id, rec_title, rec_url, username, text.
    """
    if type not in ("anime", "manga"):
        raise ValueError('type must be "anime" or "manga"')
    html = get_html(f"{BASE_URL}/recommendations.php?s=recentrecs&t={type}&p={page}")
    return parse_global_recommendations(html)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_anime_card(r: dict) -> AnimeCard:
    return AnimeCard(
        mal_id=r["mal_id"], title=r["title"], url=r["url"],
        image_url=r.get("image_url", ""), score=r.get("score"),
        type=r.get("type", ""), episodes=r.get("episodes"),
        status=r.get("status", ""), season=r.get("season", ""),
        members=r.get("members"),
    )


def _make_manga_card(r: dict) -> MangaCard:
    return MangaCard(
        mal_id=r["mal_id"], title=r["title"], url=r["url"],
        image_url=r.get("image_url", ""), score=r.get("score"),
        type=r.get("type", ""), volumes=r.get("volumes"),
        chapters=r.get("chapters"), status=r.get("status", ""),
        members=r.get("members"),
    )


def _make_seasonal_card(r: dict) -> SeasonalAnimeCard:
    return SeasonalAnimeCard(
        mal_id=r["mal_id"], title=r["title"], url=r["url"],
        image_url=r.get("image_url", ""), type=r.get("type", ""),
        source=r.get("source", ""), episodes=r.get("episodes"),
        studios=r.get("studios", []), genres=r.get("genres", []),
        score=r.get("score"), members=r.get("members"),
        synopsis=r.get("synopsis", ""),
    )
