# Examples

All scripts require `pip install pymal`. Run from the repository root or any directory where pymal is installed.

| File | Description |
|------|-------------|
| `anime_detail.py` | Fetch Cowboy Bebop (ID 1), print every field, first 5 characters with VA, first 5 staff, related entries, OP/ED themes |
| `manga_detail.py` | Fetch Berserk (ID 2), print all fields including authors and serialization |
| `search_anime.py` | Search "attack on titan", show top 5 results as a table, fetch full detail of the first result |
| `search_manga.py` | Search "one piece", show top 5 results, fetch full detail of the first result |
| `search_characters.py` | Search "Naruto", show top 5 characters, fetch first character's full detail with roles and VAs |
| `search_people.py` | Search "Hayao Miyazaki", fetch full person detail, print VA roles and staff roles |
| `top_anime.py` | Print top 10 for all anime, airing, movies, and TV — formatted table with rank, title, score, members |
| `top_manga.py` | Print top 10 for all manga, manga-only, and novels |
| `seasonal_anime.py` | Fetch 2025 spring season, group by type (TV/Movie/ONA/OVA), print each group sorted by score |
| `season_schedule.py` | Fetch the weekly broadcast schedule, group by day |
| `user_profile.py` | Fetch profile for "Xinil", print all fields, anime/manga stats, and all favorite categories |
| `user_anime_list.py` | Fetch anime list for "Xinil", print first 20 entries with status and score, compute average score |
| `user_manga_list.py` | Same for manga list |
| `watchlist_exporter.py` | Fetch full anime list for "Xinil", export to JSON and CSV, show counts per status |
| `top250_gaps.py` | Compare a user's watched anime against the top 250 to find unseen entries |
| `franchise_map.py` | Starting from an anime ID, follow Sequel/Prequel/related links to map a full franchise |
| `bulk_fetch.py` | Fetch a list of anime IDs with rate-limit awareness and a progress counter |
| `genre_explorer.py` | Fetch first page of Action, Comedy, and Romance genres, print top 5 per genre |
| `build_hf_dataset.py` | Build a Hugging Face-ready anime dataset from a genre JSONL seed file |
| `scrape_hentai_jsonl.py` | Scrape all anime under a MAL genre to a resumable `.jsonl` dataset, card or full-detail mode |
| `arm_cross_reference.py` | Cross-reference a MAL anime ID to AniList, AniDB, IMDb, and TVDB via the ARM service |
