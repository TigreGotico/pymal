"""Bulk (catalogue-wide) harvesters for pymal, built on the shared harvestkit engine.

This is an opt-in extra (``pip install pymal[harvest]``). Importing this
package registers the available sources with harvestkit's registry.
"""
from __future__ import annotations

from pymal.harvest import manga  # noqa: F401  (import registers JikanMangaSource)


def main() -> int:
    """Console-script entry point: ``pymal-harvest``."""
    from harvestkit.engine import run_cli

    from pymal.harvest.manga import JikanMangaSource

    return run_cli(JikanMangaSource)
