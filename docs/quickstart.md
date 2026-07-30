# Quickstart

pymal is a Python scraper for [MyAnimeList](https://myanimelist.net) (MAL). It fetches and parses HTML pages and JSON list endpoints from MAL, and returns typed Python dataclasses. It needs no API key.

## Install

```bash
pip install pymal
```

For stealth mode (bypasses bot detection using `curl-cffi`):

```bash
pip install pymal[stealth]
```

## Five-minute guide

### Search for an anime

```python
import pymal

results = pymal.search_anime("cowboy bebop")
for card in results[:3]:
    print(card.mal_id, card.title, card.score)
```

### Get full detail

```python
anime = pymal.get_anime(1)
print(anime.title)
print(anime.synopsis[:200])
print("Genres:", anime.genres)
print("Score:", anime.score)
for char in anime.characters[:3]:
    print(f"  {char.name} ({char.role}) — VA: {char.voice_actor_name}")
```

### Search and then fetch

`AnimeCard` and `MangaCard` have a `.get()` method that fetches the full detail object:

```python
cards = pymal.search_anime("attack on titan")
first = cards[0].get()
print(first.title, first.episodes)
```

### User data

```python
profile = pymal.get_user_profile("Xinil")
print(profile.anime_stats.completed)
print([a.title for a in profile.favorites.anime])
```

### Convert to dict

Every model exposes `.as_dict`:

```python
d = pymal.get_anime(1).as_dict
import json
print(json.dumps(d, indent=2, default=str))
```

## Common gotchas

**Rate limiting.** MAL blocks scrapers that send too many requests per second. The default delay between requests is 1.5 seconds. Increase it for bulk operations:

```python
pymal.set_delay(3.0)
```

**Bot detection / 403 errors.** MAL detects headless requests. Install `pymal[stealth]` to use `curl-cffi`, which impersonates the TLS fingerprint of a real browser. If you still get blocked, run `pymal.reset_session()` and retry after a few minutes.

**Missing fields.** Many fields on detail pages can be `None` or an empty string when MAL has not filled them in. Guard against `None` before you use numeric fields such as `score`, `episodes`, and `ranked`.

**Pagination.** Search and top-list endpoints return one page at a time. Pass `page=2`, `page=3`, and so on to get more results. User lists paginate automatically through `iter_user_anime_list`.

---
[Home](../README.md) · [Anime endpoints →](anime.md)
