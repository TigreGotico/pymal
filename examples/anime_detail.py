import pymal

anime = pymal.get_anime(1)

print(f"Title:          {anime.title}")
print(f"English:        {anime.english_title}")
print(f"Japanese:       {anime.japanese_title}")
print(f"Type:           {anime.type}")
print(f"Episodes:       {anime.episodes}")
print(f"Status:         {anime.status}")
print(f"Aired:          {anime.aired_from} to {anime.aired_to}")
print(f"Season:         {anime.season}")
print(f"Broadcast:      {anime.broadcast}")
print(f"Studios:        {', '.join(anime.studios)}")
print(f"Producers:      {', '.join(anime.producers)}")
print(f"Source:         {anime.source}")
print(f"Genres:         {', '.join(anime.genres)}")
print(f"Themes:         {', '.join(anime.themes)}")
print(f"Duration:       {anime.duration}")
print(f"Rating:         {anime.rating}")
print(f"Score:          {anime.score}  (scored by {anime.scored_by})")
print(f"Ranked:         #{anime.ranked}")
print(f"Popularity:     #{anime.popularity}")
print(f"Members:        {anime.members}")
print(f"Favorites:      {anime.favorites}")
print(f"Trailer:        {anime.trailer_url}")
print()
print("Synopsis:")
print(anime.synopsis[:400])
print()

print("=== Characters (first 5) ===")
for char in anime.characters[:5]:
    va = char.voice_actor_name or "—"
    print(f"  {char.name:<30} {char.role:<12}  VA: {va}")

print()
print("=== Staff (first 5) ===")
for s in anime.staff[:5]:
    print(f"  {s.name:<30} {s.role}")

print()
print("=== Related entries ===")
for rel_type, entries in anime.related.items():
    for e in entries:
        print(f"  {rel_type:<20} {e.title} [{e.entry_type}]")

print()
print("=== Opening themes ===")
for t in anime.opening_themes:
    print(f"  {t}")

print()
print("=== Ending themes ===")
for t in anime.ending_themes:
    print(f"  {t}")
