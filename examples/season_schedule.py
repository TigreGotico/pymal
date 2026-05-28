"""Fetch the upcoming season schedule and group by broadcast day."""
import pymal
from collections import defaultdict

cards = pymal.season_schedule()
print(f"Season schedule: {len(cards)} titles")

by_day = defaultdict(list)
for card in cards:
    # broadcast field on SeasonalAnimeCard is often empty on schedule page;
    # group all as a flat list sorted by score
    by_day["All"].append(card)

sorted_cards = sorted(cards, key=lambda c: c.score or 0.0, reverse=True)

print(f"\n{'Title':<50} {'Type':<8} {'Score':<7} {'Studios'}")
print("-" * 85)
for card in sorted_cards[:30]:
    score = str(card.score) if card.score else "N/A"
    studios = ", ".join(card.studios[:2]) or "—"
    print(f"{card.title:<50} {card.type:<8} {score:<7} {studios}")
