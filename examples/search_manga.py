import pymal

results = pymal.search_manga("one piece")

print(f"Search results for 'one piece': {len(results)} found")
print()
header = f"{'ID':<8} {'Title':<40} {'Type':<10} {'Score':<7} {'Volumes':<9} {'Chapters'}"
print(header)
print("-" * len(header))
for card in results[:5]:
    score = str(card.score) if card.score else "N/A"
    vols = str(card.volumes) if card.volumes else "?"
    chs = str(card.chapters) if card.chapters else "?"
    print(f"{card.mal_id:<8} {card.title:<40} {card.type:<10} {score:<7} {vols:<9} {chs}")

print()
print("=== Full detail for first result ===")
manga = results[0].get()
print(f"Title:      {manga.title}")
print(f"Authors:    {', '.join(f'{a.name} ({a.role})' for a in manga.authors)}")
print(f"Status:     {manga.status}")
print(f"Genres:     {', '.join(manga.genres)}")
print(f"Synopsis:   {manga.synopsis[:300]}")
