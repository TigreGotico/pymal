"""Fetch a user's anime list and show watching + plan-to-watch counts."""
import sys
import pymal

username = sys.argv[1] if len(sys.argv) > 1 else "Xinil"

profile = pymal.get_user_profile(username)
print(f"User: {profile.username}")
print(f"Joined: {profile.joined}")
print(f"Anime — Watching: {profile.anime_stats.watching}, Completed: {profile.anime_stats.completed}")
print(f"Manga — Reading: {profile.manga_stats.reading}, Completed: {profile.manga_stats.completed}")

print(f"\nFetching anime list (all statuses)...")
entries = pymal.get_user_anime_list(username, status=7)
print(f"Total entries returned: {len(entries)}")
for entry in entries[:5]:
    score = entry.score or "-"
    print(f"  [{entry.mal_id}] {entry.title} | {entry.status_label} | Score: {score} | {entry.episodes_watched}/{entry.total_episodes or '?'} eps")
