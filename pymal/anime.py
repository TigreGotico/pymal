"""Anime detail, episodes, reviews, recommendations, stats, pictures, videos, news."""
from __future__ import annotations

from typing import List

from pymal._parse import (
    parse_anime_page,
    parse_anime_stats_page,
    parse_characters_staff_page,
    parse_episodes_page,
    parse_moreinfo_page,
    parse_news_page,
    parse_pictures_page,
    parse_recommendations_page,
    parse_reviews_page,
    parse_videos_page,
)
from pymal.models import (
    Anime,
    AnimeScoreStats,
    AnimeVideo,
    CharacterRole,
    EpisodeEntry,
    NewsEntry,
    RecommendationCard,
    ReviewCard,
    StaffRole,
)
from pymal.transport import BASE_URL, get_html


def _anime_base_url(html: str, mal_id: int) -> str:
    """Extract canonical URL (with slug) from the anime detail page."""
    import re as _re
    m = _re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', html)
    if m:
        return m.group(1).rstrip("/")
    m = _re.search(r'<meta[^>]*property="og:url"[^>]*content="([^"]+)"', html)
    if m:
        return m.group(1).rstrip("/")
    return f"{BASE_URL}/anime/{mal_id}"


def get_anime(mal_id: int) -> Anime:
    html = get_html(f"{BASE_URL}/anime/{mal_id}")
    data = parse_anime_page(html, mal_id)

    base_url = _anime_base_url(html, mal_id)
    char_html = get_html(f"{base_url}/characters")
    chars_raw, staff_raw = parse_characters_staff_page(char_html)

    characters = [
        CharacterRole(
            mal_id=c["mal_id"], name=c["name"], url=c["url"],
            image_url=c["image_url"], role=c["role"],
            voice_actor_name=c["voice_actor_name"],
            va_url=c["va_url"], va_image_url=c["va_image_url"],
        )
        for c in chars_raw
    ]
    staff = [
        StaffRole(
            mal_id=s["mal_id"], name=s["name"], url=s["url"],
            image_url=s["image_url"], role=s["role"],
        )
        for s in staff_raw
    ]

    from pymal.models import RelatedEntry

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

    return Anime(
        mal_id=data["mal_id"],
        title=data["title"],
        url=data["url"],
        image_url=data["image_url"],
        english_title=data["english_title"],
        japanese_title=data["japanese_title"],
        synonyms=data["synonyms"],
        type=data["type"],
        episodes=data["episodes"],
        status=data["status"],
        aired_from=data["aired_from"],
        aired_to=data["aired_to"],
        season=data["season"],
        year=data["year"],
        broadcast=data["broadcast"],
        producers=data["producers"],
        licensors=data["licensors"],
        studios=data["studios"],
        studio_ids=data.get("studio_ids", {}),
        producer_ids=data.get("producer_ids", {}),
        source=data["source"],
        genres=data["genres"],
        themes=data["themes"],
        demographics=data["demographics"],
        duration=data["duration"],
        rating=data["rating"],
        score=data["score"],
        scored_by=data["scored_by"],
        ranked=data["ranked"],
        popularity=data["popularity"],
        members=data["members"],
        favorites=data["favorites"],
        synopsis=data["synopsis"],
        background=data["background"],
        related=related,
        characters=characters,
        staff=staff,
        opening_themes=data["opening_themes"],
        ending_themes=data["ending_themes"],
        trailer_url=data["trailer_url"],
    )


def get_anime_episodes(mal_id: int) -> List[EpisodeEntry]:
    html = get_html(f"{BASE_URL}/anime/{mal_id}/episode")
    raw = parse_episodes_page(html)
    return [
        EpisodeEntry(
            number=e["number"], title=e["title"],
            japanese_title=e["japanese_title"],
            aired=e["aired"], discussion_url=e["discussion_url"],
        )
        for e in raw
    ]


def get_anime_reviews(mal_id: int) -> List[ReviewCard]:
    html = get_html(f"{BASE_URL}/anime/{mal_id}/reviews")
    raw = parse_reviews_page(html)
    return [
        ReviewCard(
            author=r["author"], author_url=r["author_url"],
            score=r["score"], helpful_count=r["helpful_count"],
            created_at=r["created_at"], summary=r["summary"], url=r["url"],
        )
        for r in raw
    ]


def get_anime_recommendations(mal_id: int) -> List[RecommendationCard]:
    html = get_html(f"{BASE_URL}/anime/{mal_id}/userrecs")
    raw = parse_recommendations_page(html)
    return [
        RecommendationCard(
            mal_id=r["mal_id"], title=r["title"], url=r["url"],
            image_url=r["image_url"], num_recommendations=r["num_recommendations"],
        )
        for r in raw
    ]


def get_anime_stats(mal_id: int) -> AnimeScoreStats:
    """Fetch score distribution and list-status counts from /anime/{id}/stats."""
    html = get_html(f"{BASE_URL}/anime/{mal_id}/stats")
    raw = parse_anime_stats_page(html)
    scores = raw["scores"]
    return AnimeScoreStats(
        score_1=scores.get(1, 0), score_2=scores.get(2, 0),
        score_3=scores.get(3, 0), score_4=scores.get(4, 0),
        score_5=scores.get(5, 0), score_6=scores.get(6, 0),
        score_7=scores.get(7, 0), score_8=scores.get(8, 0),
        score_9=scores.get(9, 0), score_10=scores.get(10, 0),
        watching=raw["watching"], completed=raw["completed"],
        on_hold=raw["on_hold"], dropped=raw["dropped"],
        plan_to_watch=raw["plan_to_watch"],
    )


def get_anime_pictures(mal_id: int) -> List[str]:
    """Return all full-size image URLs from /anime/{id}/pics."""
    html = get_html(f"{BASE_URL}/anime/{mal_id}/pics")
    return parse_pictures_page(html)


def get_anime_videos(mal_id: int) -> List[AnimeVideo]:
    """Fetch PV/CM video entries from /anime/{id}/video."""
    html = get_html(f"{BASE_URL}/anime/{mal_id}/video")
    return [
        AnimeVideo(
            title=r["title"], url=r["url"],
            thumbnail_url=r["thumbnail_url"], video_type=r["video_type"],
        )
        for r in parse_videos_page(html)
    ]


def get_anime_news(mal_id: int) -> List[NewsEntry]:
    """Fetch news articles linked to an anime from /anime/{id}/news."""
    html = get_html(f"{BASE_URL}/anime/{mal_id}/news")
    return [
        NewsEntry(
            title=r["title"], url=r["url"], author=r["author"],
            date=r["date"], intro=r["intro"], image_url=r["image_url"],
            comments=r["comments"],
        )
        for r in parse_news_page(html)
    ]


def get_anime_moreinfo(mal_id: int) -> str:
    """Fetch the 'More Information' text block from /anime/{id}/moreinfo."""
    html = get_html(f"{BASE_URL}/anime/{mal_id}/moreinfo")
    return parse_moreinfo_page(html)
