"""Build a Hugging Face-ready anime dataset from a genre JSONL seed file.

Schema design
-------------
Each row is one anime title. Columns are chosen for maximum utility across
NLP, recommendation, and metadata tasks:

  Canonical identity
    mal_id           int32    MAL unique integer ID
    title            str      canonical title (romaji or original script)
    title_english    str      English title (empty string if none)
    title_japanese   str      Japanese script title (empty if none)
    synonyms         list[str] alternative titles / aliases

  Catalog
    type             str      TV / OVA / ONA / Movie / Special / Music
    episodes         int32    episode count (-1 = unknown)
    status           str      Finished / Airing / Not Yet Aired
    source           str      Original / Manga / Light Novel / Game / etc.
    duration         str      raw duration string e.g. "24 min. per ep."
    rating           str      age rating e.g. "R+" or "Rx"

  Dates
    aired_from       str      ISO-ish start date as scraped e.g. "Apr 3, 1998"
    aired_to         str      end date (empty for ongoing)
    season           str      e.g. "spring 1998"
    year             int32    start year (-1 = unknown)

  Metrics (all -1 when absent so the column stays int32)
    score            float32  MAL weighted mean score (0.0 = unscored)
    scored_by        int32    number of voters
    ranked           int32    rank on top list (-1 = unranked)
    popularity       int32    popularity rank
    members          int32    list-member count
    favorites        int32    favorites count

  Classification
    genres           list[str]  e.g. ["Hentai", "Fantasy"]
    themes           list[str]  e.g. ["Gore", "Psychological"]
    demographics     list[str]  e.g. ["Seinen"]

  Industry
    studios          list[str]  animation studios
    producers        list[str]  production companies
    licensors        list[str]  regional licensors

  Content
    synopsis         str      full synopsis text (empty if none)
    background       str      background notes (often empty)

  Media
    url              str      canonical MAL page URL
    image_url        str      cover art URL
    trailer_url      str      YouTube trailer URL (empty if none)

  Music
    opening_themes   list[str]  formatted as '"Title" by Artist (eps N-M)'
    ending_themes    list[str]

Resumability
------------
Progress is tracked in ``{output}.progress`` as JSON:
  {"done": [<mal_id>, ...]}
On restart, already-completed IDs are skipped. The progress file is removed
when all rows complete successfully.

Usage
-----
  # Fetch full detail for all IDs in hentai.jsonl
  python build_hf_dataset.py

  # Use a different seed file and output
  python build_hf_dataset.py --seed ecchi.jsonl --out ecchi_full.jsonl

  # Push to Hugging Face Hub after building
  python build_hf_dataset.py --push --repo your-username/mal-hentai

  # Skip full-detail fetching (use card data only, instant)
  python build_hf_dataset.py --card-only

  # Tune rate limit
  python build_hf_dataset.py --delay 2.0
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict

import pymal


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def _int(v: Any, default: int = -1) -> int:
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _float(v: Any, default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        f = float(v)
        return f if f > 0 else default
    except (TypeError, ValueError):
        return default


def _str(v: Any) -> str:
    return str(v).strip() if v else ""


def _list(v: Any) -> list:
    if isinstance(v, list):
        return [str(x) for x in v if x]
    return []


def card_to_row(card: dict) -> Dict[str, Any]:
    """Convert a scraped AnimeCard dict (from genre JSONL) to a dataset row.
    Used when --card-only is set or when full-detail fetch fails.
    """
    return {
        "mal_id":          _int(card.get("mal_id")),
        "title":           _str(card.get("title")),
        "title_english":   "",
        "title_japanese":  "",
        "synonyms":        [],
        "type":            _str(card.get("type")),
        "episodes":        _int(card.get("episodes")),
        "status":          _str(card.get("status")),
        "source":          "",
        "duration":        "",
        "rating":          "",
        "aired_from":      "",
        "aired_to":        "",
        "season":          _str(card.get("season")),
        "year":            -1,
        "score":           _float(card.get("score")),
        "scored_by":       -1,
        "ranked":          -1,
        "popularity":      -1,
        "members":         _int(card.get("members"), 0),
        "favorites":       -1,
        "genres":          _list(card.get("genres")),
        "themes":          [],
        "demographics":    [],
        "studios":         _list(card.get("studios")),
        "producers":       [],
        "licensors":       [],
        "synopsis":        _str(card.get("synopsis")),
        "background":      "",
        "url":             _str(card.get("url")),
        "image_url":       _str(card.get("image_url")),
        "trailer_url":     "",
        "opening_themes":  [],
        "ending_themes":   [],
        "data_source":     "card",   # flag so consumers know depth
    }


def anime_to_row(anime) -> Dict[str, Any]:
    """Convert a full pymal.Anime object to a dataset row."""
    return {
        "mal_id":          anime.mal_id,
        "title":           _str(anime.title),
        "title_english":   _str(anime.english_title),
        "title_japanese":  _str(anime.japanese_title),
        "synonyms":        _list(anime.synonyms),
        "type":            _str(anime.type),
        "episodes":        _int(anime.episodes),
        "status":          _str(anime.status),
        "source":          _str(anime.source),
        "duration":        _str(anime.duration),
        "rating":          _str(anime.rating),
        "aired_from":      _str(anime.aired_from),
        "aired_to":        _str(anime.aired_to),
        "season":          _str(anime.season),
        "year":            _int(anime.year),
        "score":           _float(anime.score),
        "scored_by":       _int(anime.scored_by),
        "ranked":          _int(anime.ranked),
        "popularity":      _int(anime.popularity),
        "members":         _int(anime.members, 0),
        "favorites":       _int(anime.favorites),
        "genres":          _list(anime.genres),
        "themes":          _list(anime.themes),
        "demographics":    _list(anime.demographics),
        "studios":         _list(anime.studios),
        "producers":       _list(anime.producers),
        "licensors":       _list(anime.licensors),
        "synopsis":        _str(anime.synopsis),
        "background":      _str(anime.background),
        "url":             _str(anime.url),
        "image_url":       _str(anime.image_url),
        "trailer_url":     _str(anime.trailer_url),
        "opening_themes":  _list(anime.opening_themes),
        "ending_themes":   _list(anime.ending_themes),
        "data_source":     "full",
    }


# ---------------------------------------------------------------------------
# Progress sidecar
# ---------------------------------------------------------------------------

def _load_progress(path: str) -> set:
    if not os.path.exists(path):
        return set()
    try:
        with open(path, encoding="utf-8") as fh:
            return set(json.load(fh).get("done", []))
    except (json.JSONDecodeError, ValueError):
        return set()


def _save_progress(path: str, done: set) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"done": sorted(done)}, fh)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _load_existing_ids(out_path: str) -> set:
    ids: set = set()
    if not os.path.exists(out_path):
        return ids
    with open(out_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("mal_id"):
                    ids.add(int(obj["mal_id"]))
            except json.JSONDecodeError:
                pass
    return ids


def _append_row(path: str, row: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# HF dataset conversion
# ---------------------------------------------------------------------------

def build_hf_dataset(jsonl_path: str, repo_id: str | None = None) -> None:
    """Convert the completed JSONL to a HuggingFace Dataset and optionally push."""
    from datasets import Dataset, Features, Value, Sequence
    import pandas as pd

    print(f"\nLoading {jsonl_path} into pandas...")
    rows = []
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    df = pd.DataFrame(rows)

    # Ensure correct dtypes
    for col in ("mal_id", "episodes", "scored_by", "ranked", "popularity", "members", "favorites", "year"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(-1).astype("int32")
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0.0).astype("float32")
    for col in ("title", "title_english", "title_japanese", "type", "status", "source",
                "duration", "rating", "aired_from", "aired_to", "season",
                "synopsis", "background", "url", "image_url", "trailer_url", "data_source"):
        df[col] = df[col].fillna("").astype(str)
    for col in ("synonyms", "genres", "themes", "demographics", "studios",
                "producers", "licensors", "opening_themes", "ending_themes"):
        df[col] = df[col].apply(lambda v: v if isinstance(v, list) else [])

    print(f"  {len(df)} rows, {len(df.columns)} columns")
    print(f"  Columns: {list(df.columns)}")

    ds = Dataset.from_pandas(df, preserve_index=False)
    print(f"  Dataset: {ds}")

    parquet_path = jsonl_path.replace(".jsonl", ".parquet")
    ds.to_parquet(parquet_path)
    print(f"  Saved parquet → {parquet_path}")

    if repo_id:
        print(f"\nPushing to HuggingFace Hub: {repo_id} ...")
        ds.push_to_hub(repo_id, private=True)
        print("  Done.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed",      default="hentai.jsonl",
                    help="Source JSONL with mal_id entries (default: hentai.jsonl)")
    ap.add_argument("--out",       default="",
                    help="Output JSONL path (default: <seed-stem>_full.jsonl)")
    ap.add_argument("--delay",     type=float, default=1.5,
                    help="Seconds between MAL requests (default: 1.5)")
    ap.add_argument("--card-only", action="store_true",
                    help="Write card-level data only, no full-detail requests")
    ap.add_argument("--push",      action="store_true",
                    help="Push the final dataset to HuggingFace Hub")
    ap.add_argument("--repo",      default="",
                    help="HuggingFace repo id, e.g. username/mal-hentai-dataset")
    ap.add_argument("--hf-only",   action="store_true",
                    help="Skip fetching; just convert existing --out JSONL to parquet/HF")
    args = ap.parse_args()

    seed_path = args.seed
    stem = os.path.splitext(os.path.basename(seed_path))[0]
    out_path = args.out or f"{stem}_full.jsonl"
    progress_path = out_path + ".progress"

    if args.hf_only:
        build_hf_dataset(out_path, repo_id=args.repo or None)
        return

    # --- Load seed IDs ---
    if not os.path.exists(seed_path):
        print(f"Seed file not found: {seed_path}")
        sys.exit(1)

    seed_rows: dict[int, dict] = {}
    with open(seed_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                mid = obj.get("mal_id")
                if mid:
                    seed_rows[int(mid)] = obj
            except json.JSONDecodeError:
                pass

    total = len(seed_rows)
    print(f"Seed: {seed_path} → {total} unique IDs")

    # --- Resume state ---
    done = _load_existing_ids(out_path)
    done.update(_load_progress(progress_path))
    remaining = [mid for mid in seed_rows if mid not in done]

    print(f"Output: {out_path}")
    print(f"Already done: {len(done)}, remaining: {len(remaining)}")
    print(f"Mode: {'card-only (no requests)' if args.card_only else 'full detail'}")
    print(f"Delay: {args.delay}s")
    print()

    if not remaining:
        print("Nothing to fetch — all IDs already in output.")
    else:
        pymal.set_delay(args.delay)
        written = 0
        errors = 0

        try:
            for i, mid in enumerate(remaining, 1):
                card = seed_rows[mid]
                prefix = f"[{i}/{len(remaining)}] ID {mid}"

                if args.card_only:
                    row = card_to_row(card)
                    _append_row(out_path, row)
                    done.add(mid)
                    written += 1
                    if i % 100 == 0:
                        _save_progress(progress_path, done)
                        print(f"  {prefix} (card) — {written} written")
                    continue

                print(f"  {prefix} {card.get('title', '')} ...", end=" ", flush=True)
                try:
                    anime = pymal.get_anime(mid)
                    row = anime_to_row(anime)
                    _append_row(out_path, row)
                    done.add(mid)
                    written += 1
                    _save_progress(progress_path, done)
                    score = f"score={row['score']:.2f}" if row["score"] else "unscored"
                    print(f"OK ({score}, {len(row['synopsis'])} chars synopsis)")
                except KeyboardInterrupt:
                    raise
                except Exception as exc:
                    errors += 1
                    print(f"WARN: {exc} — falling back to card data")
                    row = card_to_row(card)
                    _append_row(out_path, row)
                    done.add(mid)
                    _save_progress(progress_path, done)

        except KeyboardInterrupt:
            print(f"\nInterrupted. Progress saved ({len(done)} done). Re-run to continue.")
            sys.exit(0)

        print(f"\nFetch complete: {written} written, {errors} errors/fallbacks")

    # --- Build HF dataset ---
    total_out = sum(1 for _ in open(out_path, encoding="utf-8"))
    print(f"\nTotal rows in {out_path}: {total_out}")

    build_hf_dataset(out_path, repo_id=args.repo if args.push else None)

    if os.path.exists(progress_path):
        os.remove(progress_path)
        print("Progress file removed (complete).")


if __name__ == "__main__":
    main()
