"""Smoke tests — import and basic instantiation, no network required."""
import pytest
import pymal
from pymal.models import (
    Anime,
    AnimeCard,
    AnimeListEntry,
    AnimeStats,
    Character,
    CharacterCard,
    CharacterRole,
    EpisodeEntry,
    FavoriteAnime,
    FavoriteCharacter,
    FavoriteManga,
    FavoritePerson,
    Manga,
    MangaCard,
    MangaListEntry,
    MangaStats,
    Person,
    PersonCard,
    RecommendationCard,
    RelatedEntry,
    ReviewCard,
    SeasonalAnimeCard,
    StaffRole,
    UserFavorites,
    UserProfile,
    VoiceActorEntry,
)


def test_import():
    assert hasattr(pymal, "get_anime")
    assert hasattr(pymal, "search_anime")
    assert hasattr(pymal, "top_anime")


def test_anime_card_instantiation():
    card = AnimeCard(mal_id=1, title="Cowboy Bebop", url="https://myanimelist.net/anime/1", image_url="")
    assert str(card) == "Cowboy Bebop"
    assert card.as_dict["mal_id"] == 1


def test_anime_instantiation():
    anime = Anime(mal_id=1, title="Cowboy Bebop", url="https://myanimelist.net/anime/1")
    assert anime.title == "Cowboy Bebop"
    d = anime.as_dict
    assert d["genres"] == []
    assert d["related"] == {}


def test_manga_card_instantiation():
    card = MangaCard(mal_id=1, title="Berserk", url="https://myanimelist.net/manga/1", image_url="")
    assert str(card) == "Berserk"


def test_manga_instantiation():
    manga = Manga(mal_id=1, title="Berserk", url="https://myanimelist.net/manga/1")
    assert manga.as_dict["chapters"] is None


def test_character_card():
    card = CharacterCard(mal_id=1, name="Spike Spiegel", url="https://myanimelist.net/character/1", image_url="")
    assert str(card) == "Spike Spiegel"
    assert card.as_dict["favorites"] == 0


def test_character_instantiation():
    char = Character(mal_id=1, name="Spike Spiegel", url="https://myanimelist.net/character/1")
    assert char.as_dict["voice_actors"] == []


def test_person_card():
    card = PersonCard(mal_id=1, name="Koichi Yamadera", url="https://myanimelist.net/people/1", image_url="")
    assert str(card) == "Koichi Yamadera"


def test_person_instantiation():
    person = Person(mal_id=1, name="Koichi Yamadera", url="https://myanimelist.net/people/1")
    assert person.as_dict["va_roles"] == []


def test_episode_entry():
    ep = EpisodeEntry(number=1, title="Asteroid Blues", japanese_title="アステロイド・ブルース", aired="1998-04-03", discussion_url="")
    assert str(ep) == "1. Asteroid Blues"


def test_review_card():
    r = ReviewCard(author="user", author_url="", score=10, helpful_count=5, created_at="2023-01-01", summary="Great!", url="")
    assert r.score == 10


def test_recommendation_card():
    rec = RecommendationCard(mal_id=2, title="Trigun", url="https://myanimelist.net/anime/2", image_url="", num_recommendations=3)
    assert rec.num_recommendations == 3


def test_seasonal_anime_card():
    card = SeasonalAnimeCard(mal_id=1, title="Test", url="", image_url="", type="TV", source="Manga", episodes=12)
    assert card.as_dict["episodes"] == 12


def test_user_profile_instantiation():
    profile = UserProfile(username="testuser", url="https://myanimelist.net/profile/testuser")
    assert profile.anime_stats.watching == 0
    assert profile.manga_stats.reading == 0
    assert profile.favorites.anime == []


def test_anime_list_entry():
    entry = AnimeListEntry(mal_id=1, title="Cowboy Bebop", score=10, status=2)
    assert entry.status_label == "Completed"
    assert entry.as_dict["status_label"] == "Completed"


def test_manga_list_entry():
    entry = MangaListEntry(mal_id=1, title="Berserk", score=None, status=1)
    assert entry.status_label == "Reading"


def test_related_entry():
    rel = RelatedEntry(mal_id=5, title="Something", url="https://myanimelist.net/anime/5", entry_type="anime")
    assert rel.as_dict["entry_type"] == "anime"


def test_set_delay():
    pymal.set_delay(2.0)
    pymal.set_delay(1.5)


def test_all_exports():
    for name in pymal.__all__:
        assert hasattr(pymal, name), f"Missing export: {name}"


def test_favorite_anime():
    fav = FavoriteAnime(mal_id=1, title="Cowboy Bebop", url="https://myanimelist.net/anime/1", image_url="", type="TV", start_year=1998)
    assert str(fav) == "Cowboy Bebop"
    assert fav.as_dict["start_year"] == 1998


def test_favorite_manga():
    fav = FavoriteManga(mal_id=2, title="Berserk", url="https://myanimelist.net/manga/2", image_url="")
    assert fav.as_dict["type"] == ""
    assert fav.as_dict["start_year"] is None


def test_favorite_character():
    fav = FavoriteCharacter(mal_id=1, name="Spike Spiegel", url="https://myanimelist.net/character/1", image_url="",
                            anime_title="Cowboy Bebop", anime_url="https://myanimelist.net/anime/1")
    assert str(fav) == "Spike Spiegel"
    assert fav.as_dict["anime_title"] == "Cowboy Bebop"


def test_favorite_person():
    fav = FavoritePerson(mal_id=1, name="Koichi Yamadera", url="https://myanimelist.net/people/1", image_url="")
    assert fav.as_dict["name"] == "Koichi Yamadera"


def test_user_favorites_typed():
    favorites = UserFavorites(
        anime=[FavoriteAnime(mal_id=1, title="Cowboy Bebop", url="", image_url="")],
        characters=[FavoriteCharacter(mal_id=5, name="Spike", url="", image_url="")],
    )
    d = favorites.as_dict
    assert d["anime"][0]["mal_id"] == 1
    assert d["characters"][0]["name"] == "Spike"
    assert d["manga"] == []
    assert d["people"] == []
