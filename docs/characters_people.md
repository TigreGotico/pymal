# Characters and People Endpoints

## get_character(mal_id)

```python
char = pymal.get_character(1)
print(char.name, char.japanese_name)
print(char.about[:200])
for role in char.anime_roles:
    print(f"  {role.anime_title}: {role.role}")
for va in char.voice_actors:
    print(f"  {va.name} ({va.language})")
```

Returns `Character`.

| Field | Description |
|-------|-------------|
| `mal_id` | MAL character ID |
| `name` | Character name |
| `url` | Character page URL |
| `japanese_name` | Japanese name |
| `about` | Character description, up to 2000 characters |
| `image_url` | Character image URL |
| `anime_roles` | `List[CharacterAnimeRole]` : anime appearances |
| `manga_roles` | `List[CharacterMangaRole]` : manga appearances |
| `voice_actors` | `List[VoiceActorEntry]` : VAs in all languages |

Each `CharacterAnimeRole` has: `anime_title`, `anime_url`, `image_url`, `role` (`"Main"` or `"Supporting"`).

Each `CharacterMangaRole` has: `manga_title`, `manga_url`, `image_url`, `role`.

Each `VoiceActorEntry` has: `name`, `url`, `image_url`, `language`.

---

## get_person(mal_id)

```python
person = pymal.get_person(1)
print(person.name)
for role in person.va_roles[:5]:
    print(f"  VA: {role.character_name} in {role.anime_title} ({role.role})")
for role in person.staff_roles[:5]:
    print(f"  Staff: {role.role} on {role.anime_title}")
```

Returns `Person`.

| Field | Description |
|-------|-------------|
| `mal_id` | MAL person ID |
| `name` | Person name |
| `url` | Profile URL |
| `japanese_name` | Japanese name |
| `birthday` | Birthday string, empty if private |
| `hometown` | Hometown |
| `about` | Biography, up to 2000 characters |
| `image_url` | Photo URL |
| `va_roles` | `List[VARole]` : voice acting credits |
| `staff_roles` | `List[StaffAnimeRole]` : anime staff credits |

**VARole vs StaffAnimeRole.** `va_roles` lists characters the person voiced, each linked to an anime. `staff_roles` lists production credits (Director, Sound Director, etc.).

Each `VARole` has: `character_name`, `character_url`, `anime_title`, `anime_url`, `role`.

Each `StaffAnimeRole` has: `anime_title`, `anime_url`, `role`.

---

## search_characters(query)

```python
results = pymal.search_characters("naruto")
for card in results[:5]:
    print(card.mal_id, card.name, card.favorites)
```

Returns `List[CharacterCard]`. Call `.get()` on any card to fetch the full `Character`.

---

## search_people(query)

```python
results = pymal.search_people("Hayao Miyazaki")
for card in results[:5]:
    print(card.mal_id, card.name)
person = results[0].get()
```

Returns `List[PersonCard]`. Call `.get()` on any card to fetch the full `Person`.

---
[← Manga endpoints](manga.md) · [Home](../README.md) · [User endpoints →](user.md)
