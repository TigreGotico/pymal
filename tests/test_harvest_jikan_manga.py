"""Row-schema equivalence tests for the jikan_manga bulk harvester.

These lock the exact flat-row shape emitted by JikanMangaSource against a
realistic upstream sample — moved verbatim (schema unchanged) from
metadatarr's test_scrapers_batch1.py when the scraper was ported onto the
shared harvestkit engine.
"""
from __future__ import annotations

from harvestkit.engine import all_sources
from pymal.harvest import manga  # noqa: F401  (import registers JikanMangaSource)
from pymal.harvest.manga import JikanMangaSource


def test_jikan_manga_map_row_schema():
    src = JikanMangaSource()
    m = {
        "mal_id": 1,
        "title": "Monster",
        "title_english": "Monster",
        "title_japanese": "MONSTER",
        "titles": [{"type": "Default", "title": "Monster"}, {"type": "Synonym", "title": "MONSTAA"}],
        "type": "Manga",
        "status": "Finished",
        "chapters": 162,
        "volumes": 18,
        "published": {"prop": {"from": {"year": 1994, "month": 12, "day": 5},
                                "to": {"year": 2001, "month": 12, "day": 20}}},
        "authors": [{"name": "Urasawa, Naoki"}],
        "serializations": [{"name": "Big Comic Original"}],
        "genres": [{"name": "Mystery"}],
        "themes": [{"name": "Psychological"}],
        "demographics": [{"name": "Seinen"}],
        "score": 9.15,
        "scored_by": 60000,
        "rank": 1,
        "popularity": 30,
        "members": 200000,
        "synopsis": "s" * 600,
        "background": "b" * 400,
        "approved": True,
    }
    row = src.map_row(m)
    assert row["mal_id"] == 1
    assert row["aliases"] == ["MONSTAA"]
    assert row["published_from"] == "1994-12-05"
    assert row["published_to"] == "2001-12-20"
    assert len(row["synopsis"]) == 500
    assert len(row["background"]) == 300
    assert set(row) == {
        "mal_id", "title", "title_english", "title_japanese", "aliases",
        "type", "status", "chapters", "volumes", "published_from",
        "published_to", "authors", "serializations", "genres", "themes",
        "demographics", "score", "scored_by", "rank", "popularity",
        "members", "synopsis", "background", "approved",
    }


def test_jikan_manga_map_row_drops_records_without_mal_id():
    assert JikanMangaSource().map_row({"mal_id": None}) is None


def test_jikan_manga_fetch_respects_has_next_page():
    src = JikanMangaSource()
    src.get_json = lambda url, params: {
        "data": [{"mal_id": 1}],
        "pagination": {"has_next_page": False},
    }
    rows, cursor = src.fetch(1)
    assert len(rows) == 1
    assert cursor is None


def test_jikan_manga_registered():
    assert all_sources()["jikan_manga"] is JikanMangaSource
