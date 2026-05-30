"""Scrape the complete MyAnimeList anime database into a resumable .jsonl dataset.

Two-phase approach
------------------
Phase 1  ID discovery
    Iterates every letter page on /anime.php?letter=X&show=N (50 per page).
    Letters: 0 (numbers / symbols), A–Z.
    Each discovered (mal_id, title) is appended to --ids-file.
    Progress is saved after every page so Ctrl+C is safe.

Phase 2  Detail fetch
    For every ID in --ids-file that is not already in --out, fetches:
      card     — data from the browse page only (already present after phase 1)
      full     — parse_anime_page() — 1 HTTP request, all sidebar fields, no characters
      complete — full + /characters page — 2 HTTP requests, characters+staff included

    Progress is tracked by which IDs are already written to --out; re-running
    resumes automatically.

Estimated time
--------------
    ~30,000 anime total (varies as MAL grows)
    full     mode:  1 req × delay   ≈  12–15 h at 1.5 s/req
    complete mode:  2 req × delay   ≈  25–30 h at 1.5 s/req
    card     mode:  phase-1 only    ≈  30–40 min

Usage examples
--------------
    # Full run (default: full detail, 1 req/anime)
    python scrape_full_database.py

    # Complete run with characters + staff (2 req/anime)
    python scrape_full_database.py --detail complete

    # Cards only — instant after phase 1
    python scrape_full_database.py --detail card

    # Resume — just run the same command again

    # Only phase 1 (collect IDs, skip detail fetch)
    python scrape_full_database.py --phase discovery

    # Only phase 2 (assumes IDs already collected)
    python scrape_full_database.py --phase fetch

    # Faster (be polite — MAL will rate-limit below ~0.8 s)
    python scrape_full_database.py --delay 1.0

Output files
------------
    mal_anime_ids.jsonl          one {"mal_id": N, "title": "...", "type": "...",
                                      "episodes": N, "score": F} per line
    mal_anime_full.jsonl         one full Anime record per line (same schema as
                                 hentai_full.jsonl from build_hf_dataset.py)
    mal_anime_ids.progress       JSON sidecar — last completed (letter, show offset)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Iterator, Optional

import pymal
from pymal._parse import _parse_search_table
from pymal.transport import BASE_URL, get_html

# ── letters to iterate ────────────────────────────────────────────────────────
_LETTERS = ["0"] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]


# ── schema (reused from build_hf_dataset) ────────────────────────────────────

def _int(v, default=-1):
    if v is None: return default
    try: return int(v)
    except: return default

def _float(v, default=0.0):
    if v is None: return default
    try:
        f = float(v)
        return f if f > 0 else default
    except: return default

def _str(v): return str(v).strip() if v else ""
def _list(v): return [str(x) for x in v if x] if isinstance(v, list) else []


def card_to_row(card: dict) -> dict:
    return {
        "mal_id":         _int(card.get("mal_id")),
        "title":          _str(card.get("title")),
        "title_english":  "", "title_japanese": "", "synonyms": [],
        "type":           _str(card.get("type")),
        "episodes":       _int(card.get("episodes")),
        "status":         _str(card.get("status")),
        "source":         "", "duration": "", "rating": "",
        "aired_from":     "", "aired_to": "", "season": "", "year": -1,
        "score":          _float(card.get("score")),
        "scored_by":      -1, "ranked": -1, "popularity": -1,
        "members":        _int(card.get("members"), 0),
        "favorites":      -1,
        "genres":         _list(card.get("genres")),
        "themes":         [], "demographics": [],
        "studios":        _list(card.get("studios")),
        "producers":      [], "licensors": [],
        "synopsis":       _str(card.get("synopsis")),
        "background":     "",
        "url":            _str(card.get("url")),
        "image_url":      _str(card.get("image_url")),
        "trailer_url":    "", "opening_themes": [], "ending_themes": [],
        "data_source":    "card",
    }


def anime_to_row(anime) -> dict:
    return {
        "mal_id":         anime.mal_id,
        "title":          _str(anime.title),
        "title_english":  _str(anime.english_title),
        "title_japanese": _str(anime.japanese_title),
        "synonyms":       _list(anime.synonyms),
        "type":           _str(anime.type),
        "episodes":       _int(anime.episodes),
        "status":         _str(anime.status),
        "source":         _str(anime.source),
        "duration":       _str(anime.duration),
        "rating":         _str(anime.rating),
        "aired_from":     _str(anime.aired_from),
        "aired_to":       _str(anime.aired_to),
        "season":         _str(anime.season),
        "year":           _int(anime.year),
        "score":          _float(anime.score),
        "scored_by":      _int(anime.scored_by),
        "ranked":         _int(anime.ranked),
        "popularity":     _int(anime.popularity),
        "members":        _int(anime.members, 0),
        "favorites":      _int(anime.favorites),
        "genres":         _list(anime.genres),
        "themes":         _list(anime.themes),
        "demographics":   _list(anime.demographics),
        "studios":        _list(anime.studios),
        "producers":      _list(anime.producers),
        "licensors":      _list(anime.licensors),
        "synopsis":       _str(anime.synopsis),
        "background":     _str(anime.background),
        "url":            _str(anime.url),
        "image_url":      _str(anime.image_url),
        "trailer_url":    _str(anime.trailer_url),
        "opening_themes": _list(anime.opening_themes),
        "ending_themes":  _list(anime.ending_themes),
        "data_source":    "full",
    }


def anime_to_row_complete(anime) -> dict:
    row = anime_to_row(anime)
    row["data_source"] = "complete"
    row["characters"] = [
        {"mal_id": c.mal_id, "name": c.name, "role": c.role,
         "va_name": c.voice_actor_name, "va_mal_id": _va_id(c.va_url)}
        for c in anime.characters
    ]
    row["staff"] = [
        {"mal_id": s.mal_id, "name": s.name, "role": s.role}
        for s in anime.staff
    ]
    return row


def _va_id(va_url: str) -> Optional[int]:
    m = re.search(r"/people/(\d+)/", va_url or "")
    return int(m.group(1)) if m else None


# ── IO helpers ────────────────────────────────────────────────────────────────

def _append(path: str, obj: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _load_ids(path: str) -> dict:
    """Return {mal_id: dict} from a ids jsonl."""
    out: dict = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                mid = obj.get("mal_id")
                if mid: out[int(mid)] = obj
            except json.JSONDecodeError:
                pass
    return out


def _load_done_ids(path: str) -> set:
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                mid = obj.get("mal_id")
                if mid: done.add(int(mid))
            except json.JSONDecodeError:
                pass
    return done


def _load_progress(progress_path: str) -> dict:
    if not os.path.exists(progress_path):
        return {"letter": "0", "show": 0}
    try:
        with open(progress_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {"letter": "0", "show": 0}


def _save_progress(progress_path: str, letter: str, show: int) -> None:
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump({"letter": letter, "show": show}, f)


# ── Phase 1: ID discovery ─────────────────────────────────────────────────────

def _letter_pages(letter: str, start_show: int = 0) -> Iterator[tuple[int, list]]:
    """Yield (show_offset, list_of_cards) for every page of a letter."""
    show = start_show
    while True:
        url = f"{BASE_URL}/anime.php?letter={letter}&show={show}"
        try:
            html = get_html(url)
        except Exception as exc:
            # 404 means we've gone past the last page
            if "404" in str(exc):
                return
            raise
        cards = _parse_search_table(html, "anime")
        if not cards:
            return
        yield show, cards
        if len(cards) < 50:
            return
        show += 50


def run_discovery(ids_file: str, progress_path: str) -> None:
    existing = _load_ids(ids_file)
    prog = _load_progress(progress_path)
    start_letter = prog["letter"]
    start_show = prog["show"]

    letters_to_do = _LETTERS[_LETTERS.index(start_letter):]
    total_new = 0

    print(f"Phase 1 — ID discovery")
    print(f"  IDs file:  {ids_file}  ({len(existing)} already collected)")
    print(f"  Resuming:  letter={start_letter} show={start_show}")
    print()

    try:
        for letter in letters_to_do:
            s0 = start_show if letter == start_letter else 0
            letter_new = 0
            for show, cards in _letter_pages(letter, s0):
                for card in cards:
                    mid = card.get("mal_id")
                    if not mid or int(mid) in existing:
                        continue
                    existing[int(mid)] = card
                    _append(ids_file, {"mal_id": int(mid), "title": card.get("title",""),
                                       "type": card.get("type",""), "episodes": card.get("episodes"),
                                       "score": card.get("score"), "image_url": card.get("image_url",""),
                                       "url": card.get("url","")})
                    letter_new += 1
                    total_new += 1
                _save_progress(progress_path, letter, show)
                print(f"  letter={letter} show={show:4d}  +{len(cards)} ids  (letter total: {letter_new}  grand: {len(existing)})")

            print(f"  ✓ letter={letter}: {letter_new} new IDs")

    except KeyboardInterrupt:
        print(f"\nInterrupted. Progress saved. Re-run to continue.")
        sys.exit(0)

    print(f"\nDiscovery complete — {len(existing)} total IDs in {ids_file}")
    # remove progress sidecar when fully done
    if os.path.exists(progress_path):
        os.remove(progress_path)


# ── Phase 2: Detail fetch ─────────────────────────────────────────────────────

def _fetch_full(mal_id: int) -> Optional[dict]:
    """1 request — main detail page only (no characters)."""
    from pymal._parse import parse_anime_page, parse_related_entries, _parse_theme_songs
    from pymal.models import RelatedEntry
    html = get_html(f"{BASE_URL}/anime/{mal_id}")
    data = parse_anime_page(html, mal_id)
    # build a minimal Anime-like object using a namespace so anime_to_row() works
    class _A:
        pass
    a = _A()
    a.mal_id = data["mal_id"]
    a.title = data["title"]
    a.english_title = data["english_title"]
    a.japanese_title = data["japanese_title"]
    a.synonyms = data["synonyms"]
    a.type = data["type"]
    a.episodes = data["episodes"]
    a.status = data["status"]
    a.source = data["source"]
    a.duration = data["duration"]
    a.rating = data["rating"]
    a.aired_from = data["aired_from"]
    a.aired_to = data["aired_to"]
    a.season = data["season"]
    a.year = data["year"]
    a.broadcast = data["broadcast"]
    a.producers = data["producers"]
    a.licensors = data["licensors"]
    a.studios = data["studios"]
    a.genres = data["genres"]
    a.themes = data["themes"]
    a.demographics = data["demographics"]
    a.score = data["score"]
    a.scored_by = data["scored_by"]
    a.ranked = data["ranked"]
    a.popularity = data["popularity"]
    a.members = data["members"]
    a.favorites = data["favorites"]
    a.synopsis = data["synopsis"]
    a.background = data["background"]
    a.url = data["url"]
    a.image_url = data["image_url"]
    a.trailer_url = data["trailer_url"]
    a.opening_themes = data["opening_themes"]
    a.ending_themes = data["ending_themes"]
    a.characters = []
    a.staff = []
    return anime_to_row(a)


def run_fetch(ids_file: str, out_file: str, detail: str) -> None:
    all_ids = _load_ids(ids_file)
    done = _load_done_ids(out_file)
    remaining = [mid for mid in sorted(all_ids) if mid not in done]

    print(f"Phase 2 — Detail fetch  (detail={detail})")
    print(f"  IDs total:  {len(all_ids)}")
    print(f"  Done:       {len(done)}")
    print(f"  Remaining:  {len(remaining)}")
    print(f"  Output:     {out_file}")
    print()

    errors = 0
    written = 0

    try:
        for i, mid in enumerate(remaining, 1):
            card = all_ids[mid]
            title_hint = card.get("title", "")[:45]
            prefix = f"[{i}/{len(remaining)}] ID {mid}"
            print(f"  {prefix} {title_hint} ...", end=" ", flush=True)

            try:
                if detail == "card":
                    row = card_to_row(card)
                    row["mal_id"] = mid
                elif detail == "complete":
                    anime = pymal.get_anime(mid)
                    row = anime_to_row_complete(anime)
                else:  # full (default)
                    row = _fetch_full(mid)

                _append(out_file, row)
                written += 1
                score_str = f"score={row['score']:.2f}" if row.get("score") else "unscored"
                print(f"OK  ({score_str}, {len(row.get('synopsis',''))} chars)")

            except KeyboardInterrupt:
                raise
            except Exception as exc:
                errors += 1
                # fall back to card-level data so the ID is recorded
                row = card_to_row(card)
                row["mal_id"] = mid
                _append(out_file, row)
                print(f"WARN fallback→card: {exc}")

    except KeyboardInterrupt:
        print(f"\nInterrupted at ID {mid}. Re-run to continue.")
        sys.exit(0)

    print(f"\nFetch complete: {written} written, {errors} errors/fallbacks")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase",  choices=["all", "discovery", "fetch"], default="all",
                    help="Which phase(s) to run (default: all)")
    ap.add_argument("--detail", choices=["card", "full", "complete"], default="full",
                    help="card=browse data only | full=detail page (1 req) | "
                         "complete=full+characters (2 req)  [default: full]")
    ap.add_argument("--ids-file",  default="mal_anime_ids.jsonl",
                    help="JSONL file to store discovered IDs (default: mal_anime_ids.jsonl)")
    ap.add_argument("--out",       default="mal_anime_full.jsonl",
                    help="Output JSONL for full records (default: mal_anime_full.jsonl)")
    ap.add_argument("--delay", type=float, default=1.5,
                    help="Seconds between requests (default: 1.5)")
    args = ap.parse_args()

    progress_path = args.ids_file + ".progress"
    pymal.set_delay(args.delay)

    print(f"MAL Full Database Scraper")
    print(f"  phase={args.phase}  detail={args.detail}  delay={args.delay}s")
    print()

    if args.phase in ("all", "discovery"):
        run_discovery(args.ids_file, progress_path)

    if args.phase in ("all", "fetch"):
        if args.detail == "card" and args.phase == "all":
            # card mode: write cards directly from the ids file, no extra requests
            pass
        run_fetch(args.ids_file, args.out, args.detail)

    total = sum(1 for _ in open(args.out, encoding="utf-8")) if os.path.exists(args.out) else 0
    print(f"\nDone. {total} records in {args.out}")


if __name__ == "__main__":
    main()
