# AGENTS.md — pymal

Python scraper / API client for myanimelist.net: anime, manga, characters, people, user lists, plus ARM-based cross-referencing to other anime ID providers.

## Setup

```bash
pip install -e .
# Optional browser-impersonation transport (recommended against MAL's anti-scraping):
pip install -e .[stealth]   # pulls curl-cffi
# Test deps:
pip install -e .[test]      # pytest, vcrpy, pytest-vcr
```

Requires Python >= 3.8. Sole runtime dependency is `requests`; `curl-cffi` is optional.

## Test

```bash
pytest
```

Tests are offline smoke tests (`tests/test_smoke.py`): imports, dataclass instantiation, and `__all__` export coverage. No network is hit. `vcrpy`/`pytest-vcr` are declared for future cassette-backed tests; `tests/cassettes/` is gitignored and currently absent.

## Lint/Typecheck

None configured. No linter, formatter, or type-checker settings exist. Source uses `from __future__ import annotations` with typing hints but is not type-checked in CI.

## Layout

- `pymal/__init__.py` — public API surface; re-exports all functions and models, defines `__all__`, plus the convenience helper `get_anime_by_imdb` (IMDb → TVmaze → AniList → ARM → MAL chain).
- `pymal/transport.py` — HTTP layer. Lazy singleton session, `set_delay` (default 1.5 s rate limit), `reset_session`. Uses `curl-cffi` browser impersonation when installed, else falls back to `requests`.
- `pymal/_parse.py` — shared HTML parsing helpers.
- `pymal/anime.py`, `manga.py`, `character.py`, `people.py` — detail/sub-page fetchers (episodes, reviews, recommendations, stats, videos, pictures, news).
- `pymal/listing.py` — top lists, seasonal, schedules, genre/producer/magazine listings; both single-page and `iter_*` full-pagination variants; global feeds.
- `pymal/search.py` — `search_anime/manga/characters/people`.
- `pymal/user.py` — profile and anime/manga list scraping via the undocumented list JSON endpoints; `iter_*` paginators.
- `pymal/arm.py` — ARM (arm.haglund.dev) cross-reference client mapping MAL ↔ AniList/AniDB/Kitsu/TheTVDB/TMDB/IMDb/etc.; `to_external_ids` converts ARM responses to a mediavocab `ExternalIds`.
- `pymal/models.py` — plain `@dataclass` models (Anime, Manga, Character, Person, *Card, *ListEntry, stats, favorites, etc.), each with `as_dict`.
- `examples/` — runnable scripts (search, detail, seasonal, user lists, bulk/full-database scrape, HF dataset build).
- `docs/` — per-area Markdown docs (anime, manga, characters_people, user, models, transport, quickstart, recipes).

## Conventions (Org hard rules)

- Branches: work on `dev`, stable on `master`. NEVER use `main`.
- Never edit `pymal/version.py`; gh-automations bump semver from conventional-commit prefixes (`feat:`, `fix:`, `feat!:`).
- New repos are private by default; do not make source public without asking.
- Commit identity: `JarbasAi <jarbasai@mailfence.com>`.
- Reference `OpenVoiceOS/gh-automations` reusable workflows at `@dev`.
- No Neon / `neon-*` references.
- No meta-commentary in docs/commits/code (no history, dates, or "before times"). Describe current state only.
- CI is provided by `OpenVoiceOS/gh-automations` (not yet wired up here).

## Gotchas

- `mediavocab` is imported lazily inside `pymal/arm.py` (`to_external_ids`) and is NOT declared in `pyproject.toml` dependencies — that function fails unless `mediavocab` is installed separately.
- `[project.urls] Homepage` points to `github.com/OpenJarbas/pymal`, but the actual remote is `TigreGotico/pymal`. Stale URL.
- MAL actively blocks aggressive scrapers; keep the request delay up (`set_delay`) and prefer the `stealth` extra to avoid 429s.
- Large generated data artifacts (`*.jsonl`, `*.parquet`, `*.csv`, `*.png`) sit untracked in the repo root from example runs; they are gitignored, do not commit them.
- Models are dataclasses (not Pydantic). Cross-reference output is the only place a mediavocab type appears.
