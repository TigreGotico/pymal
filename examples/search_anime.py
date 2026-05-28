import pymal

results = pymal.search_anime("naruto")

print(f"Search results for 'naruto': {len(results)} found")
print()
header = f"{'ID':<8} {'Title':<45} {'Type':<8} {'Score':<7} {'Episodes'}"
print(header)
print("-" * len(header))
for card in results[:5]:
    score = str(card.score) if card.score else "N/A"
    eps = str(int(card.episodes)) if card.episodes else "?"
    print(f"{card.mal_id:<8} {card.title:<45} {card.type:<8} {score:<7} {eps}")

print()
print("=== Full detail for first result ===")
anime = results[0].get()
print(f"Title:    {anime.title}")
print(f"Studios:  {', '.join(anime.studios) or '—'}")
print(f"Genres:   {', '.join(anime.genres)}")
print(f"Synopsis: {anime.synopsis[:300]}")
