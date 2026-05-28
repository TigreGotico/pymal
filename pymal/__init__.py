"""pymal — Python scraper / API client for myanimelist.net."""
from pymal.anime import (
    get_anime,
    get_anime_episodes,
    get_anime_moreinfo,
    get_anime_news,
    get_anime_pictures,
    get_anime_recommendations,
    get_anime_reviews,
    get_anime_stats,
    get_anime_videos,
)
from pymal.character import get_character, get_character_pictures
from pymal.listing import (
    anime_genre,
    get_magazine_manga,
    get_producer_anime,
    iter_anime_genre,
    iter_magazine_manga,
    iter_manga_genre,
    iter_producer_anime,
    iter_top_anime,
    iter_top_manga,
    manga_genre,
    recent_recommendations,
    recent_reviews,
    season_schedule,
    seasonal_anime,
    top_anime,
    top_manga,
)
from pymal.manga import get_manga, get_manga_news, get_manga_pictures
from pymal.models import (
    Anime,
    AnimeCard,
    AnimeListEntry,
    AnimeScoreStats,
    AnimeStats,
    AnimeVideo,
    AuthorRole,
    Character,
    CharacterAnimeRole,
    CharacterCard,
    CharacterMangaRole,
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
    NewsEntry,
    Person,
    PersonCard,
    RecommendationCard,
    RelatedEntry,
    ReviewCard,
    SeasonalAnimeCard,
    StaffAnimeRole,
    StaffRole,
    UserFavorites,
    UserProfile,
    VARole,
    VoiceActorEntry,
)
from pymal.people import get_person, get_person_pictures
from pymal.search import (
    search_anime,
    search_characters,
    search_manga,
    search_people,
)
from pymal.transport import reset_session, set_delay
from pymal.arm import get_ids_from_imdb
from pymal.user import (
    get_user_anime_list,
    get_user_manga_list,
    get_user_profile,
    iter_user_anime_list,
    iter_user_manga_list,
)

__all__ = [
    # models
    "Anime", "AnimeCard", "AnimeListEntry", "AnimeScoreStats", "AnimeStats",
    "AnimeVideo", "AuthorRole",
    "Character", "CharacterAnimeRole", "CharacterCard", "CharacterMangaRole", "CharacterRole",
    "EpisodeEntry",
    "FavoriteAnime", "FavoriteCharacter", "FavoriteManga", "FavoritePerson",
    "Manga", "MangaCard", "MangaListEntry", "MangaStats",
    "NewsEntry",
    "Person", "PersonCard",
    "RecommendationCard", "RelatedEntry", "ReviewCard",
    "SeasonalAnimeCard", "StaffAnimeRole", "StaffRole",
    "UserFavorites", "UserProfile",
    "VARole", "VoiceActorEntry",
    # anime
    "get_anime", "get_anime_episodes", "get_anime_moreinfo", "get_anime_news",
    "get_anime_pictures", "get_anime_recommendations", "get_anime_reviews",
    "get_anime_stats", "get_anime_videos",
    # manga
    "get_manga", "get_manga_news", "get_manga_pictures",
    # character
    "get_character", "get_character_pictures",
    # people
    "get_person", "get_person_pictures",
    # search
    "search_anime", "search_manga", "search_characters", "search_people",
    # listing — single page
    "top_anime", "top_manga", "seasonal_anime", "season_schedule",
    "anime_genre", "manga_genre",
    "get_producer_anime", "get_magazine_manga",
    # listing — iterators (full pagination)
    "iter_top_anime", "iter_top_manga",
    "iter_anime_genre", "iter_manga_genre",
    "iter_producer_anime", "iter_magazine_manga",
    # global feeds
    "recent_reviews", "recent_recommendations",
    # user
    "get_user_profile",
    "get_user_anime_list", "iter_user_anime_list",
    "get_user_manga_list", "iter_user_manga_list",
    # transport
    "set_delay", "reset_session",
    # cross-reference
    "get_ids_from_imdb",
]


def get_anime_by_imdb(imdb_id: str) -> "Anime":
    """Fetch full Anime detail by IMDb ID.

    Chain: IMDb → TVmaze (title) → AniList (mal_id via idMal) → ARM → get_anime().

    Args:
        imdb_id: IMDb ID string, e.g. ``"tt0213338"``.

    Returns:
        A fully populated :class:`~pymal.models.Anime`.

    Raises:
        ValueError: when the IMDb ID cannot be resolved to a MAL ID.
        requests.HTTPError: on network failures.
    """
    data = get_ids_from_imdb(imdb_id)
    mal_id = data.get("myanimelist")
    if not mal_id:
        raise ValueError(f"Could not resolve IMDb ID {imdb_id!r} to a MAL ID")
    from pymal.anime import get_anime
    return get_anime(int(mal_id))


__all__.append("get_anime_by_imdb")
