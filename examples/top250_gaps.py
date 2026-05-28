import pymal

username = "Xinil"

print(f"Fetching anime list for {username}...")
user_entries = pymal.get_user_anime_list(username)
watched_ids = {e.mal_id for e in user_entries if e.status in (1, 2)}
print(f"  Watching or completed: {len(watched_ids)} entries")

print("Fetching top 250 anime (5 pages)...")
top = []
for page in range(1, 6):
    cards = pymal.top_anime(page=page)
    top.extend(cards)
    if len(cards) < 50:
        break

print()
print(f"Top-250 titles not watched by {username}:")
print(f"{'Rank':<5} {'Title':<45} {'Score'}")
print("-" * 60)
rank = 0
for card in top[:250]:
    rank += 1
    if card.mal_id not in watched_ids:
        score = str(card.score) if card.score else "N/A"
        print(f"{rank:<5} {card.title:<45} {score}")
