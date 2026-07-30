# Recipes

## Export a user's full anime watchlist to JSON and CSV

```python
import csv
import json
import pymal

username = "Xinil"
entries = pymal.get_user_anime_list(username)

rows = [e.as_dict for e in entries]
with open(f"{username}_animelist.json", "w") as f:
    json.dump(rows, f, indent=2)

with open(f"{username}_animelist.csv", "w", newline="") as f:
    if rows:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

print(f"Exported {len(rows)} entries")
```

---

## Cross-reference a user's list against top-250

```python
import pymal

username = "Xinil"
user_entries = pymal.get_user_anime_list(username)
watched_ids = {
    e.mal_id for e in user_entries
    if e.status in (1, 2)
}

top = pymal.top_anime()
for i, card in enumerate(top[:250], 1):
    if card.mal_id not in watched_ids:
        print(f"#{i:3d}  {card.title}  (score: {card.score})")
```

---

## Scrape all seasonal anime for a year

```python
import pymal

year = 2024
for season in ("winter", "spring", "summer", "fall"):
    entries = pymal.seasonal_anime(year, season)
    print(f"{year} {season}: {len(entries)} anime")
    for e in entries[:3]:
        print(f"  {e.title} [{e.type}] score={e.score}")
```

---

## Find all anime by a specific studio

The top and genre listing pages include studio names on `SeasonalAnimeCard`. To search by studio, go through the genre or top pages and filter them:

```python
import pymal

studio = "Madhouse"
found = []
for page in range(1, 6):
    cards = pymal.top_anime(page=page)
    if not cards:
        break
    for card in cards:
        anime = card.get()
        if studio in anime.studios:
            found.append(anime)
        pymal.set_delay(2.0)

for a in found:
    print(a.title, a.score)
```

---

## Map characters in a franchise

Given a starting anime, follow Sequel/Prequel relations to build the full franchise chain:

```python
import pymal

def build_chain(start_id):
    visited = set()
    chain = []
    queue = [start_id]
    while queue:
        mid = queue.pop(0)
        if mid in visited:
            continue
        visited.add(mid)
        anime = pymal.get_anime(mid)
        chain.append(anime)
        for rel_type in ("Prequel", "Sequel"):
            for entry in anime.related.get(rel_type, []):
                if entry.entry_type == "anime" and entry.mal_id not in visited:
                    queue.append(entry.mal_id)
    return chain

chain = build_chain(1)
for anime in chain:
    print(anime.title)
    for char in anime.characters[:5]:
        print(f"  {char.name} ({char.role})")
```

---

## Rate-limit aware bulk fetcher with progress counter

```python
import pymal

ids = [1, 5, 6, 19, 20, 30, 199, 269, 1735]
pymal.set_delay(2.0)

results = []
for i, mid in enumerate(ids, 1):
    print(f"[{i}/{len(ids)}] Fetching {mid}...", end=" ", flush=True)
    anime = pymal.get_anime(mid)
    results.append(anime)
    print(anime.title)

print(f"\nFetched {len(results)} anime")
```

---

## Persist and diff a user's anime list over time

```python
import json
import os
import pymal
from datetime import date

username = "Xinil"
today = date.today().isoformat()
filename = f"{username}_{today}.json"

entries = pymal.get_user_anime_list(username)
snapshot = {e.mal_id: e.as_dict for e in entries}

with open(filename, "w") as f:
    json.dump(snapshot, f, indent=2)

previous_files = sorted(
    f for f in os.listdir(".") if f.startswith(username) and f.endswith(".json") and f != filename
)

if previous_files:
    with open(previous_files[-1]) as f:
        previous = json.load(f)
    prev_ids = set(int(k) for k in previous)
    curr_ids = set(snapshot)
    added = curr_ids - prev_ids
    removed = prev_ids - curr_ids
    for mid in added:
        print(f"Added:   {snapshot[mid]['title']}")
    for mid in removed:
        print(f"Removed: {previous[str(mid)]['title']}")
```

---
[← Transport and HTTP configuration](transport.md) · [Home](../README.md)
