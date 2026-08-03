"""Regression tests replaying real recorded MyAnimeList HTML responses.

Fixtures under tests/fixtures/ were recorded with a single bounded live GET
through pymal's own transport (real User-Agent, no auth) on 2026-08-03:

  - anime_1_userrecs.html      <- https://myanimelist.net/anime/1/userrecs
  - manga_genre_1_action_p1.html <- https://myanimelist.net/manga/genre/1/Action?p=1&page=1
  - profile_xinil.html         <- https://myanimelist.net/profile/Xinil

Each test replays the saved bytes through the parser — no network is used here.
"""
import os

import pytest

from pymal._parse import (
    parse_manga_genre_page,
    parse_recommendations_page,
    parse_user_profile,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name: str) -> str:
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Recommendations — MAL redesigned the carousel away from div.userrecs-col
# to <li class="btn-anime">; the old regex matched nothing.
# ---------------------------------------------------------------------------

def test_recommendations_happy_path():
    html = _load("anime_1_userrecs.html")
    recs = parse_recommendations_page(html)
    assert len(recs) > 10
    titles = {r["title"] for r in recs}
    assert "Samurai Champloo" in titles
    assert "Trigun" in titles
    samurai = next(r for r in recs if r["title"] == "Samurai Champloo")
    assert samurai["mal_id"] == 205
    assert samurai["url"] == "https://myanimelist.net/anime/205"
    assert samurai["num_recommendations"] == 122
    assert samurai["image_url"].startswith("https://cdn.myanimelist.net/")


def test_recommendations_dedupes_by_mal_id():
    html = _load("anime_1_userrecs.html")
    recs = parse_recommendations_page(html)
    ids = [r["mal_id"] for r in recs]
    assert len(ids) == len(set(ids))


def test_recommendations_empty_html():
    assert parse_recommendations_page("") == []
    assert parse_recommendations_page("<html><body>no recs here</body></html>") == []


def test_recommendations_malformed_html():
    # unclosed tags / truncated markup must not raise
    broken = '<li class="btn-anime" title="Broken"><a href="/recommendations/anime/1-2"'
    assert parse_recommendations_page(broken) == []


# ---------------------------------------------------------------------------
# Manga genre listing — genre/magazine pages use the seasonal-anime card
# grid, not the topmanga ranking-list table; the old parser always
# returned an empty list for these URLs.
# ---------------------------------------------------------------------------

def test_manga_genre_happy_path():
    html = _load("manga_genre_1_action_p1.html")
    cards = parse_manga_genre_page(html)
    assert len(cards) == 100
    berserk = next(c for c in cards if c["title"] == "Berserk")
    assert berserk["mal_id"] == 2
    assert berserk["url"] == "https://myanimelist.net/manga/2/Berserk"
    assert berserk["status"] == "Publishing"
    assert "Action" in berserk["genres"]
    assert berserk["synopsis"]


def test_manga_genre_missing_volumes_chapters_is_none():
    html = _load("manga_genre_1_action_p1.html")
    cards = parse_manga_genre_page(html)
    berserk = next(c for c in cards if c["title"] == "Berserk")
    # Berserk is ongoing with unknown vol/chapter counts on this listing page ("?")
    assert berserk["volumes"] is None
    assert berserk["chapters"] is None


def test_manga_genre_dedupes_by_mal_id():
    html = _load("manga_genre_1_action_p1.html")
    cards = parse_manga_genre_page(html)
    ids = [c["mal_id"] for c in cards]
    assert len(ids) == len(set(ids))


def test_manga_genre_empty_html():
    assert parse_manga_genre_page("") == []
    assert parse_manga_genre_page("<div>nothing here</div>") == []


# ---------------------------------------------------------------------------
# User profile — "Total Entries" is a plain <span>label</span><span>N</span>
# pair (not the anchor-terminated pattern used for status counts), and
# favorite characters/people use relative hrefs (/character/.., /people/..)
# unlike favorite anime/manga which are absolute. Both were silently
# dropped before the fix.
# ---------------------------------------------------------------------------

def test_user_profile_total_entries():
    html = _load("profile_xinil.html")
    data = parse_user_profile(html, "Xinil")
    assert data["anime_stats"]["total_entries"] == 399
    assert data["manga_stats"]["total_entries"] == 76
    # status counts (already-working anchor-based rows) must stay correct
    assert data["anime_stats"]["completed"] == 233
    assert data["anime_stats"]["days_watched"] == 142.3
    assert data["anime_stats"]["mean_score"] == 7.37


def test_user_profile_favorite_characters_and_people():
    html = _load("profile_xinil.html")
    data = parse_user_profile(html, "Xinil")
    chars = data["favorites"]["characters"]
    people = data["favorites"]["people"]
    assert len(chars) == 9
    assert len(people) == 6

    spike = next(c for c in chars if c["name"] == "Spiegel, Spike")
    assert spike["mal_id"] == 1
    assert spike["url"] == "https://myanimelist.net/character/1/Spike_Spiegel"
    assert spike["anime_title"] == "Cowboy Bebop"
    assert spike["image_url"].startswith("https://cdn.myanimelist.net/")

    seki = next(p for p in people if p["name"] == "Seki, Tomokazu")
    assert seki["mal_id"] == 1
    assert seki["url"] == "https://myanimelist.net/people/1/Tomokazu_Seki"


def test_user_profile_favorite_anime_still_works():
    """Regression guard: absolute-URL favorites (anime/manga) must not break."""
    html = _load("profile_xinil.html")
    data = parse_user_profile(html, "Xinil")
    anime = data["favorites"]["anime"]
    assert len(anime) == 6
    cowboy = next(a for a in anime if a["title"] == "Cowboy Bebop")
    assert cowboy["mal_id"] == 1
    assert cowboy["image_url"].startswith("https://cdn.myanimelist.net/")


def test_user_profile_missing_favorites_section():
    data = parse_user_profile("<html><body>no favorites here</body></html>", "nobody")
    assert data["favorites"]["characters"] == []
    assert data["favorites"]["people"] == []
    assert data["favorites"]["anime"] == []
    assert data["anime_stats"] == {}
