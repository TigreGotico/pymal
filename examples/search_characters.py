import pymal

results = pymal.search_characters("Naruto")

print(f"Character search for 'Naruto': {len(results)} found")
print()
header = f"{'ID':<8} {'Name':<35} {'Favorites'}"
print(header)
print("-" * len(header))
for card in results[:5]:
    print(f"{card.mal_id:<8} {card.name:<35} {card.favorites}")

print()
print("=== Full detail for first result ===")
char = results[0].get()
print(f"Name:     {char.name}")
print(f"Japanese: {char.japanese_name}")
print(f"About:    {char.about[:200]}")
print()

print("Anime roles:")
for role in char.anime_roles[:5]:
    print(f"  {role.anime_title:<40} {role.role}")

print()
print("Voice actors:")
for va in char.voice_actors[:5]:
    print(f"  {va.name:<30} {va.language}")
