import pymal

def print_top(label, type_str):
    cards = pymal.top_manga(type=type_str, page=1)
    print(f"\n=== Top 10: {label} ===")
    print(f"{'Rank':<5} {'Title':<45} {'Score':<7} {'Members'}")
    print("-" * 75)
    for i, card in enumerate(cards[:10], 1):
        score = str(card.score) if card.score else "N/A"
        members = f"{card.members:,}" if card.members else "?"
        print(f"{i:<5} {card.title:<45} {score:<7} {members}")

print_top("All Manga", "all")
print_top("Manga only", "manga")
print_top("Novels", "novels")
