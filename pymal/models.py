"""Data models for myanimelist.net objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AnimeScoreStats:
    """Score distribution and list-status counts from an anime's /stats page."""
    score_1: int = 0
    score_2: int = 0
    score_3: int = 0
    score_4: int = 0
    score_5: int = 0
    score_6: int = 0
    score_7: int = 0
    score_8: int = 0
    score_9: int = 0
    score_10: int = 0
    watching: int = 0
    completed: int = 0
    on_hold: int = 0
    dropped: int = 0
    plan_to_watch: int = 0

    @property
    def total_scored(self) -> int:
        return sum(getattr(self, f"score_{i}") for i in range(1, 11))

    @property
    def scores(self) -> Dict[int, int]:
        return {i: getattr(self, f"score_{i}") for i in range(1, 11)}

    @property
    def as_dict(self) -> dict:
        return {
            "scores": self.scores,
            "watching": self.watching, "completed": self.completed,
            "on_hold": self.on_hold, "dropped": self.dropped,
            "plan_to_watch": self.plan_to_watch,
            "total_scored": self.total_scored,
        }


@dataclass
class AnimeVideo:
    """A promotional video or episode entry from an anime's /video page."""
    title: str
    url: str
    thumbnail_url: str
    video_type: str  # "PV" | "CM" | "Episode" | "Other"

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "title": self.title, "url": self.url,
            "thumbnail_url": self.thumbnail_url, "video_type": self.video_type,
        }


@dataclass
class NewsEntry:
    """A news article linked to an anime or manga."""
    title: str
    url: str
    author: str
    date: str
    intro: str
    image_url: str
    comments: int = 0

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "title": self.title, "url": self.url, "author": self.author,
            "date": self.date, "intro": self.intro, "image_url": self.image_url,
            "comments": self.comments,
        }


@dataclass
class RelatedEntry:
    mal_id: int
    title: str
    url: str
    entry_type: str  # "anime" | "manga"

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {"mal_id": self.mal_id, "title": self.title, "url": self.url, "entry_type": self.entry_type}


@dataclass
class CharacterRole:
    mal_id: int
    name: str
    url: str
    image_url: str
    role: str
    voice_actor_name: str = ""
    va_url: str = ""
    va_image_url: str = ""

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "name": self.name, "url": self.url,
            "image_url": self.image_url, "role": self.role,
            "voice_actor_name": self.voice_actor_name, "va_url": self.va_url,
            "va_image_url": self.va_image_url,
        }


@dataclass
class StaffRole:
    mal_id: int
    name: str
    url: str
    image_url: str
    role: str

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {"mal_id": self.mal_id, "name": self.name, "url": self.url, "image_url": self.image_url, "role": self.role}


@dataclass
class AuthorRole:
    mal_id: int
    name: str
    url: str
    role: str

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {"mal_id": self.mal_id, "name": self.name, "url": self.url, "role": self.role}


@dataclass
class VARole:
    character_name: str
    character_url: str
    anime_title: str
    anime_url: str
    role: str

    def __str__(self) -> str:
        return self.character_name

    @property
    def as_dict(self) -> dict:
        return {
            "character_name": self.character_name, "character_url": self.character_url,
            "anime_title": self.anime_title, "anime_url": self.anime_url, "role": self.role,
        }


@dataclass
class StaffAnimeRole:
    anime_title: str
    anime_url: str
    role: str

    def __str__(self) -> str:
        return self.anime_title

    @property
    def as_dict(self) -> dict:
        return {"anime_title": self.anime_title, "anime_url": self.anime_url, "role": self.role}


@dataclass
class CharacterAnimeRole:
    anime_title: str
    anime_url: str
    image_url: str
    role: str

    def __str__(self) -> str:
        return self.anime_title

    @property
    def as_dict(self) -> dict:
        return {"anime_title": self.anime_title, "anime_url": self.anime_url, "image_url": self.image_url, "role": self.role}


@dataclass
class CharacterMangaRole:
    manga_title: str
    manga_url: str
    image_url: str
    role: str

    def __str__(self) -> str:
        return self.manga_title

    @property
    def as_dict(self) -> dict:
        return {"manga_title": self.manga_title, "manga_url": self.manga_url, "image_url": self.image_url, "role": self.role}


@dataclass
class VoiceActorEntry:
    name: str
    url: str
    image_url: str
    language: str

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {"name": self.name, "url": self.url, "image_url": self.image_url, "language": self.language}


@dataclass
class EpisodeEntry:
    number: int
    title: str
    japanese_title: str
    aired: str
    discussion_url: str

    def __str__(self) -> str:
        return f"{self.number}. {self.title}"

    @property
    def as_dict(self) -> dict:
        return {
            "number": self.number, "title": self.title, "japanese_title": self.japanese_title,
            "aired": self.aired, "discussion_url": self.discussion_url,
        }


@dataclass
class ReviewCard:
    author: str
    author_url: str
    score: Optional[int]
    helpful_count: int
    created_at: str
    summary: str
    url: str

    def __str__(self) -> str:
        return f"{self.author}: {self.summary[:60]}"

    @property
    def as_dict(self) -> dict:
        return {
            "author": self.author, "author_url": self.author_url, "score": self.score,
            "helpful_count": self.helpful_count, "created_at": self.created_at,
            "summary": self.summary, "url": self.url,
        }


@dataclass
class RecommendationCard:
    mal_id: int
    title: str
    url: str
    image_url: str
    num_recommendations: int

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url,
            "image_url": self.image_url, "num_recommendations": self.num_recommendations,
        }


@dataclass
class SeasonalAnimeCard:
    mal_id: int
    title: str
    url: str
    image_url: str
    type: str
    source: str
    episodes: Optional[int]
    studios: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    score: Optional[float] = None
    members: Optional[int] = None
    synopsis: str = ""

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url,
            "image_url": self.image_url, "type": self.type, "source": self.source,
            "episodes": self.episodes, "studios": self.studios, "genres": self.genres,
            "score": self.score, "members": self.members, "synopsis": self.synopsis,
        }


@dataclass
class AnimeCard:
    mal_id: int
    title: str
    url: str
    image_url: str
    score: Optional[float] = None
    type: str = ""
    episodes: Optional[int] = None
    status: str = ""
    season: str = ""
    members: Optional[int] = None

    def get(self) -> "Anime":
        from pymal.anime import get_anime
        return get_anime(self.mal_id)

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url,
            "image_url": self.image_url, "score": self.score, "type": self.type,
            "episodes": self.episodes, "status": self.status, "season": self.season,
            "members": self.members,
        }


@dataclass
class Anime:
    mal_id: int
    title: str
    url: str
    image_url: str = ""
    english_title: str = ""
    japanese_title: str = ""
    synonyms: List[str] = field(default_factory=list)
    type: str = ""
    episodes: Optional[int] = None
    status: str = ""
    aired_from: str = ""
    aired_to: str = ""
    season: str = ""
    year: Optional[int] = None
    broadcast: str = ""
    producers: List[str] = field(default_factory=list)
    licensors: List[str] = field(default_factory=list)
    studios: List[str] = field(default_factory=list)
    studio_ids: Dict[str, int] = field(default_factory=dict)
    producer_ids: Dict[str, int] = field(default_factory=dict)
    source: str = ""
    genres: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    demographics: List[str] = field(default_factory=list)
    duration: str = ""
    rating: str = ""
    score: Optional[float] = None
    scored_by: Optional[int] = None
    ranked: Optional[int] = None
    popularity: Optional[int] = None
    members: Optional[int] = None
    favorites: Optional[int] = None
    synopsis: str = ""
    background: str = ""
    related: Dict[str, List[RelatedEntry]] = field(default_factory=dict)
    characters: List[CharacterRole] = field(default_factory=list)
    staff: List[StaffRole] = field(default_factory=list)
    opening_themes: List[str] = field(default_factory=list)
    ending_themes: List[str] = field(default_factory=list)
    trailer_url: str = ""

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url, "image_url": self.image_url,
            "english_title": self.english_title, "japanese_title": self.japanese_title,
            "synonyms": self.synonyms, "type": self.type, "episodes": self.episodes,
            "status": self.status, "aired_from": self.aired_from, "aired_to": self.aired_to,
            "season": self.season, "year": self.year, "broadcast": self.broadcast,
            "producers": self.producers, "licensors": self.licensors, "studios": self.studios,
            "studio_ids": self.studio_ids, "producer_ids": self.producer_ids,
            "source": self.source, "genres": self.genres, "themes": self.themes,
            "demographics": self.demographics, "duration": self.duration, "rating": self.rating,
            "score": self.score, "scored_by": self.scored_by, "ranked": self.ranked,
            "popularity": self.popularity, "members": self.members, "favorites": self.favorites,
            "synopsis": self.synopsis, "background": self.background,
            "related": {k: [e.as_dict for e in v] for k, v in self.related.items()},
            "characters": [c.as_dict for c in self.characters],
            "staff": [s.as_dict for s in self.staff],
            "opening_themes": self.opening_themes, "ending_themes": self.ending_themes,
            "trailer_url": self.trailer_url,
        }


@dataclass
class MangaCard:
    mal_id: int
    title: str
    url: str
    image_url: str
    score: Optional[float] = None
    type: str = ""
    volumes: Optional[int] = None
    chapters: Optional[int] = None
    status: str = ""
    members: Optional[int] = None

    def get(self) -> "Manga":
        from pymal.manga import get_manga
        return get_manga(self.mal_id)

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url,
            "image_url": self.image_url, "score": self.score, "type": self.type,
            "volumes": self.volumes, "chapters": self.chapters, "status": self.status,
            "members": self.members,
        }


@dataclass
class Manga:
    mal_id: int
    title: str
    url: str
    image_url: str = ""
    english_title: str = ""
    japanese_title: str = ""
    synonyms: List[str] = field(default_factory=list)
    type: str = ""
    volumes: Optional[int] = None
    chapters: Optional[int] = None
    status: str = ""
    published_from: str = ""
    published_to: str = ""
    genres: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    demographics: List[str] = field(default_factory=list)
    score: Optional[float] = None
    scored_by: Optional[int] = None
    ranked: Optional[int] = None
    popularity: Optional[int] = None
    members: Optional[int] = None
    favorites: Optional[int] = None
    synopsis: str = ""
    background: str = ""
    authors: List[AuthorRole] = field(default_factory=list)
    author_ids: Dict[str, int] = field(default_factory=dict)
    serialization: List[str] = field(default_factory=list)
    related: Dict[str, List[RelatedEntry]] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url, "image_url": self.image_url,
            "english_title": self.english_title, "japanese_title": self.japanese_title,
            "synonyms": self.synonyms, "type": self.type, "volumes": self.volumes,
            "chapters": self.chapters, "status": self.status,
            "published_from": self.published_from, "published_to": self.published_to,
            "genres": self.genres, "themes": self.themes, "demographics": self.demographics,
            "score": self.score, "scored_by": self.scored_by, "ranked": self.ranked,
            "popularity": self.popularity, "members": self.members, "favorites": self.favorites,
            "synopsis": self.synopsis, "background": self.background,
            "authors": [a.as_dict for a in self.authors],
            "author_ids": self.author_ids,
            "serialization": self.serialization,
            "related": {k: [e.as_dict for e in v] for k, v in self.related.items()},
        }


@dataclass
class CharacterCard:
    mal_id: int
    name: str
    url: str
    image_url: str
    anime_count: int = 0
    manga_count: int = 0
    favorites: int = 0

    def get(self) -> "Character":
        from pymal.character import get_character
        return get_character(self.mal_id)

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "name": self.name, "url": self.url, "image_url": self.image_url,
            "anime_count": self.anime_count, "manga_count": self.manga_count, "favorites": self.favorites,
        }


@dataclass
class Character:
    mal_id: int
    name: str
    url: str
    japanese_name: str = ""
    about: str = ""
    image_url: str = ""
    anime_roles: List[CharacterAnimeRole] = field(default_factory=list)
    manga_roles: List[CharacterMangaRole] = field(default_factory=list)
    voice_actors: List[VoiceActorEntry] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "name": self.name, "url": self.url,
            "japanese_name": self.japanese_name, "about": self.about, "image_url": self.image_url,
            "anime_roles": [r.as_dict for r in self.anime_roles],
            "manga_roles": [r.as_dict for r in self.manga_roles],
            "voice_actors": [v.as_dict for v in self.voice_actors],
        }


@dataclass
class PersonCard:
    mal_id: int
    name: str
    url: str
    image_url: str

    def get(self) -> "Person":
        from pymal.people import get_person
        return get_person(self.mal_id)

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {"mal_id": self.mal_id, "name": self.name, "url": self.url, "image_url": self.image_url}


@dataclass
class Person:
    mal_id: int
    name: str
    url: str
    japanese_name: str = ""
    birthday: str = ""
    hometown: str = ""
    about: str = ""
    image_url: str = ""
    va_roles: List[VARole] = field(default_factory=list)
    staff_roles: List[StaffAnimeRole] = field(default_factory=list)

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "name": self.name, "url": self.url,
            "japanese_name": self.japanese_name, "birthday": self.birthday,
            "hometown": self.hometown, "about": self.about, "image_url": self.image_url,
            "va_roles": [r.as_dict for r in self.va_roles],
            "staff_roles": [r.as_dict for r in self.staff_roles],
        }


@dataclass
class AnimeStats:
    watching: int = 0
    completed: int = 0
    on_hold: int = 0
    dropped: int = 0
    plan_to_watch: int = 0
    total_entries: int = 0
    days_watched: float = 0.0
    mean_score: float = 0.0

    @property
    def as_dict(self) -> dict:
        return {
            "watching": self.watching, "completed": self.completed, "on_hold": self.on_hold,
            "dropped": self.dropped, "plan_to_watch": self.plan_to_watch,
            "total_entries": self.total_entries, "days_watched": self.days_watched,
            "mean_score": self.mean_score,
        }


@dataclass
class MangaStats:
    reading: int = 0
    completed: int = 0
    on_hold: int = 0
    dropped: int = 0
    plan_to_read: int = 0
    total_entries: int = 0
    days_read: float = 0.0
    mean_score: float = 0.0

    @property
    def as_dict(self) -> dict:
        return {
            "reading": self.reading, "completed": self.completed, "on_hold": self.on_hold,
            "dropped": self.dropped, "plan_to_read": self.plan_to_read,
            "total_entries": self.total_entries, "days_read": self.days_read,
            "mean_score": self.mean_score,
        }


@dataclass
class FavoriteAnime:
    mal_id: int
    title: str
    url: str
    image_url: str
    type: str = ""
    start_year: Optional[int] = None

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url,
            "image_url": self.image_url, "type": self.type, "start_year": self.start_year,
        }


@dataclass
class FavoriteManga:
    mal_id: int
    title: str
    url: str
    image_url: str
    type: str = ""
    start_year: Optional[int] = None

    def __str__(self) -> str:
        return self.title

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "url": self.url,
            "image_url": self.image_url, "type": self.type, "start_year": self.start_year,
        }


@dataclass
class FavoriteCharacter:
    mal_id: int
    name: str
    url: str
    image_url: str
    anime_title: str = ""
    anime_url: str = ""

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "name": self.name, "url": self.url,
            "image_url": self.image_url, "anime_title": self.anime_title, "anime_url": self.anime_url,
        }


@dataclass
class FavoritePerson:
    mal_id: int
    name: str
    url: str
    image_url: str

    def __str__(self) -> str:
        return self.name

    @property
    def as_dict(self) -> dict:
        return {"mal_id": self.mal_id, "name": self.name, "url": self.url, "image_url": self.image_url}


@dataclass
class UserFavorites:
    anime: List[FavoriteAnime] = field(default_factory=list)
    manga: List[FavoriteManga] = field(default_factory=list)
    characters: List[FavoriteCharacter] = field(default_factory=list)
    people: List[FavoritePerson] = field(default_factory=list)

    @property
    def as_dict(self) -> dict:
        return {
            "anime": [a.as_dict for a in self.anime],
            "manga": [m.as_dict for m in self.manga],
            "characters": [c.as_dict for c in self.characters],
            "people": [p.as_dict for p in self.people],
        }


@dataclass
class UserProfile:
    username: str
    url: str
    image_url: str = ""
    about: str = ""
    last_online: str = ""
    gender: str = ""
    birthday: str = ""
    location: str = ""
    website: str = ""
    joined: str = ""
    anime_stats: AnimeStats = field(default_factory=AnimeStats)
    manga_stats: MangaStats = field(default_factory=MangaStats)
    favorites: UserFavorites = field(default_factory=UserFavorites)

    def __str__(self) -> str:
        return self.username

    @property
    def as_dict(self) -> dict:
        return {
            "username": self.username, "url": self.url, "image_url": self.image_url,
            "about": self.about, "last_online": self.last_online, "gender": self.gender,
            "birthday": self.birthday, "location": self.location, "website": self.website,
            "joined": self.joined, "anime_stats": self.anime_stats.as_dict,
            "manga_stats": self.manga_stats.as_dict, "favorites": self.favorites.as_dict,
        }


_ANIME_STATUS_LABELS = {1: "Watching", 2: "Completed", 3: "On Hold", 4: "Dropped", 6: "Plan to Watch"}
_MANGA_STATUS_LABELS = {1: "Reading", 2: "Completed", 3: "On Hold", 4: "Dropped", 6: "Plan to Read"}


@dataclass
class AnimeListEntry:
    mal_id: int
    title: str
    score: Optional[int]
    status: int
    episodes_watched: int = 0
    total_episodes: Optional[int] = None
    image_url: str = ""
    url: str = ""

    def __str__(self) -> str:
        return self.title

    @property
    def status_label(self) -> str:
        return _ANIME_STATUS_LABELS.get(self.status, str(self.status))

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "score": self.score,
            "status": self.status, "status_label": self.status_label,
            "episodes_watched": self.episodes_watched, "total_episodes": self.total_episodes,
            "image_url": self.image_url, "url": self.url,
        }


@dataclass
class MangaListEntry:
    mal_id: int
    title: str
    score: Optional[int]
    status: int
    chapters_read: int = 0
    total_chapters: Optional[int] = None
    volumes_read: int = 0
    total_volumes: Optional[int] = None
    image_url: str = ""
    url: str = ""

    def __str__(self) -> str:
        return self.title

    @property
    def status_label(self) -> str:
        return _MANGA_STATUS_LABELS.get(self.status, str(self.status))

    @property
    def as_dict(self) -> dict:
        return {
            "mal_id": self.mal_id, "title": self.title, "score": self.score,
            "status": self.status, "status_label": self.status_label,
            "chapters_read": self.chapters_read, "total_chapters": self.total_chapters,
            "volumes_read": self.volumes_read, "total_volumes": self.total_volumes,
            "image_url": self.image_url, "url": self.url,
        }
