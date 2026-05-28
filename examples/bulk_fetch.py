import pymal

ids = [1, 5, 6, 19, 20, 30, 199, 269, 1735, 2025, 9253, 11061]
pymal.set_delay(2.0)

results = []
for i, mid in enumerate(ids, 1):
    print(f"[{i}/{len(ids)}] Fetching {mid}...", end=" ", flush=True)
    anime = pymal.get_anime(mid)
    results.append(anime)
    print(f"{anime.title}")

print()
print(f"Done. Fetched {len(results)} anime.")
print()
print(f"{'Title':<45} {'Score':<7} {'Type'}")
print("-" * 65)
for anime in results:
    score = str(anime.score) if anime.score else "N/A"
    print(f"{anime.title:<45} {score:<7} {anime.type}")
