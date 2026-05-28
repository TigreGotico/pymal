"""Scrape all anime under a MAL genre to a resumable .jsonl dataset.

Usage:
    python scrape_hentai_jsonl.py                        # genre 12 (Hentai)
    python scrape_hentai_jsonl.py --genre 9 --name Ecchi
    python scrape_hentai_jsonl.py --out my_dataset.jsonl
    python scrape_hentai_jsonl.py --detail              # fetch full Anime objects (slow)
    python scrape_hentai_jsonl.py --delay 2.0           # seconds between requests

Resume: just run the same command again. Already-seen MAL IDs are skipped.
The progress sidecar ({output}.progress) tracks the last completed page so
the genre listing itself is also resumed page-by-page, not just by ID.

Output format (one JSON object per line):
  card mode  — AnimeCard.as_dict  (fast, no extra requests)
  detail mode — Anime.as_dict     (one extra request per title)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import pymal
from pymal.transport import BASE_URL, get_html
from pymal._parse import parse_last_page, parse_genre_page


def _load_seen(path: str) -> set:
    seen: set = set()
    if not os.path.exists(path):
        return seen
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                mid = obj.get("mal_id")
                if mid:
                    seen.add(int(mid))
            except json.JSONDecodeError:
                pass
    return seen


def _load_progress(progress_path: str) -> int:
    if not os.path.exists(progress_path):
        return 1
    try:
        with open(progress_path, encoding="utf-8") as fh:
            data = json.load(fh)
            return int(data.get("last_completed_page", 0)) + 1
    except (json.JSONDecodeError, ValueError):
        return 1


def _save_progress(progress_path: str, page: int) -> None:
    with open(progress_path, "w", encoding="utf-8") as fh:
        json.dump({"last_completed_page": page}, fh)


def _append_record(path: str, record: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _fetch_page(genre_id: int, genre_name: str, page: int):
    slug = f"{genre_id}/{genre_name}" if genre_name else str(genre_id)
    html = get_html(f"{BASE_URL}/anime/genre/{slug}?p=1&page={page}")
    last = parse_last_page(html)
    raw = parse_genre_page(html)
    return html, raw, last


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--genre", type=int, default=12, help="MAL genre ID (default: 12 = Hentai)")
    ap.add_argument("--name",  type=str, default="Hentai", help="Genre slug name for the URL (default: Hentai)")
    ap.add_argument("--out",   type=str, default="", help="Output .jsonl path (default: <genre_name>.jsonl)")
    ap.add_argument("--detail", action="store_true", help="Fetch full Anime detail (slow; one request per title)")
    ap.add_argument("--delay", type=float, default=1.5, help="Seconds between requests (default: 1.5)")
    args = ap.parse_args()

    out_path = args.out or f"{args.name.lower()}.jsonl"
    progress_path = out_path + ".progress"

    pymal.set_delay(args.delay)

    seen = _load_seen(out_path)
    start_page = _load_progress(progress_path)

    print(f"Genre: {args.name} (id={args.genre})")
    print(f"Output: {out_path}")
    print(f"Already seen: {len(seen)} titles")
    print(f"Resuming from page: {start_page}")
    print(f"Mode: {'full detail' if args.detail else 'card (fast)'}")
    print()

    page = start_page
    last_page = None
    total_written = 0

    try:
        while True:
            if last_page is not None and page > last_page:
                break

            print(f"  page {page}" + (f"/{last_page}" if last_page else "") + " ...", end=" ", flush=True)

            try:
                html, raw, discovered_last = _fetch_page(args.genre, args.name, page)
            except Exception as exc:
                print(f"ERROR: {exc}  (retrying in 10s)")
                time.sleep(10)
                continue

            if last_page is None:
                last_page = discovered_last

            new_on_page = 0
            for r in raw:
                mid = r["mal_id"]
                if not mid or mid in seen:
                    continue

                if args.detail:
                    try:
                        anime = pymal.get_anime(mid)
                        record = anime.as_dict
                    except Exception as exc:
                        print(f"\n    WARN: could not fetch detail for {mid}: {exc}")
                        record = r
                else:
                    record = r

                _append_record(out_path, record)
                seen.add(mid)
                new_on_page += 1
                total_written += 1

            _save_progress(progress_path, page)
            print(f"{new_on_page} new  (total written: {total_written})")

            if not raw:
                print("Empty page — stopping.")
                break

            page += 1

    except KeyboardInterrupt:
        print(f"\nInterrupted at page {page}. Progress saved. Re-run to continue.")
        sys.exit(0)

    print(f"\nDone. {total_written} new records written to {out_path}")
    if os.path.exists(progress_path):
        os.remove(progress_path)
    print("Progress file removed (scrape complete).")


if __name__ == "__main__":
    main()
