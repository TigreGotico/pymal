# User Endpoints

## get_user_profile(username)

```python
profile = pymal.get_user_profile("Xinil")
print(profile.username)
print(profile.joined, profile.location)
print("Anime completed:", profile.anime_stats.completed)
print("Manga mean score:", profile.manga_stats.mean_score)
for fav in profile.favorites.anime:
    print(f"  {fav.title}")
```

Returns `UserProfile`.

### Profile fields

| Field | Type | Description |
|-------|------|-------------|
| `username` | `str` | MAL username |
| `url` | `str` | `https://myanimelist.net/profile/<username>` |
| `image_url` | `str` | Avatar URL, empty string if default |
| `about` | `str` | User-written about text |
| `last_online` | `str` | Last seen string, e.g. `"Just Now"` or `"3 hours ago"` |
| `gender` | `str` | Gender, empty if not set |
| `birthday` | `str` | Birthday, empty if not set |
| `location` | `str` | Location, empty if not set |
| `website` | `str` | Website URL, empty if not set |
| `joined` | `str` | Join date, e.g. `"Nov 14, 2004"` |
| `anime_stats` | `AnimeStats` | Aggregate anime list statistics |
| `manga_stats` | `MangaStats` | Aggregate manga list statistics |
| `favorites` | `UserFavorites` | Favorited entries |

### AnimeStats fields

| Field | Type |
|-------|------|
| `watching` | `int` |
| `completed` | `int` |
| `on_hold` | `int` |
| `dropped` | `int` |
| `plan_to_watch` | `int` |
| `total_entries` | `int` |
| `days_watched` | `float` |
| `mean_score` | `float` |

### MangaStats fields

Same shape with `reading` / `plan_to_read` / `days_read` variants.

### UserFavorites

`favorites.anime` is `List[FavoriteAnime]`, `favorites.manga` is `List[FavoriteManga]`, `favorites.characters` is `List[FavoriteCharacter]`, `favorites.people` is `List[FavoritePerson]`. All fields documented in [models.md](models.md).

---

## get_user_anime_list(username, status)

```python
entries = pymal.get_user_anime_list("Xinil")
entries = pymal.get_user_anime_list("Xinil", status=2)
```

Returns `List[AnimeListEntry]`. Fetches all pages automatically.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | `str` | required | MAL username |
| `status` | `int` | `7` (all) | Status filter |

### Status values

| Value | Meaning |
|-------|---------|
| `1` | Watching |
| `2` | Completed |
| `3` | On Hold |
| `4` | Dropped |
| `6` | Plan to Watch |
| `7` | All (default) |

Each `AnimeListEntry` has: `mal_id`, `title`, `score` (user score, `None` if unscored), `status`, `status_label` (human-readable), `episodes_watched`, `total_episodes`, `image_url`, `url`.

---

## iter_user_anime_list(username, status)

Streaming variant. Yields `AnimeListEntry` objects one page at a time (300 entries per page).

```python
for entry in pymal.iter_user_anime_list("Xinil", status=2):
    print(entry.title, entry.score)
```

Use this when memory is a concern for large lists.

---

## get_user_manga_list(username, status)

```python
entries = pymal.get_user_manga_list("Xinil")
entries = pymal.get_user_manga_list("Xinil", status=1)
```

Returns `List[MangaListEntry]`. Status values:

| Value | Meaning |
|-------|---------|
| `1` | Reading |
| `2` | Completed |
| `3` | On Hold |
| `4` | Dropped |
| `6` | Plan to Read |
| `7` | All (default) |

Each `MangaListEntry` has: `mal_id`, `title`, `score`, `status`, `status_label`, `chapters_read`, `total_chapters`, `volumes_read`, `total_volumes`, `image_url`, `url`.

---

## iter_user_manga_list(username, status)

Streaming variant, same pattern as `iter_user_anime_list`.

---

## Pagination internals

pymal fetches user lists from `https://myanimelist.net/animelist/<username>/load.json?status=<status>&offset=<offset>`. Each page returns up to 300 entries. pymal increments the offset automatically until a page returns fewer than 300 entries.

---
[← Characters and people endpoints](characters_people.md) · [Home](../README.md) · [Data models →](models.md)
