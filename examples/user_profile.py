import pymal

profile = pymal.get_user_profile("Xinil")

print(f"Username:     {profile.username}")
print(f"URL:          {profile.url}")
print(f"Joined:       {profile.joined}")
print(f"Last online:  {profile.last_online}")
print(f"Gender:       {profile.gender or '—'}")
print(f"Birthday:     {profile.birthday or '—'}")
print(f"Location:     {profile.location or '—'}")
print(f"Website:      {profile.website or '—'}")
print()

a = profile.anime_stats
print("=== Anime Stats ===")
print(f"  Watching:       {a.watching}")
print(f"  Completed:      {a.completed}")
print(f"  On Hold:        {a.on_hold}")
print(f"  Dropped:        {a.dropped}")
print(f"  Plan to Watch:  {a.plan_to_watch}")
print(f"  Total:          {a.total_entries}")
print(f"  Days Watched:   {a.days_watched}")
print(f"  Mean Score:     {a.mean_score}")
print()

m = profile.manga_stats
print("=== Manga Stats ===")
print(f"  Reading:        {m.reading}")
print(f"  Completed:      {m.completed}")
print(f"  On Hold:        {m.on_hold}")
print(f"  Dropped:        {m.dropped}")
print(f"  Plan to Read:   {m.plan_to_read}")
print(f"  Total:          {m.total_entries}")
print(f"  Days Read:      {m.days_read}")
print(f"  Mean Score:     {m.mean_score}")
print()

fav = profile.favorites
print("=== Favorite Anime ===")
for f in fav.anime:
    print(f"  [{f.mal_id}] {f.title}")

print()
print("=== Favorite Manga ===")
for f in fav.manga:
    print(f"  [{f.mal_id}] {f.title}")

print()
print("=== Favorite Characters ===")
for f in fav.characters:
    print(f"  [{f.mal_id}] {f.name}")

print()
print("=== Favorite People ===")
for f in fav.people:
    print(f"  [{f.mal_id}] {f.name}")
