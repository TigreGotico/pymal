import pymal

results = pymal.search_people("Hayao Miyazaki")

print(f"People search for 'Hayao Miyazaki': {len(results)} found")
for card in results[:5]:
    print(f"  [{card.mal_id}] {card.name}")

print()
person = results[0].get()
print(f"Name:     {person.name}")
print(f"Japanese: {person.japanese_name}")
print(f"Birthday: {person.birthday}")
print(f"About:    {person.about[:200]}")
print()

print("Voice acting roles (first 5):")
for role in person.va_roles[:5]:
    print(f"  {role.character_name:<30} in {role.anime_title} ({role.role})")

print()
print("Staff roles (first 5):")
for role in person.staff_roles[:5]:
    print(f"  {role.role:<25} on {role.anime_title}")
