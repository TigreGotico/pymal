# TODO — pymal

## Open issues

- [ ] #2 Dependency Dashboard (Renovate bot meta-issue)

## Gaps

- [ ] No CI workflows at all (`.github/workflows/` absent). Add gh-automations reusable workflows: build-tests, coverage, license-check, release_workflow, publish_stable (referenced at `@dev`).
- [ ] Tests are import/instantiation smoke only; no parsing tests. `vcrpy`/`pytest-vcr` are declared but no cassettes exist (`tests/cassettes/` gitignored/absent) — add recorded-response tests for the parsers in `anime.py`, `manga.py`, `listing.py`, `user.py`, `search.py`.
- [ ] `mediavocab` used in `pymal/arm.py::to_external_ids` but not declared in `pyproject.toml` dependencies (not even as an optional extra). Either add it as a dependency/extra or guard the import with a clear error.
- [ ] `[project.urls] Homepage` is stale: points to `github.com/OpenJarbas/pymal`, remote is `TigreGotico/pymal`. Fix the URL.
- [ ] No lint/typecheck configuration despite typed source. Consider adding the standard tooling.

## Code TODOs

None found. (No TODO/FIXME/XXX markers in `pymal/` or `examples/`.)
