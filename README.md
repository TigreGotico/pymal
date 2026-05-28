# pymal

Python scraper / API client for [myanimelist.net](https://myanimelist.net).

Scrapes public HTML pages and the undocumented list JSON endpoints. No API key required.

## Install

```bash
pip install pymal
# Optional: curl-cffi for browser-impersonation stealth mode
pip install pymal[stealth]
```

## Quick start

```python
import pymal

# Search
results = pymal.search_anime("cowboy bebop")
anime = results[0].get()          # fetch full detail
print(anime.title, anime.score)

# Top lists
for card in pymal.top_anime(type="tv"):
    print(card.title)

# Seasonal
for card in pymal.seasonal_anime(2024, "spring"):
    print(card.title, card.type)

# User lists
for entry in pymal.iter_user_anime_list("Xinil"):
    print(entry.title, entry.status_label)
```

## Rate limiting

MAL blocks aggressive scrapers. The default delay between requests is **1.5 seconds**.

```python
pymal.set_delay(2.0)   # increase if getting 429s
```

## Covered endpoints

| Category | Functions |
|---|---|
| Anime | `get_anime`, `get_anime_episodes`, `get_anime_reviews`, `get_anime_recommendations` |
| Manga | `get_manga` |
| Character | `get_character` |
| People | `get_person` |
| Search | `search_anime`, `search_manga`, `search_characters`, `search_people` |
| Listings | `top_anime`, `top_manga`, `seasonal_anime`, `season_schedule`, `anime_genre`, `manga_genre` |
| User | `get_user_profile`, `get_user_anime_list`, `get_user_manga_list`, `iter_user_anime_list`, `iter_user_manga_list` |
