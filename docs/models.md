# Data Models

All public types are importable directly from `pymal`. This page lists every field on every model, grouped by the endpoint that returns it.

## Card vs full model pattern

Most search, top, and listing functions return "card" objects: lightweight summaries with a subset of fields. Call `.get()` on any card to fetch the full detail object with one HTTP request.

```python
cards = pymal.search_anime("bebop")
anime = cards[0].get()       # fetches full Anime object
```

Card types: `AnimeCard`, `MangaCard`, `CharacterCard`, `PersonCard`.

## `as_dict`

Every model exposes `.as_dict` (a property, not a method call). Nested objects are recursively serialized.

```python
d = anime.as_dict
print(d["genres"])
print(d["characters"][0]["name"])
```

---

## AnimeCard

`AnimeCard` is the summary returned by search, top, and listing functions.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `mal_id` | `int` | MAL numeric ID | `1` |
| `title` | `str` | Primary title | `"Cowboy Bebop"` |
| `url` | `str` | MAL page URL | `"https://myanimelist.net/anime/1"` |
| `image_url` | `str` | Cover image CDN URL | `"https://cdn.myanimelist.net/..."` |
| `score` | `Optional[float]` | Community score 1 to 10, `None` if not scored | `8.75` |
| `type` | `str` | Format string | `"TV"` |
| `episodes` | `Optional[int]` | Episode count, `None` if unknown | `26` |
| `status` | `str` | Airing status | `"Finished Airing"` |
| `season` | `str` | Season string | `"spring 1998"` |
| `members` | `Optional[int]` | List member count | `620000` |

`.get()` returns `Anime`.

---

## Anime

`Anime` is the full detail object returned by `get_anime`. It extends everything in `AnimeCard` plus:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `english_title` | `str` | English title, empty if none | `"Cowboy Bebop"` |
| `japanese_title` | `str` | Japanese title | `"カウボーイビバップ"` |
| `synonyms` | `List[str]` | Alternative titles | `["CB"]` |
| `aired_from` | `str` | First air date string | `"Apr 3, 1998"` |
| `aired_to` | `str` | Last air date string, empty if ongoing | `"Apr 24, 1999"` |
| `year` | `Optional[int]` | Premiere year | `1998` |
| `broadcast` | `str` | Broadcast schedule | `"Saturdays at 01:00"` |
| `producers` | `List[str]` | Producer names | `["Bandai Visual"]` |
| `licensors` | `List[str]` | Licensor names | `["Funimation"]` |
| `studios` | `List[str]` | Studio names | `["Sunrise"]` |
| `source` | `str` | Source material | `"Original"` |
| `genres` | `List[str]` | Genre names | `["Action", "Sci-Fi"]` |
| `themes` | `List[str]` | Theme names | `["Space"]` |
| `demographics` | `List[str]` | Demographic names | `["Seinen"]` |
| `duration` | `str` | Episode duration | `"24 min. per ep."` |
| `rating` | `str` | Age rating | `"R - 17+"` |
| `score` | `Optional[float]` | Score, `None` if unscored | `8.75` |
| `scored_by` | `Optional[int]` | Number of scorers | `400000` |
| `ranked` | `Optional[int]` | All-time rank, `None` if unranked | `39` |
| `popularity` | `Optional[int]` | Popularity rank | `39` |
| `members` | `Optional[int]` | Members count | `620000` |
| `favorites` | `Optional[int]` | Favorites count | `70000` |
| `synopsis` | `str` | Plot synopsis | `"In the year 2071..."` |
| `background` | `str` | Background/production notes, often empty | `""` |
| `related` | `Dict[str, List[RelatedEntry]]` | Related entries grouped by relation type | `{"Sequel": [...]}` |
| `characters` | `List[CharacterRole]` | Main/supporting characters with VA | `[...]` |
| `staff` | `List[StaffRole]` | Staff credits | `[...]` |
| `opening_themes` | `List[str]` | OP theme song titles | `["Tank!"]` |
| `ending_themes` | `List[str]` | ED theme song titles | `["The Real Folk Blues"]` |
| `trailer_url` | `str` | YouTube trailer URL, empty if none | `"https://youtube.com/..."` |

---

## MangaCard

`MangaCard` is the summary returned by `search_manga`, `top_manga`, and `manga_genre`.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `mal_id` | `int` | MAL numeric ID | `2` |
| `title` | `str` | Primary title | `"Berserk"` |
| `url` | `str` | MAL page URL | `"https://myanimelist.net/manga/2"` |
| `image_url` | `str` | Cover image URL | `"https://cdn.myanimelist.net/..."` |
| `score` | `Optional[float]` | Score, `None` if unscored | `9.47` |
| `type` | `str` | Format | `"Manga"` |
| `volumes` | `Optional[int]` | Volume count | `41` |
| `chapters` | `Optional[int]` | Chapter count | `374` |
| `status` | `str` | Publishing status | `"Finished"` |
| `members` | `Optional[int]` | Members count | `580000` |

`.get()` returns `Manga`.

---

## Manga

`Manga` is the full detail object returned by `get_manga`. It extends `MangaCard` plus:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `english_title` | `str` | English title | `"Berserk"` |
| `japanese_title` | `str` | Japanese title | `"ベルセルク"` |
| `synonyms` | `List[str]` | Alternative titles | `[]` |
| `published_from` | `str` | Start publish date | `"Aug 25, 1989"` |
| `published_to` | `str` | End publish date | `"Jul 26, 2021"` |
| `genres` | `List[str]` | Genres | `["Action", "Dark Fantasy"]` |
| `themes` | `List[str]` | Themes | `["Gore", "Mythology"]` |
| `demographics` | `List[str]` | Demographics | `["Seinen"]` |
| `score` | `Optional[float]` | Score | `9.47` |
| `scored_by` | `Optional[int]` | Number of scorers | `220000` |
| `ranked` | `Optional[int]` | Rank | `1` |
| `popularity` | `Optional[int]` | Popularity rank | `16` |
| `members` | `Optional[int]` | Members | `580000` |
| `favorites` | `Optional[int]` | Favorites | `140000` |
| `synopsis` | `str` | Synopsis | `"Guts is a lone mercenary..."` |
| `background` | `str` | Background notes | `""` |
| `authors` | `List[AuthorRole]` | Author entries with roles | `[...]` |
| `serialization` | `List[str]` | Magazine names | `["Young Animal"]` |
| `related` | `Dict[str, List[RelatedEntry]]` | Related entries | `{}` |

---

## CharacterCard

`CharacterCard` is the summary returned by `search_characters`.

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `mal_id` | `int` | MAL character ID | `1` |
| `name` | `str` | Character name | `"Spike Spiegel"` |
| `url` | `str` | Character page URL | `"https://myanimelist.net/character/1"` |
| `image_url` | `str` | Character image | `"https://cdn.myanimelist.net/..."` |
| `anime_count` | `int` | Number of anime appearances | `1` |
| `manga_count` | `int` | Number of manga appearances | `0` |
| `favorites` | `int` | Favorites count | `45000` |

`.get()` returns `Character`.

---

## Character

`Character` is the full detail object returned by `get_character`.

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL ID |
| `name` | `str` | Name |
| `url` | `str` | Page URL |
| `japanese_name` | `str` | Japanese name, empty if not provided |
| `about` | `str` | Character description, truncated at 2000 chars |
| `image_url` | `str` | Image URL |
| `anime_roles` | `List[CharacterAnimeRole]` | Anime appearances |
| `manga_roles` | `List[CharacterMangaRole]` | Manga appearances |
| `voice_actors` | `List[VoiceActorEntry]` | Voice actors by language |

---

## PersonCard

`PersonCard` is the summary returned by `search_people`.

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL person ID |
| `name` | `str` | Person name |
| `url` | `str` | Profile URL |
| `image_url` | `str` | Photo URL |

`.get()` returns `Person`.

---

## Person

`Person` is the full detail object returned by `get_person`.

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL ID |
| `name` | `str` | Name |
| `url` | `str` | Profile URL |
| `japanese_name` | `str` | Japanese name |
| `birthday` | `str` | Birthday string, empty if private |
| `hometown` | `str` | Hometown, empty if not listed |
| `about` | `str` | Biography, truncated at 2000 chars |
| `image_url` | `str` | Photo URL |
| `va_roles` | `List[VARole]` | Voice acting credits |
| `staff_roles` | `List[StaffAnimeRole]` | Anime staff credits |

---

## SeasonalAnimeCard

Returned by `seasonal_anime()` and `season_schedule()`.

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL ID |
| `title` | `str` | Title |
| `url` | `str` | Page URL |
| `image_url` | `str` | Cover image |
| `type` | `str` | Format (TV, Movie, OVA, ONA) |
| `source` | `str` | Source material |
| `episodes` | `Optional[int]` | Episode count, `None` if unknown |
| `studios` | `List[str]` | Studios |
| `genres` | `List[str]` | Genres |
| `score` | `Optional[float]` | Score, `None` if not yet scored |
| `members` | `Optional[int]` | Members |
| `synopsis` | `str` | Short synopsis |

---

## AnimeListEntry / MangaListEntry

Returned by `get_user_anime_list` / `get_user_manga_list`.

### AnimeListEntry

Each entry describes one anime on a user's list.

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL ID |
| `title` | `str` | Anime title |
| `score` | `Optional[int]` | User score 1 to 10, `None` if not scored |
| `status` | `int` | Status code (see user docs) |
| `status_label` | `str` (property) | Human-readable status |
| `episodes_watched` | `int` | Episodes watched |
| `total_episodes` | `Optional[int]` | Total episodes in series |
| `image_url` | `str` | Cover image |
| `url` | `str` | MAL page URL |

### MangaListEntry

Each entry describes one manga on a user's list.

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL ID |
| `title` | `str` | Manga title |
| `score` | `Optional[int]` | User score |
| `status` | `int` | Status code |
| `status_label` | `str` (property) | Human-readable status |
| `chapters_read` | `int` | Chapters read |
| `total_chapters` | `Optional[int]` | Total chapters |
| `volumes_read` | `int` | Volumes read |
| `total_volumes` | `Optional[int]` | Total volumes |
| `image_url` | `str` | Cover image |
| `url` | `str` | MAL page URL |

`status_label` maps numeric codes to strings: 1=Watching, 2=Completed, 3=On Hold, 4=Dropped, 6=Plan to Watch (or analogous manga variants).

---

## UserProfile

`UserProfile` is the full profile object returned by `get_user_profile`.

| Field | Type | Description |
|-------|------|-------------|
| `username` | `str` | MAL username |
| `url` | `str` | Profile URL |
| `image_url` | `str` | Avatar URL, empty if default |
| `about` | `str` | About text, truncated at 1000 chars |
| `last_online` | `str` | Last online string |
| `gender` | `str` | Gender, empty if not set |
| `birthday` | `str` | Birthday, empty if not set |
| `location` | `str` | Location, empty if not set |
| `website` | `str` | Website URL, empty if not set |
| `joined` | `str` | Join date string |
| `anime_stats` | `AnimeStats` | Anime statistics |
| `manga_stats` | `MangaStats` | Manga statistics |
| `favorites` | `UserFavorites` | Favorited entries |

---

## AnimeStats / MangaStats

### AnimeStats

`AnimeStats` counts a user's anime list entries by status.

| Field | Type | Description |
|-------|------|-------------|
| `watching` | `int` | Entries with status=Watching |
| `completed` | `int` | Completed entries |
| `on_hold` | `int` | On-hold entries |
| `dropped` | `int` | Dropped entries |
| `plan_to_watch` | `int` | Plan-to-watch entries |
| `total_entries` | `int` | Total list entries |
| `days_watched` | `float` | Cumulative days watched |
| `mean_score` | `float` | Mean score across scored entries |

### MangaStats

Same shape, with `reading` / `plan_to_read` / `days_read` instead of anime equivalents.

---

## UserFavorites

`UserFavorites` groups the entries a user marked as favorites, by entry type.

| Field | Type | Description |
|-------|------|-------------|
| `anime` | `List[FavoriteAnime]` | Favorite anime |
| `manga` | `List[FavoriteManga]` | Favorite manga |
| `characters` | `List[FavoriteCharacter]` | Favorite characters |
| `people` | `List[FavoritePerson]` | Favorite people |

### FavoriteAnime / FavoriteManga

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL ID |
| `title` | `str` | Title |
| `url` | `str` | Page URL |
| `image_url` | `str` | Cover image |
| `type` | `str` | Format, empty if not parsed |
| `start_year` | `Optional[int]` | Start year, `None` if not parsed |

### FavoriteCharacter

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL character ID |
| `name` | `str` | Character name |
| `url` | `str` | Character page URL |
| `image_url` | `str` | Character image |
| `anime_title` | `str` | Source anime title, empty if not parsed |
| `anime_url` | `str` | Source anime URL, empty if not parsed |

### FavoritePerson

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL person ID |
| `name` | `str` | Person name |
| `url` | `str` | Profile URL |
| `image_url` | `str` | Photo URL |

---

## Supporting types

These types appear nested inside the models above.

### RelatedEntry

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | MAL ID |
| `title` | `str` | Title |
| `url` | `str` | Page URL |
| `entry_type` | `str` | `"anime"` or `"manga"` |

### CharacterRole (in Anime.characters)

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | Character MAL ID |
| `name` | `str` | Character name |
| `url` | `str` | Character URL |
| `image_url` | `str` | Image URL |
| `role` | `str` | `"Main"` or `"Supporting"` |
| `voice_actor_name` | `str` | Japanese VA name, empty if none |
| `va_url` | `str` | VA profile URL |
| `va_image_url` | `str` | VA photo URL |

### StaffRole (in Anime.staff)

Each entry names one crew member and their production role.

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | Person MAL ID |
| `name` | `str` | Person name |
| `url` | `str` | Profile URL |
| `image_url` | `str` | Photo URL |
| `role` | `str` | Staff role, e.g. `"Director"` |

### AuthorRole (in Manga.authors)

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | Person MAL ID |
| `name` | `str` | Person name |
| `url` | `str` | Profile URL |
| `role` | `str` | `"Story"`, `"Art"`, or `"Story & Art"` |

### VARole (in Person.va_roles)

Each entry links one character to the anime the person voiced them in.

| Field | Type | Description |
|-------|------|-------------|
| `character_name` | `str` | Character name |
| `character_url` | `str` | Character URL |
| `anime_title` | `str` | Anime title |
| `anime_url` | `str` | Anime URL |
| `role` | `str` | `"Main"` or `"Supporting"` |

### StaffAnimeRole (in Person.staff_roles)

| Field | Type | Description |
|-------|------|-------------|
| `anime_title` | `str` | Anime title |
| `anime_url` | `str` | Anime URL |
| `role` | `str` | Staff role |

### VoiceActorEntry (in Character.voice_actors)

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | VA name |
| `url` | `str` | Profile URL |
| `image_url` | `str` | Photo URL |
| `language` | `str` | Language, e.g. `"Japanese"` |

### EpisodeEntry

Each entry describes one aired episode, from `get_anime_episodes`.

| Field | Type | Description |
|-------|------|-------------|
| `number` | `int` | Episode number |
| `title` | `str` | English title |
| `japanese_title` | `str` | Japanese title |
| `aired` | `str` | Air date string |
| `discussion_url` | `str` | MAL episode discussion URL |

### ReviewCard

Each entry is one user review, from `get_anime_reviews`.

| Field | Type | Description |
|-------|------|-------------|
| `author` | `str` | Reviewer username |
| `author_url` | `str` | Profile URL |
| `score` | `Optional[int]` | Score given by reviewer |
| `helpful_count` | `int` | Number of helpful votes |
| `created_at` | `str` | Date string |
| `summary` | `str` | Review text, truncated at 500 chars |
| `url` | `str` | Review permalink |

### RecommendationCard

| Field | Type | Description |
|-------|------|-------------|
| `mal_id` | `int` | Recommended anime MAL ID |
| `title` | `str` | Title |
| `url` | `str` | Page URL |
| `image_url` | `str` | Cover image |
| `num_recommendations` | `int` | Number of users who recommended this |

### CharacterAnimeRole / CharacterMangaRole

Fields: `anime_title`/`manga_title`, `anime_url`/`manga_url`, `image_url`, `role`.

---
[← User endpoints](user.md) · [Home](../README.md) · [Transport and HTTP configuration →](transport.md)
