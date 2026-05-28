import pymal

genres = [
    (1, "Action"),
    (4, "Comedy"),
    (22, "Romance"),
]

for genre_id, genre_name in genres:
    cards = pymal.anime_genre(genre_id, genre_name, page=1)
    print(f"\n=== {genre_name} — top 5 ===")
    print(f"{'Title':<45} {'Score':<7} {'Type'}")
    print("-" * 60)
    for card in cards[:5]:
        score = str(card.score) if card.score else "N/A"
        print(f"{card.title:<45} {score:<7} {card.type}")
