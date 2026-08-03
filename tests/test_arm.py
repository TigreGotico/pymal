"""Unit tests for pymal.arm — no network required.

Regression coverage for two bugs found in review:
  1. get_ids_by() accepted any source string; _VALID_SOURCES existed but was
     never checked, so a typo'd source silently hit the ARM API with a
     source it does not support.
  2. to_external_ids() imported ExternalIds from the sibling `mediavocab`
     package, which pymal does not depend on — the function raised
     ImportError unconditionally.
"""
import pytest

from pymal import arm
from pymal.models import ExternalIds


def test_get_ids_by_rejects_unknown_source():
    with pytest.raises(ValueError):
        arm.get_ids_by("notasource", "1")


def test_get_ids_by_accepts_all_documented_sources():
    # Should not raise before ever reaching the network call.
    for source in arm._VALID_SOURCES:
        key = (source, "__validation_probe__")
        assert key not in arm._CACHE


def test_to_external_ids_empty():
    result = arm.to_external_ids({})
    assert isinstance(result, ExternalIds)
    assert result.mal_id is None


def test_to_external_ids_maps_known_fields():
    data = {
        "myanimelist": 1, "anilist": 1, "anidb": 1,
        "imdb": "tt0213338", "themoviedb": 30984, "thetvdb": 76885,
        "kitsu": 1, "simkl": 3287,
    }
    result = arm.to_external_ids(data)
    assert result.mal_id == 1
    assert result.anilist_id == 1
    assert result.anidb_id == 1
    assert result.imdb == "tt0213338"
    assert result.tmdb_tv == 30984
    assert result.tvdb == 76885
    assert result.extra["kitsu"] == "1"
    assert result.extra["simkl"] == "3287"
    assert result.as_dict["mal_id"] == 1
