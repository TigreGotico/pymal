# Anime Endpoints

## get_anime(mal_id)

Fetches the full detail page for a single anime.

```python
anime = pymal.get_anime(1)
```

Returns `Anime`. All fields are documented in [models.md](models.md).

The function fetches two pages: the main anime page and the characters+staff page. Expect two HTTP requests.

---

## get_anime_episodes(mal_id)

```python
episodes = pymal.get_anime_episodes(1)
for ep in episodes:
    print(ep.number, ep.title, ep.aired)
```

Returns `List[EpisodeEntry]`. Each entry has `number`, `title`, `japanese_title`, `aired`, `discussion_url`.

---

## get_anime_reviews(mal_id)

```python
reviews = pymal.get_anime_reviews(1)
for r in reviews:
    print(r.author, r.score, r.summary[:80])
```

Returns `List[ReviewCard]`. Fetches the first page of reviews (~20 entries).

---

## get_anime_recommendations(mal_id)

```python
recs = pymal.get_anime_recommendations(1)
for r in recs:
    print(r.title, r.num_recommendations)
```

Returns `List[RecommendationCard]`.

---

## search_anime(query, page, type, status, score)

```python
results = pymal.search_anime("cowboy bebop")
results = pymal.search_anime("action", page=2, type=1, status=2)
```

Returns `List[AnimeCard]`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | required | Search string |
| `page` | `int` | `1` | Page number |
| `type` | `int` | `0` | Format filter (see table below) |
| `status` | `int` | `0` | Status filter (see table below) |
| `score` | `int` | `0` | Minimum score filter (1–10, 0=any) |

**Type values:**

| Value | Meaning |
|-------|---------|
| `0` | Any |
| `1` | TV |
| `2` | OVA |
| `3` | Movie |
| `4` | Special |
| `5` | ONA |
| `6` | Music |

**Status values:**

| Value | Meaning |
|-------|---------|
| `0` | Any |
| `1` | Airing |
| `2` | Finished Airing |
| `3` | Not Yet Aired |

---

## top_anime(type, page)

```python
top = pymal.top_anime()
top_movies = pymal.top_anime(type="movie", page=1)
```

Returns `List[AnimeCard]`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | `str` | `"all"` | List type (see table below) |
| `page` | `int` | `1` | Page number (50 per page) |

**Type values:**

| Value | Meaning |
|-------|---------|
| `"all"` | All anime by score |
| `"airing"` | Currently airing by score |
| `"upcoming"` | Upcoming by popularity |
| `"tv"` | TV series only |
| `"movie"` | Movies only |
| `"ova"` | OVAs only |
| `"ona"` | ONAs only |
| `"special"` | Specials only |
| `"bypopularity"` | All by member count |
| `"favorite"` | All by favorites count |

---

## seasonal_anime(year, season)

```python
spring = pymal.seasonal_anime(2025, "spring")
for a in spring:
    print(a.title, a.type, a.score)
```

Returns `List[SeasonalAnimeCard]`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | `int` | Year, e.g. `2025` |
| `season` | `str` | `"winter"`, `"spring"`, `"summer"`, or `"fall"` |

---

## season_schedule()

```python
schedule = pymal.season_schedule()
for day, entries in schedule.items():
    print(day, [e.title for e in entries[:3]])
```

Returns `Dict[str, List[SeasonalAnimeCard]]` keyed by broadcast day (`"Monday"`, `"Tuesday"`, etc., plus `"Other"` for irregular schedules).

---

## anime_genre(genre_id, genre_name, page)

```python
action = pymal.anime_genre(1, "Action")
page2 = pymal.anime_genre(1, "Action", page=2)
```

Returns `List[AnimeCard]`. `genre_name` is used only in the URL construction and can be any slug string; the canonical slugs are listed below.

### Anime genre IDs

| ID | Genre | ID | Genre | ID | Genre |
|----|-------|----|-------|----|-------|
| 1 | Action | 2 | Adventure | 4 | Comedy |
| 5 | Avant Garde | 7 | Mystery | 8 | Drama |
| 9 | Ecchi | 10 | Fantasy | 11 | Game |
| 13 | Historical | 14 | Horror | 15 | Kids |
| 17 | Martial Arts | 18 | Mecha | 19 | Music |
| 20 | Parody | 21 | Samurai | 22 | Romance |
| 23 | School | 24 | Sci-Fi | 25 | Shoujo |
| 26 | Girls Love | 27 | Shounen | 28 | Boys Love |
| 29 | Space | 30 | Sports | 31 | Super Power |
| 32 | Vampire | 35 | Harem | 36 | Slice of Life |
| 37 | Supernatural | 38 | Military | 39 | Police |
| 40 | Psychological | 41 | Suspense | 42 | Seinen |
| 43 | Josei | 44 | Shoujo Ai (deprecated alias) | 45 | Shounen Ai (deprecated alias) |
| 46 | Erotica | 47 | Adult Cast | 48 | Anthropomorphic |
| 49 | CGDCT | 50 | Childcare | 51 | Combat Sports |
| 52 | Delinquents | 53 | Detective | 54 | Educational |
| 55 | Gag Humor | 56 | Gore | 57 | High Stakes Game |
| 58 | Idols (Female) | 59 | Idols (Male) | 60 | Isekai |
| 61 | Iyashikei | 62 | Love Polygon | 63 | Magical Sex Shift |
| 64 | Mahou Shoujo | 65 | Medical | 66 | Military (theme) |
| 67 | Mythology | 68 | Organized Crime | 69 | Otaku Culture |
| 70 | Performing Arts | 71 | Pets | 72 | Racing |
| 73 | Reincarnation | 74 | Reverse Harem | 75 | Romantic Subtext |
| 76 | Showbiz | 77 | Survival | 78 | Team Sports |
| 79 | Time Travel | 80 | Vampire (theme) | 81 | Video Game |
| 82 | Visual Arts | 83 | Workplace |
