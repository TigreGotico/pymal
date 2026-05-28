import csv
import json
import pymal
from collections import Counter

username = "Xinil"
print(f"Fetching full anime list for {username}...")
entries = pymal.get_user_anime_list(username)

rows = [e.as_dict for e in entries]

json_file = f"{username}_animelist.json"
with open(json_file, "w") as f:
    json.dump(rows, f, indent=2)
print(f"Exported {len(rows)} entries to {json_file}")

csv_file = f"{username}_animelist.csv"
with open(csv_file, "w", newline="") as f:
    if rows:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
print(f"Exported {len(rows)} entries to {csv_file}")

status_counts = Counter(e.status_label for e in entries)
print()
print("Counts per status:")
for label, count in sorted(status_counts.items()):
    print(f"  {label:<20} {count}")
