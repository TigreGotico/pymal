import pymal
from collections import defaultdict

cards = pymal.seasonal_anime(2025, "spring")
print(f"Spring 2025: {len(cards)} titles")

by_type = defaultdict(list)
for card in cards:
    by_type[card.type or "Unknown"].append(card)

for type_label in ("TV", "ONA", "Movie", "OVA", "Special", "Unknown"):
    group = by_type.get(type_label, [])
    if not group:
        continue
    sorted_group = sorted(group, key=lambda c: c.score or 0.0, reverse=True)
    print(f"\n=== {type_label} ({len(sorted_group)}) ===")
    print(f"{'Title':<45} {'Score':<7} {'Episodes'}")
    print("-" * 65)
    for card in sorted_group[:10]:
        score = str(card.score) if card.score else "N/A"
        eps = str(card.episodes) if card.episodes else "?"
        print(f"{card.title:<45} {score:<7} {eps}")
