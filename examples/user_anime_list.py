import pymal

username = "Xinil"
entries = pymal.get_user_anime_list(username)

print(f"Anime list for {username}: {len(entries)} entries")
print()
print(f"{'Title':<45} {'Status':<15} {'Score':<7} {'Progress'}")
print("-" * 85)
for entry in entries[:20]:
    score = str(entry.score) if entry.score else "—"
    total = str(entry.total_episodes) if entry.total_episodes else "?"
    progress = f"{entry.episodes_watched}/{total}"
    print(f"{entry.title:<45} {entry.status_label:<15} {score:<7} {progress}")

completed = [e for e in entries if e.status == 2 and e.score]
if completed:
    avg = sum(e.score for e in completed) / len(completed)
    print(f"\nCompleted with score: {len(completed)} entries")
    print(f"Average score: {avg:.2f}")
