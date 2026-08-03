# pymal

pymal is a Python client for [myanimelist.net](https://myanimelist.net) (MAL). It scrapes public HTML pages and the undocumented list JSON endpoints. It needs no API key.

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

See [docs/quickstart.md](docs/quickstart.md) for a longer walkthrough and common gotchas.

## Rate limiting

MAL blocks scrapers that send too many requests. The default delay between requests is **1.5 seconds**.

```python
pymal.set_delay(2.0)   # increase if you get 429 responses
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

## Documentation

- [Quickstart](docs/quickstart.md)
- [Anime endpoints](docs/anime.md)
- [Manga endpoints](docs/manga.md)
- [Characters and people endpoints](docs/characters_people.md)
- [User endpoints](docs/user.md)
- [Data models](docs/models.md)
- [Transport and HTTP configuration](docs/transport.md)
- [ARM cross-reference](docs/arm.md)
- [Recipes](docs/recipes.md)

## Related projects

- [LeMetadatarr/pyimdb](https://github.com/LeMetadatarr/pyimdb): client for IMDb, in the same `clients/video` group.
- [LeMetadatarr/tutubo](https://github.com/LeMetadatarr/tutubo): client for YouTube, built on the same transport pattern.

## License

Apache-2.0.
