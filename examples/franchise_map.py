import pymal

def build_franchise_chain(start_id):
    visited = {}
    queue = [(start_id, None)]
    while queue:
        mid, came_from = queue.pop(0)
        if mid in visited:
            continue
        anime = pymal.get_anime(mid)
        visited[mid] = (anime, came_from)
        for rel_type in ("Prequel", "Sequel", "Side story", "Alternative version"):
            for entry in anime.related.get(rel_type, []):
                if entry.entry_type == "anime" and entry.mal_id not in visited:
                    queue.append((entry.mal_id, rel_type))
    return visited

start_id = 20  # Naruto
print(f"Building franchise map starting from MAL ID {start_id} (Naruto)...")
chain = build_franchise_chain(start_id)

print(f"\nFranchise: {len(chain)} entries")
print()
for mid, (anime, rel) in chain.items():
    rel_label = f"[{rel}]" if rel else "[START]"
    score = str(anime.score) if anime.score else "N/A"
    print(f"  {rel_label:<22} {anime.title:<40} score={score}")
