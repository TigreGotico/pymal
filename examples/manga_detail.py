import pymal

manga = pymal.get_manga(2)

print(f"Title:          {manga.title}")
print(f"English:        {manga.english_title}")
print(f"Japanese:       {manga.japanese_title}")
print(f"Type:           {manga.type}")
print(f"Volumes:        {manga.volumes}")
print(f"Chapters:       {manga.chapters}")
print(f"Status:         {manga.status}")
print(f"Published:      {manga.published_from} to {manga.published_to}")
print(f"Genres:         {', '.join(manga.genres)}")
print(f"Themes:         {', '.join(manga.themes)}")
print(f"Demographics:   {', '.join(manga.demographics)}")
print(f"Score:          {manga.score}  (scored by {manga.scored_by})")
print(f"Ranked:         #{manga.ranked}")
print(f"Popularity:     #{manga.popularity}")
print(f"Members:        {manga.members}")
print(f"Favorites:      {manga.favorites}")
print(f"Serialization:  {', '.join(manga.serialization)}")
print()

print("=== Authors ===")
for a in manga.authors:
    print(f"  {a.name:<30} {a.role}")

print()
print("=== Related entries ===")
for rel_type, entries in manga.related.items():
    for e in entries:
        print(f"  {rel_type:<20} {e.title} [{e.entry_type}]")

print()
print("Synopsis:")
print(manga.synopsis[:400])
