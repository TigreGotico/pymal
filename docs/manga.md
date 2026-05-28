# Manga Endpoints

## get_manga(mal_id)

```python
manga = pymal.get_manga(2)
print(manga.title, manga.score)
print("Authors:", [(a.name, a.role) for a in manga.authors])
```

Returns `Manga`. All fields are documented in [models.md](models.md).

---

## search_manga(query, page, type, status)

```python
results = pymal.search_manga("berserk")
results = pymal.search_manga("romance", page=2, type=1)
```

Returns `List[MangaCard]`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | required | Search string |
| `page` | `int` | `1` | Page number |
| `type` | `int` | `0` | Format filter |
| `status` | `int` | `0` | Status filter |

**Type values:**

| Value | Meaning |
|-------|---------|
| `0` | Any |
| `1` | Manga |
| `2` | Novel |
| `3` | One-shot |
| `4` | Doujinshi |
| `5` | Manhwa |
| `6` | Manhua |

**Status values:**

| Value | Meaning |
|-------|---------|
| `0` | Any |
| `1` | Publishing |
| `2` | Finished |
| `3` | Not Yet Published |

---

## top_manga(type, page)

```python
top = pymal.top_manga()
novels = pymal.top_manga(type="novel")
```

Returns `List[MangaCard]`.

**Type values:**

| Value | Meaning |
|-------|---------|
| `"all"` | All manga by score |
| `"manga"` | Standard manga only |
| `"novels"` | Light novels only |
| `"oneshots"` | One-shots only |
| `"doujin"` | Doujinshi only |
| `"manhwa"` | Manhwa only |
| `"manhua"` | Manhua only |
| `"bypopularity"` | By member count |
| `"favorite"` | By favorites count |

---

## manga_genre(genre_id, genre_name, page)

```python
action = pymal.manga_genre(1, "Action")
page2 = pymal.manga_genre(1, "Action", page=2)
```

Returns `List[MangaCard]`.

### Manga genre IDs

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
| 43 | Josei | 46 | Erotica | 47 | Adult Cast |
| 48 | Anthropomorphic | 49 | CGDCT | 50 | Childcare |
| 51 | Combat Sports | 52 | Delinquents | 53 | Detective |
| 54 | Educational | 55 | Gag Humor | 56 | Gore |
| 57 | High Stakes Game | 58 | Idols (Female) | 59 | Idols (Male) |
| 60 | Isekai | 61 | Iyashikei | 62 | Love Polygon |
| 64 | Mahou Shoujo | 65 | Medical | 67 | Mythology |
| 68 | Organized Crime | 69 | Otaku Culture | 70 | Performing Arts |
| 71 | Pets | 72 | Racing | 73 | Reincarnation |
| 74 | Reverse Harem | 75 | Romantic Subtext | 76 | Showbiz |
| 77 | Survival | 78 | Team Sports | 79 | Time Travel |
| 80 | Vampire (theme) | 81 | Video Game | 82 | Visual Arts |
| 83 | Workplace | | | | |
