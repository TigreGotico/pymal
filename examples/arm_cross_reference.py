"""Cross-reference a MAL anime ID to AniList, AniDB, IMDb, and TVDB via ARM.

ARM (https://arm.haglund.dev) is a separate service from MyAnimeList — this
example does not use pymal.transport or pymal.set_delay().
"""
from pymal import arm


def main() -> None:
    mal_id = 1  # Cowboy Bebop
    raw = arm.get_ids(mal_id)
    if not raw:
        print("ARM lookup failed or returned no data")
        return

    ids = arm.to_external_ids(raw)
    print(f"MAL {mal_id} cross-references to:")
    print(f"  AniList: {ids.anilist_id}")
    print(f"  AniDB:   {ids.anidb_id}")
    print(f"  IMDb:    {ids.imdb}")
    print(f"  TVDB:    {ids.tvdb}")
    print(f"  extra:   {ids.extra}")


if __name__ == "__main__":
    main()
