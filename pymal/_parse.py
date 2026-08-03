"""HTML/JSON parsing helpers for myanimelist.net pages."""
from __future__ import annotations

import html as _html_mod
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

BASE_URL = "https://myanimelist.net"


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def _strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = _html_mod.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", text).strip()


def _clean(text: str) -> str:
    return _strip_tags(text).strip()


def _parse_int(text: str) -> Optional[int]:
    if not text:
        return None
    text = re.sub(r"[,\s]", "", text.strip())
    m = re.search(r"\d+", text)
    return int(m.group()) if m else None


def _parse_float(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"[\d.]+", text.strip())
    try:
        return float(m.group()) if m else None
    except ValueError:
        return None


def _extract_mal_id(url: str) -> int:
    m = re.search(r"/(?:anime|manga|character|people)/(\d+)", url)
    return int(m.group(1)) if m else 0


def _sidebar_value(html: str, label: str) -> str:
    pattern = rf'<span[^>]*class="dark_text"[^>]*>{re.escape(label)}[:\s]*</span>\s*(.*?)(?=<span[^>]*class="dark_text"|</div>|<br)'
    m = re.search(pattern, html, re.DOTALL | re.I)
    if not m:
        return ""
    return _clean(m.group(1))


def _sidebar_links(html: str, label: str) -> List[str]:
    pattern = rf'<span[^>]*class="dark_text"[^>]*>{re.escape(label)}[:\s]*</span>(.*?)(?=<span[^>]*class="dark_text"|</div>)'
    m = re.search(pattern, html, re.DOTALL | re.I)
    if not m:
        return []
    block = m.group(1)
    return [_clean(t) for t in re.findall(r'<a[^>]*>([^<]+)</a>', block) if _clean(t) not in ("", "add some")]


def _sidebar_links_with_ids(html: str, label: str, id_pattern: str) -> List[Tuple[str, Optional[int]]]:
    """Like _sidebar_links but also captures a numeric ID from the href.

    id_pattern is a regex applied to the href, e.g. r'/anime/producer/(\\d+)/'.
    Returns list of (name, id_or_None) tuples.
    """
    pattern = rf'<span[^>]*class="dark_text"[^>]*>{re.escape(label)}[:\s]*</span>(.*?)(?=<span[^>]*class="dark_text"|</div>)'
    m = re.search(pattern, html, re.DOTALL | re.I)
    if not m:
        return []
    block = m.group(1)
    results = []
    for anchor in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', block):
        href, text = anchor.group(1), _clean(anchor.group(2))
        if not text or text in ("", "add some"):
            continue
        id_match = re.search(id_pattern, href)
        entity_id = int(id_match.group(1)) if id_match else None
        results.append((text, entity_id))
    return results


def _sidebar_stat(html: str, label: str) -> str:
    # match plain text OR anchor link text after the label span
    pattern = rf'<span[^>]*class="dark_text"[^>]*>{re.escape(label)}[:\s]*</span>\s*(.*?)(?=<span[^>]*class="dark_text"|</div>)'
    m = re.search(pattern, html, re.DOTALL | re.I)
    if not m:
        return ""
    raw = m.group(1)
    # if it contains anchor tags, grab the link text; otherwise strip all tags
    link_texts = re.findall(r'<a[^>]*>([^<]+)</a>', raw)
    if link_texts:
        return _clean(link_texts[0])
    return _clean(raw)


# ---------------------------------------------------------------------------
# Anime detail page
# ---------------------------------------------------------------------------

def parse_anime_page(html: str, mal_id: int) -> dict:
    url = f"{BASE_URL}/anime/{mal_id}"

    # Title — try specific containers first to avoid matching breadcrumb "Top" span
    m = re.search(r'<div[^>]*class="[^"]*h1-title[^"]*"[^>]*>.*?<strong[^>]*>([^<]+)</strong>', html, re.DOTALL)
    if not m:
        m = re.search(r'<h1[^>]*class="[^"]*title-name[^"]*"[^>]*>([^<]+)</h1>', html)
    if not m:
        m = re.search(r'<p[^>]*class="[^"]*title-name[^"]*"[^>]*><strong[^>]*>([^<]+)</strong>', html)
    if not m:
        m = re.search(r'<h1[^>]*itemprop="name"[^>]*>([^<]+)</h1>', html)
    title = _clean(m.group(1)) if m else ""

    # Image
    m_img = re.search(r'<img[^>]*itemprop="image"[^>]*src="([^"]+)"', html)
    if not m_img:
        m_img = re.search(r'<div[^>]*class="[^"]*leftside[^"]*".*?<img[^>]*src="([^"]+cdn\.myanimelist\.net[^"]+)"', html, re.DOTALL)
    image_url = m_img.group(1) if m_img else ""

    # Trailer
    m_trailer = re.search(r'data-video-id="([^"]+)"', html)
    trailer_url = f"https://www.youtube.com/watch?v={m_trailer.group(1)}" if m_trailer else ""

    # Sidebar fields
    english_title = _sidebar_stat(html, "English")
    japanese_title = _sidebar_stat(html, "Japanese")
    synonyms_raw = _sidebar_stat(html, "Synonyms")
    synonyms = [s.strip() for s in synonyms_raw.split(",") if s.strip()] if synonyms_raw else []

    anime_type = _sidebar_stat(html, "Type")
    episodes_raw = _sidebar_stat(html, "Episodes")
    episodes = _parse_int(episodes_raw) if episodes_raw and episodes_raw.lower() != "unknown" else None
    status = _sidebar_stat(html, "Status")

    # Aired
    aired_raw = _sidebar_stat(html, "Aired")
    aired_from, aired_to = _parse_aired(aired_raw)

    # Season / year
    season_raw = _sidebar_stat(html, "Premiered")
    season, year = _parse_season(season_raw)

    broadcast = _sidebar_stat(html, "Broadcast")

    producers_with_ids = _sidebar_links_with_ids(html, "Producers", r'/anime/producer/(\d+)/')
    producers = [name for name, _ in producers_with_ids]
    producer_ids = {name: pid for name, pid in producers_with_ids if pid is not None}
    licensors = _sidebar_links(html, "Licensors")
    studios_with_ids = _sidebar_links_with_ids(html, "Studios", r'/anime/producer/(\d+)/')
    studios = [name for name, _ in studios_with_ids]
    studio_ids = {name: pid for name, pid in studios_with_ids if pid is not None}
    source = _sidebar_stat(html, "Source")

    genres = _sidebar_links(html, "Genres")
    if not genres:
        genres = _sidebar_links(html, "Genre")
    themes = _sidebar_links(html, "Themes")
    if not themes:
        themes = _sidebar_links(html, "Theme")
    demographics = _sidebar_links(html, "Demographics")
    if not demographics:
        demographics = _sidebar_links(html, "Demographic")

    duration = _sidebar_stat(html, "Duration")
    rating = _sidebar_stat(html, "Rating")

    # Stats block — score
    score = None
    m_score = re.search(
        r'<span[^>]*itemprop="ratingValue"[^>]*>([\d.]+)</span>',
        html,
    )
    if not m_score:
        m_score = re.search(
            r'<span[^>]*class="[^"]*score-label[^"]*"[^>]*>([\d.N/A]+)</span>',
            html,
        )
    if m_score and m_score.group(1) not in ("N/A", ""):
        score = _parse_float(m_score.group(1))

    scored_by = None
    m_sb = re.search(r'scored by <strong[^>]*>([\d,]+)</strong>\s*users', html, re.I)
    if not m_sb:
        m_sb = re.search(r'itemprop="ratingCount"[^>]*>([\d,]+)<', html)
    if m_sb:
        scored_by = _parse_int(m_sb.group(1))

    ranked = None
    m_ranked = re.search(r'<span[^>]*class="dark_text"[^>]*>Ranked[:\s]*</span>\s*#([\d,]+)', html, re.I)
    if m_ranked:
        ranked = _parse_int(m_ranked.group(1))

    popularity = None
    m_pop = re.search(r'<span[^>]*class="dark_text"[^>]*>Popularity[:\s]*</span>\s*#([\d,]+)', html, re.I)
    if m_pop:
        popularity = _parse_int(m_pop.group(1))

    members = None
    m_mem = re.search(r'<span[^>]*class="dark_text"[^>]*>Members[:\s]*</span>\s*([\d,]+)', html, re.I)
    if m_mem:
        members = _parse_int(m_mem.group(1))

    favorites = None
    m_fav = re.search(r'<span[^>]*class="dark_text"[^>]*>Favorites[:\s]*</span>\s*([\d,]+)', html, re.I)
    if m_fav:
        favorites = _parse_int(m_fav.group(1))

    # Synopsis
    synopsis = ""
    m_syn = re.search(
        r'<p[^>]*itemprop="description"[^>]*>(.*?)</p>',
        html, re.DOTALL
    )
    if m_syn:
        synopsis = _clean(m_syn.group(1))

    # Background
    background = ""
    m_bg = re.search(
        r'<h2[^>]*>\s*Background\s*</h2>\s*<p[^>]*>(.*?)</p>',
        html, re.DOTALL | re.I,
    )
    if m_bg:
        background = _clean(m_bg.group(1))

    # Related
    related = parse_related_entries(html)

    # Opening / ending themes
    opening_themes = _parse_theme_songs(html, "opnening")
    ending_themes = _parse_theme_songs(html, "ending")

    return {
        "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
        "english_title": english_title, "japanese_title": japanese_title,
        "synonyms": synonyms, "type": anime_type, "episodes": episodes,
        "status": status, "aired_from": aired_from, "aired_to": aired_to,
        "season": season, "year": year, "broadcast": broadcast,
        "producers": producers, "licensors": licensors, "studios": studios,
        "studio_ids": studio_ids, "producer_ids": producer_ids,
        "source": source, "genres": genres, "themes": themes, "demographics": demographics,
        "duration": duration, "rating": rating, "score": score, "scored_by": scored_by,
        "ranked": ranked, "popularity": popularity, "members": members, "favorites": favorites,
        "synopsis": synopsis, "background": background,
        "related": related, "opening_themes": opening_themes, "ending_themes": ending_themes,
        "trailer_url": trailer_url,
    }


def _parse_aired(raw: str) -> Tuple[str, str]:
    if not raw or raw.lower() == "not available":
        return "", ""
    if " to " in raw:
        parts = raw.split(" to ", 1)
        return parts[0].strip(), parts[1].strip()
    return raw.strip(), ""


def _parse_season(raw: str) -> Tuple[str, Optional[int]]:
    if not raw:
        return "", None
    m = re.search(r'(Spring|Summer|Fall|Winter)\s+(\d{4})', raw, re.I)
    if m:
        return f"{m.group(1).lower()} {m.group(2)}", int(m.group(2))
    m_year = re.search(r'(\d{4})', raw)
    return raw.strip(), int(m_year.group(1)) if m_year else None


def _parse_theme_songs(html: str, css_class: str) -> List[str]:
    """Extract opening or ending theme songs from the theme-songs div."""
    # Stop at the other theme div or at the next major section
    other = "ending" if css_class == "opnening" else "opnening"
    m = re.search(
        rf'<div[^>]*class="[^"]*theme-songs[^"]*{re.escape(css_class)}[^"]*"[^>]*>(.*?)'
        rf'(?=<div[^>]*class="[^"]*theme-songs[^"]*{re.escape(other)}[^"]*"|<h2)',
        html, re.DOTALL,
    )
    if not m:
        return []
    block = re.sub(r'<script[^>]*>.*?</script>', '', m.group(1), flags=re.DOTALL)
    # also strip oped-popup divs (they contain noise inside the theme block)
    block = re.sub(r'<div[^>]*class="oped-popup[^>]*>.*?</div>', '', block, flags=re.DOTALL)
    songs = []
    titles = re.findall(r'<span[^>]*class="theme-song-title"[^>]*>([^<]+)</span>', block)
    artists = re.findall(r'<span[^>]*class="theme-song-artist"[^>]*>([^<]+)</span>', block)
    eps_list = re.findall(r'<span[^>]*class="theme-song-episode"[^>]*>([^<]+)</span>', block)
    for i, title in enumerate(titles):
        title = _clean(title)
        artist = _clean(artists[i]) if i < len(artists) else ""
        eps = _clean(eps_list[i]) if i < len(eps_list) else ""
        parts = [p for p in (title, artist, eps) if p]
        songs.append(" ".join(parts))
    return songs


def parse_related_entries(html: str) -> Dict[str, list]:
    """Parse the Related Entries section.

    MAL now uses div.related-entries with div.entry tiles instead of a table.
    Fallback to the legacy table format for older cached pages.
    """
    related: Dict[str, list] = {}

    # Modern layout: <div class="related-entries"> with detail divs per entry
    m_section = re.search(
        r'<div[^>]*class="related-entries"[^>]*>(.*?)(?=<div[^>]*class="[^"]*mauto[^"]*"|<h2|$)',
        html, re.DOTALL,
    )
    if m_section:
        block = m_section.group(1)
        # Each entry has a .content div containing .relation + .title link
        for m_detail in re.finditer(r'<div[^>]*class="content"[^>]*>(.*?)</div>\s*</div>', block, re.DOTALL):
            detail = m_detail.group(1)
            m_rel = re.search(r'<div[^>]*class="relation"[^>]*>\s*([^\n<(]+)', detail)
            m_link = re.search(
                r'<a[^>]+href="(https?://myanimelist\.net/(?:anime|manga)/(\d+)/[^"]*)"[^>]*>([^<]+)</a>',
                detail,
            )
            if not m_rel or not m_link:
                continue
            rel_type = _clean(m_rel.group(1))
            url = m_link.group(1)
            title = _clean(m_link.group(3))
            entry_type = "manga" if "/manga/" in url else "anime"
            eid = int(m_link.group(2))
            related.setdefault(rel_type, []).append(
                {"mal_id": eid, "title": title, "url": url, "entry_type": entry_type}
            )
        if related:
            return related

    # Legacy table layout
    m_table = re.search(
        r'<table[^>]*class="[^"]*anime_detail_related_anime[^"]*"[^>]*>(.*?)</table>',
        html, re.DOTALL,
    )
    if not m_table:
        return related
    for row in re.finditer(r'<tr[^>]*>(.*?)</tr>', m_table.group(1), re.DOTALL):
        row_html = row.group(1)
        m_label = re.search(r'<td[^>]*>\s*([^<:]+):', row_html)
        if not m_label:
            continue
        rel_type = _clean(m_label.group(1))
        for m_link in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', row_html):
            href = m_link.group(1)
            title = _clean(m_link.group(2))
            if not title:
                continue
            full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
            if "/anime/" not in full_url and "/manga/" not in full_url:
                continue
            entry_type = "manga" if "/manga/" in full_url else "anime"
            eid = _extract_mal_id(full_url)
            related.setdefault(rel_type, []).append(
                {"mal_id": eid, "title": title, "url": full_url, "entry_type": entry_type}
            )
    return related


# ---------------------------------------------------------------------------
# Anime characters + staff page
# ---------------------------------------------------------------------------

def parse_characters_staff_page(html: str) -> Tuple[List[dict], List[dict]]:
    """Parse /anime/{id}/characters page.

    Each character is in a div.js-navi-anime-character container.
    Staff are in plain <table> elements after the Staff <h2>.
    """
    return _parse_char_blocks(html), _parse_staff_blocks(html)


def _parse_char_blocks(html: str) -> List[dict]:
    """Extract characters from div.js-navi-anime-character containers."""
    results = []
    seen: set = set()
    # isolate the Characters section (stop at Staff h2)
    m_section = re.search(r'Characters[^<]*</h2>(.*?)(?=<h2[^>]*>\s*Staff|$)', html, re.DOTALL | re.I)
    if not m_section:
        return results
    section = m_section.group(1)

    # split by container divs; use js-anime-character-table as the boundary
    char_blocks = re.split(r'(?=<table[^>]*class="js-anime-character-table")', section)

    for block in char_blocks:
        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/character/(\d+)/[^"]*)"', block)
        if not m_link:
            continue
        char_url = m_link.group(1)
        char_id = int(m_link.group(2))
        if char_id in seen:
            continue
        seen.add(char_id)

        m_name = re.search(r'<h3[^>]*class="h3_character_name"[^>]*>([^<]+)</h3>', block)
        char_name = _clean(m_name.group(1)) if m_name else ""

        m_img = re.search(r'<img[^>]+(?:data-src|src)="(https?://cdn\.myanimelist\.net/[^"]+)"', block)
        char_img = m_img.group(1) if m_img else ""

        spaceit = re.findall(r'class="spaceit_pad"[^>]*>\s*([^\n<]+)', block)
        role = ""
        for s in spaceit:
            s = _clean(s).replace("\xa0", "").strip()
            if s and "Favorites" not in s and s:
                role = s
                break

        # VA: first people/ link in the same block
        m_va = re.search(r'<a[^>]+href="(https?://myanimelist\.net/people/(\d+)/[^"]*)"[^>]*>\s*([^<]+)</a>', block)
        va_name = _clean(m_va.group(3)) if m_va else ""
        va_url = m_va.group(1) if m_va else ""

        results.append({
            "mal_id": char_id, "name": char_name, "url": char_url,
            "image_url": char_img, "role": role,
            "voice_actor_name": va_name, "va_url": va_url, "va_image_url": "",
        })
    return results


def _parse_staff_blocks(html: str) -> List[dict]:
    """Extract staff from plain tables after the Staff h2."""
    results = []
    seen: set = set()
    m_section = re.search(r'<h2[^>]*>\s*Staff\s*</h2>(.*?)(?=<h2|$)', html, re.DOTALL | re.I)
    if not m_section:
        return results
    section = m_section.group(1)

    for m_table in re.finditer(r'<table[^>]*>(.*?)</table>', section, re.DOTALL):
        table = m_table.group(1)
        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/people/(\d+)/[^"]*)"[^>]*>([^<]+)</a>', table)
        if not m_link:
            continue
        person_url = m_link.group(1)
        person_id = int(m_link.group(2))
        if person_id in seen:
            continue
        seen.add(person_id)
        name = _clean(m_link.group(3))
        m_img = re.search(r'<img[^>]+(?:data-src|src)="(https?://cdn\.myanimelist\.net/[^"]+)"', table)
        img = m_img.group(1) if m_img else ""
        m_role = re.search(r'<small>([^<]+)</small>', table)
        role = _clean(m_role.group(1)) if m_role else ""
        results.append({
            "mal_id": person_id, "name": name, "url": person_url,
            "image_url": img, "role": role,
        })
    return results




# ---------------------------------------------------------------------------
# Episode list page
# ---------------------------------------------------------------------------

def parse_episodes_page(html: str) -> List[dict]:
    episodes = []
    # Episode table rows
    for m in re.finditer(
        r'<tr[^>]*class="[^"]*episode-list-data[^"]*"[^>]*>(.*?)</tr>',
        html, re.DOTALL
    ):
        row = m.group(1)
        # Episode number
        m_num = re.search(r'<td[^>]*class="[^"]*episode-number[^"]*"[^>]*>(\d+)</td>', row)
        num = int(m_num.group(1)) if m_num else 0

        # Title + discussion link
        m_title = re.search(r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*fl-l[^"]*"[^>]*>([^<]+)</a>', row)
        if not m_title:
            m_title = re.search(r'<td[^>]*class="[^"]*episode-title[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', row, re.DOTALL)
        title = _clean(m_title.group(2)) if m_title else ""
        disc_url = m_title.group(1) if m_title else ""
        if disc_url and not disc_url.startswith("http"):
            disc_url = f"{BASE_URL}{disc_url}"

        # Japanese title
        m_jp = re.search(r'<span[^>]*class="[^"]*di-ib[^"]*"[^>]*>([^<]+)</span>', row)
        jp_title = _clean(m_jp.group(1)) if m_jp else ""

        # Air date
        m_date = re.search(r'<td[^>]*class="[^"]*episode-aired[^"]*"[^>]*>([^<]+)</td>', row)
        aired = _clean(m_date.group(1)) if m_date else ""

        episodes.append({
            "number": num, "title": title, "japanese_title": jp_title,
            "aired": aired, "discussion_url": disc_url,
        })
    return episodes


# ---------------------------------------------------------------------------
# Reviews page
# ---------------------------------------------------------------------------

def parse_reviews_page(html: str) -> List[dict]:
    reviews = []
    for m in re.finditer(
        r'<div[^>]*class="[^"]*review-element[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
        html, re.DOTALL
    ):
        block = m.group(1)

        m_author = re.search(r'<a[^>]*href="(https?://myanimelist\.net/profile/[^"]+)"[^>]*>([^<]+)</a>', block)
        author = _clean(m_author.group(2)) if m_author else ""
        author_url = m_author.group(1) if m_author else ""

        m_score = re.search(r'<div[^>]*class="[^"]*num[^"]*"[^>]*>(\d+)</div>', block)
        score = int(m_score.group(1)) if m_score else None

        m_helpful = re.search(r'(\d+)\s*(?:people\s*)?found\s*this\s*(?:review\s*)?helpful', block, re.I)
        helpful = int(m_helpful.group(1)) if m_helpful else 0

        m_date = re.search(r'<div[^>]*class="[^"]*date[^"]*"[^>]*>([^<]+)</div>', block)
        created_at = _clean(m_date.group(1)) if m_date else ""

        m_text = re.search(r'<div[^>]*class="[^"]*text[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        summary = _clean(m_text.group(1))[:500] if m_text else ""

        m_url = re.search(r'<a[^>]*href="([^"]+/reviews/[^"]+)"', block)
        rev_url = m_url.group(1) if m_url else ""

        if author:
            reviews.append({
                "author": author, "author_url": author_url, "score": score,
                "helpful_count": helpful, "created_at": created_at,
                "summary": summary, "url": rev_url,
            })
    return reviews


# ---------------------------------------------------------------------------
# Recommendations page
# ---------------------------------------------------------------------------

def parse_recommendations_page(html: str) -> List[dict]:
    """Parse the recommendations carousel from /anime/{id}/userrecs or /manga/{id}/userrecs.

    MAL renders each recommended entry as an <li class="btn-anime"> card with a
    title attribute, a link to /recommendations/(anime|manga)/{src}-{target},
    a "N Users" count, and a lazy-loaded thumbnail (data-src).
    """
    recs = []
    seen: set = set()
    for m in re.finditer(
        r'<li[^>]*class="btn-anime"[^>]*title="([^"]*)"[^>]*>\s*'
        r'<a[^>]+href="[^"]*/recommendations/(anime|manga)/\d+-(\d+)"[^>]*>.*?'
        r'<span[^>]*class="users"[^>]*>([\d,]+)\s*Users?</span>.*?'
        r'data-src="([^"]+)"',
        html, re.DOTALL,
    ):
        title = _clean(m.group(1))
        entry_type = m.group(2)
        mal_id = int(m.group(3))
        if mal_id in seen:
            continue
        seen.add(mal_id)
        num_recs = _parse_int(m.group(4)) or 0
        image_url = m.group(5)
        url = f"{BASE_URL}/{entry_type}/{mal_id}"

        recs.append({"mal_id": mal_id, "title": title, "url": url, "image_url": image_url, "num_recommendations": num_recs})
    return recs


# ---------------------------------------------------------------------------
# Manga detail page
# ---------------------------------------------------------------------------

def parse_manga_page(html: str, mal_id: int) -> dict:
    url = f"{BASE_URL}/manga/{mal_id}"

    m = re.search(r'<span[^>]*itemprop="name"[^>]*>([^<]+)</span>', html)
    if not m:
        m = re.search(r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>\s*<strong[^>]*>([^<]+)</strong>', html)
    title = _clean(m.group(1)) if m else ""

    m_img = re.search(r'<img[^>]*itemprop="image"[^>]*src="([^"]+)"', html)
    if not m_img:
        m_img = re.search(r'<div[^>]*class="[^"]*leftside[^"]*".*?<img[^>]*src="([^"]+cdn\.myanimelist\.net[^"]+)"', html, re.DOTALL)
    image_url = m_img.group(1) if m_img else ""

    english_title = _sidebar_stat(html, "English")
    japanese_title = _sidebar_stat(html, "Japanese")
    synonyms_raw = _sidebar_stat(html, "Synonyms")
    synonyms = [s.strip() for s in synonyms_raw.split(",") if s.strip()] if synonyms_raw else []

    manga_type = _sidebar_stat(html, "Type")
    volumes_raw = _sidebar_stat(html, "Volumes")
    chapters_raw = _sidebar_stat(html, "Chapters")
    volumes = _parse_int(volumes_raw) if volumes_raw and volumes_raw.lower() != "unknown" else None
    chapters = _parse_int(chapters_raw) if chapters_raw and chapters_raw.lower() != "unknown" else None

    status = _sidebar_stat(html, "Status")
    published_raw = _sidebar_stat(html, "Published")
    published_from, published_to = _parse_aired(published_raw)

    genres = _sidebar_links(html, "Genres")
    if not genres:
        genres = _sidebar_links(html, "Genre")
    themes = _sidebar_links(html, "Themes")
    if not themes:
        themes = _sidebar_links(html, "Theme")
    demographics = _sidebar_links(html, "Demographics")
    if not demographics:
        demographics = _sidebar_links(html, "Demographic")

    score, scored_by, ranked, popularity, members, favorites = _parse_stats_block(html)

    synopsis = ""
    m_syn = re.search(r'<p[^>]*itemprop="description"[^>]*>(.*?)</p>', html, re.DOTALL)
    if m_syn:
        synopsis = _clean(m_syn.group(1))

    background = ""
    m_bg = re.search(r'<h2[^>]*>\s*Background\s*</h2>\s*<p[^>]*>(.*?)</p>', html, re.DOTALL | re.I)
    if m_bg:
        background = _clean(m_bg.group(1))

    authors = _parse_manga_authors(html)
    serialization = _sidebar_links(html, "Serialization")
    related = parse_related_entries(html)

    return {
        "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
        "english_title": english_title, "japanese_title": japanese_title,
        "synonyms": synonyms, "type": manga_type, "volumes": volumes, "chapters": chapters,
        "status": status, "published_from": published_from, "published_to": published_to,
        "genres": genres, "themes": themes, "demographics": demographics,
        "score": score, "scored_by": scored_by, "ranked": ranked,
        "popularity": popularity, "members": members, "favorites": favorites,
        "synopsis": synopsis, "background": background,
        "authors": authors, "serialization": serialization, "related": related,
    }


def _parse_stats_block(html: str) -> Tuple[Optional[float], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]]:
    score = None
    m_score = re.search(r'<span[^>]*itemprop="ratingValue"[^>]*>([\d.]+)</span>', html)
    if not m_score:
        m_score = re.search(r'<span[^>]*class="[^"]*score-label[^"]*"[^>]*>([\d.N/A]+)</span>', html)
    if m_score and m_score.group(1) not in ("N/A", ""):
        score = _parse_float(m_score.group(1))

    scored_by = None
    m_sb = re.search(r'itemprop="ratingCount"[^>]*>([\d,]+)<', html)
    if not m_sb:
        m_sb = re.search(r'scored by <strong[^>]*>([\d,]+)</strong>', html, re.I)
    if m_sb:
        scored_by = _parse_int(m_sb.group(1))

    ranked = None
    m_r = re.search(r'<span[^>]*class="dark_text"[^>]*>Ranked[:\s]*</span>\s*#([\d,]+)', html, re.I)
    if m_r:
        ranked = _parse_int(m_r.group(1))

    popularity = None
    m_p = re.search(r'<span[^>]*class="dark_text"[^>]*>Popularity[:\s]*</span>\s*#([\d,]+)', html, re.I)
    if m_p:
        popularity = _parse_int(m_p.group(1))

    members = None
    m_m = re.search(r'<span[^>]*class="dark_text"[^>]*>Members[:\s]*</span>\s*([\d,]+)', html, re.I)
    if m_m:
        members = _parse_int(m_m.group(1))

    favorites = None
    m_f = re.search(r'<span[^>]*class="dark_text"[^>]*>Favorites[:\s]*</span>\s*([\d,]+)', html, re.I)
    if m_f:
        favorites = _parse_int(m_f.group(1))

    return score, scored_by, ranked, popularity, members, favorites


def _parse_manga_authors(html: str) -> List[dict]:
    authors = []
    m = re.search(
        r'<span[^>]*class="dark_text"[^>]*>Authors?[:\s]*</span>(.*?)(?=<span[^>]*class="dark_text"|</div>)',
        html, re.DOTALL | re.I
    )
    if not m:
        return authors
    block = m.group(1)
    for m_a in re.finditer(r'<a[^>]*href="(/people/(\d+)/[^"]*)"[^>]*>([^<]+)</a>\s*\(([^)]+)\)', block):
        url = f"{BASE_URL}{m_a.group(1)}"
        pid = int(m_a.group(2))
        name = _clean(m_a.group(3))
        role = _clean(m_a.group(4))
        authors.append({"mal_id": pid, "name": name, "url": url, "role": role})
    return authors


# ---------------------------------------------------------------------------
# Character detail page
# ---------------------------------------------------------------------------

def parse_character_page(html: str, mal_id: int) -> dict:
    url = f"{BASE_URL}/character/{mal_id}"

    # name in h1-title div > strong, fallback to <title> tag
    m = re.search(r'<div[^>]*class="[^"]*h1-title[^"]*"[^>]*>.*?<strong[^>]*>([^<]+)</strong>', html, re.DOTALL)
    if not m:
        m = re.search(r'<title>\s*([^(\n<]+?)\s*\(', html)
    name = _clean(m.group(1)) if m else ""

    # japanese name usually in a span with font-size style right after the name
    m_jp = re.search(r'<span[^>]*style="font-size[^"]*"[^>]*>([^<]+)</span>', html)
    japanese_name = _clean(m_jp.group(1)) if m_jp else ""

    m_img = re.search(r'<img[^>]+(?:data-src|src)="(https?://cdn\.myanimelist\.net/images/characters/[^"]+)"', html)
    image_url = m_img.group(1) if m_img else ""

    # Name from normal_header (fallback, more reliable for name+jp)
    m_nh = re.search(r'<h2[^>]*class="normal_header"[^>]*>([^<]+)', html)
    if m_nh and not name:
        name = _clean(m_nh.group(1))
    m_jp2 = re.search(r'<h2[^>]*class="normal_header"[^>]*>[^<]+<span[^>]*><small>([^<]+)</small>', html)
    if m_jp2 and not japanese_name:
        japanese_name = _clean(m_jp2.group(1))

    # About: text after normal_header h2, before Animeography h2
    about = ""
    m_about = re.search(
        r'<h2[^>]*class="normal_header"[^>]*>.*?</h2>(.*?)(?=<h2[^>]*class="normal_header"|<div[^>]*id=)',
        html, re.DOTALL,
    )
    if m_about:
        about = _clean(m_about.group(1))[:2000]

    anime_roles = _parse_char_anime_roles(html)
    manga_roles = _parse_char_manga_roles(html)
    voice_actors = _parse_char_vas(html)

    return {
        "mal_id": mal_id, "name": name, "url": url, "japanese_name": japanese_name,
        "about": about, "image_url": image_url,
        "anime_roles": anime_roles, "manga_roles": manga_roles, "voice_actors": voice_actors,
    }


def _char_section(html: str, label: str) -> str:
    """Return the HTML block after a character-page section heading div."""
    m = re.search(
        rf'<div[^>]*class="[^"]*normal_header[^"]*"[^>]*>\s*{re.escape(label)}\s*</div>(.*?)(?=<div[^>]*class="[^"]*normal_header|$)',
        html, re.DOTALL | re.I,
    )
    return m.group(1) if m else ""


def _parse_char_anime_roles(html: str) -> List[dict]:
    block = _char_section(html, "Animeography")
    if not block:
        return []
    results = []
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', block, re.DOTALL):
        row = m.group(1)
        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/anime/(\d+)/[^"]*)"[^>]*>([^<]+)</a>', row)
        if not m_link:
            continue
        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', row)
        m_role = re.search(r'<div[^>]*class="[^"]*s[^"]*"[^>]*>([^<]+)</div>', row)
        if not m_role:
            m_role = re.search(r'<small>([^<]+)</small>', row)
        results.append({
            "anime_title": _clean(m_link.group(3)),
            "anime_url": m_link.group(1),
            "image_url": m_img.group(1) if m_img else "",
            "role": _clean(m_role.group(1)) if m_role else "",
        })
    return results


def _parse_char_manga_roles(html: str) -> List[dict]:
    block = _char_section(html, "Mangaography")
    if not block:
        return []
    results = []
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', block, re.DOTALL):
        row = m.group(1)
        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/manga/(\d+)/[^"]*)"[^>]*>([^<]+)</a>', row)
        if not m_link:
            continue
        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', row)
        m_role = re.search(r'<small>([^<]+)</small>', row)
        results.append({
            "manga_title": _clean(m_link.group(3)),
            "manga_url": m_link.group(1),
            "image_url": m_img.group(1) if m_img else "",
            "role": _clean(m_role.group(1)) if m_role else "",
        })
    return results


def _parse_char_vas(html: str) -> List[dict]:
    block = _char_section(html, "Voice Actors")
    if not block:
        return []
    results = []
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', block, re.DOTALL):
        row = m.group(1)
        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/people/(\d+)/[^"]*)"[^>]*>([^<]+)</a>', row)
        if not m_link:
            continue
        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', row)
        m_lang = re.search(r'<small>([^<]+)</small>', row)
        results.append({
            "name": _clean(m_link.group(3)),
            "url": m_link.group(1),
            "image_url": m_img.group(1) if m_img else "",
            "language": _clean(m_lang.group(1)) if m_lang else "",
        })
    return results


# ---------------------------------------------------------------------------
# People detail page
# ---------------------------------------------------------------------------

def parse_person_page(html: str, mal_id: int) -> dict:
    url = f"{BASE_URL}/people/{mal_id}"

    m = re.search(r'<h1[^>]*class="[^"]*title-name[^"]*"[^>]*><strong[^>]*>([^<]+)</strong></h1>', html)
    if not m:
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    name = _clean(m.group(1)) if m else ""

    m_jp = re.search(r'<span[^>]*class="[^"]*alternative-titles[^"]*"[^>]*>([^<]+)</span>', html)
    if not m_jp:
        m_jp = re.search(r'<h2[^>]*class="[^"]*normal_header[^"]*"[^>]*>[^<]+<span[^>]*>([^<]+)</span>', html)
    japanese_name = _clean(m_jp.group(1)) if m_jp else ""

    m_img = re.search(r'<div[^>]*class="[^"]*people-image[^"]*".*?<img[^>]+src="([^"]+)"', html, re.DOTALL)
    if not m_img:
        m_img = re.search(r'<img[^>]+alt="[^"]*"[^>]+src="([^"]+cdn\.myanimelist\.net/images/voiceactors[^"]+)"', html)
    image_url = m_img.group(1) if m_img else ""

    birthday = _sidebar_stat(html, "Birthday")
    hometown = _sidebar_stat(html, "Hometown")

    about = ""
    m_about = re.search(r'<div[^>]*class="[^"]*people-informantion-more[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m_about:
        m_about = re.search(r'<p[^>]*itemprop="description"[^>]*>(.*?)</p>', html, re.DOTALL)
    if m_about:
        about = _clean(m_about.group(1))[:2000]

    va_roles = _parse_person_va_roles(html)
    staff_roles = _parse_person_staff_roles(html)

    return {
        "mal_id": mal_id, "name": name, "url": url, "japanese_name": japanese_name,
        "birthday": birthday, "hometown": hometown, "about": about, "image_url": image_url,
        "va_roles": va_roles, "staff_roles": staff_roles,
    }


def _person_section(html: str, label: str) -> str:
    """Return HTML block after a people-page section heading div.

    Heading may contain a floatRightHeader span before the label text.
    """
    m = re.search(
        rf'<div[^>]*class="[^"]*normal_header[^"]*"[^>]*>(?:<span[^>]*>.*?</span>)?\s*{re.escape(label)}\s*</div>(.*?)(?=<div[^>]*class="[^"]*normal_header[^"]*"[^>]*>|$)',
        html, re.DOTALL | re.I,
    )
    if not m:
        m = re.search(
            rf'<h2[^>]*>\s*{re.escape(label)}\s*</h2>(.*?)(?=<h2[^>]*>|$)',
            html, re.DOTALL | re.I,
        )
    return m.group(1) if m else ""


def _parse_person_va_roles(html: str) -> List[dict]:
    block = _person_section(html, "Voice Acting Roles")
    if not block:
        block = _person_section(html, "Anime VA Roles")
    if not block:
        return []
    results = []
    for m in re.finditer(r'<tr[^>]*class="[^"]*js-people-va[^"]*"[^>]*>(.*?)</tr>', block, re.DOTALL):
        row = m.group(1)
        m_anime = re.search(r'<a[^>]+href="(https?://myanimelist\.net/anime/\d+/[^"]*)"[^>]*class="js-people-title"[^>]*>([^<]+)</a>', row)
        m_char = re.search(r'<a[^>]+href="(https?://myanimelist\.net/character/\d+/[^"]*)"[^>]*>([^<]+)</a>', row)
        m_role = re.search(r'<div[^>]*class="[^"]*spaceit_pad[^"]*"[^>]*>\s*([^<\n]+)\s*</div>', row)
        if not m_anime:
            continue
        results.append({
            "anime_title": _clean(m_anime.group(2)),
            "anime_url": m_anime.group(1),
            "character_name": _clean(m_char.group(2)) if m_char else "",
            "character_url": m_char.group(1) if m_char else "",
            "role": _clean(m_role.group(1)) if m_role else "",
        })
    return results


def _parse_person_staff_roles(html: str) -> List[dict]:
    block = _person_section(html, "Anime Staff Positions")
    if not block:
        block = _person_section(html, "Staff Positions")
    if not block:
        return []
    results = []
    for m in re.finditer(r'<tr[^>]*class="[^"]*js-people-staff[^"]*"[^>]*>(.*?)</tr>', block, re.DOTALL):
        row = m.group(1)
        m_anime = re.search(r'<a[^>]+href="(https?://myanimelist\.net/anime/\d+/[^"]*)"[^>]*class="js-people-title"[^>]*>([^<]+)</a>', row)
        if not m_anime:
            continue
        # role is the first <small> tag text in the row
        smalls = re.findall(r'<small[^>]*>([^<]+)</small>', row)
        role = _clean(smalls[0]) if smalls else ""
        results.append({
            "anime_title": _clean(m_anime.group(2)),
            "anime_url": m_anime.group(1),
            "role": role,
        })
    return results


# ---------------------------------------------------------------------------
# Search results
# ---------------------------------------------------------------------------

def _parse_search_table(html: str, entry_type: str) -> List[dict]:
    """Shared parser for /anime.php and /manga.php search result tables.

    MAL search pages render a 5-column table inside div.js-categories-seasonal:
      TD0: thumbnail image + URL
      TD1: title strong + URL
      TD2: type  (TV / Manga / etc.)
      TD3: episodes or volumes/chapters
      TD4: score
    """
    results = []
    seen: set = set()

    m_block = re.search(
        r'<div[^>]*class="[^"]*js-categories-seasonal[^"]*"[^>]*>(.*?)</table>',
        html, re.DOTALL,
    )
    if not m_block:
        return results

    for m_row in re.finditer(r'<tr[^>]*>(.*?)</tr>', m_block.group(1), re.DOTALL):
        row = m_row.group(1)
        if f'/{entry_type}/' not in row:
            continue

        # URL + MAL ID from the thumbnail anchor
        m_link = re.search(
            rf'href="(https?://myanimelist\.net/{entry_type}/(\d+)/[^"?#]*)"',
            row,
        )
        if not m_link:
            continue
        url = m_link.group(1)
        mal_id = int(m_link.group(2))
        if mal_id in seen:
            continue
        seen.add(mal_id)

        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', row)
        image_url = m_img.group(1) if m_img else ""

        # title is in a <strong> inside the second anchor (class hoverinfo_trigger fw-b)
        m_title = re.search(r'class="hoverinfo_trigger fw-b[^"]*"[^>]*>\s*<strong[^>]*>([^<]+)</strong>', row)
        if not m_title:
            m_title = re.search(rf'href="[^"]*/{entry_type}/\d+/[^"]*"[^>]*>\s*<strong[^>]*>([^<]+)</strong>', row)
        title = _clean(m_title.group(1)) if m_title else ""

        # extract all td contents
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        # tds[0]=image, tds[1]=title, tds[2]=type, tds[3]=eps/vols, tds[4]=score
        entry_type_str = _clean(tds[2]) if len(tds) > 2 else ""
        count_raw = _clean(tds[3]) if len(tds) > 3 else ""
        score_raw = _clean(tds[4]) if len(tds) > 4 else ""
        score = _parse_float(score_raw) if score_raw and score_raw not in ("N/A", "-") else None
        count = _parse_int(count_raw)

        if entry_type == "anime":
            results.append({
                "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
                "score": score, "type": entry_type_str,
                "episodes": count, "status": "", "season": "", "members": None,
            })
        else:
            results.append({
                "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
                "score": score, "type": entry_type_str,
                "volumes": None, "chapters": count, "status": "", "members": None,
            })
    return results


def parse_anime_search(html: str) -> List[dict]:
    return _parse_search_table(html, "anime")


def parse_manga_search(html: str) -> List[dict]:
    return _parse_search_table(html, "manga")


def parse_character_search(html: str) -> List[dict]:
    """Parse /character.php?q= search results.

    Table rows: TD0=image, TD1=name+aliases, TD2=anime appearances, TD3=manga appearances
    """
    results = []
    seen: set = set()
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL):
        row = m.group(1)
        if '/character/' not in row:
            continue
        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/character/(\d+)/[^"?#]*)"[^>]*>([^<]+)</a>', row)
        if not m_link:
            m_link = re.search(r'href="(/character/(\d+)/[^"?#]*)"[^>]*>([^<]+)</a>', row)
            if not m_link:
                continue
            url = BASE_URL + m_link.group(1)
            mal_id = int(m_link.group(2))
            name = _clean(m_link.group(3))
        else:
            url = m_link.group(1)
            mal_id = int(m_link.group(2))
            name = _clean(m_link.group(3))
        if mal_id in seen:
            continue
        seen.add(mal_id)
        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', row)
        image_url = m_img.group(1) if m_img else ""
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        anime_links = re.findall(r'href="[^"]*?/anime/\d+', tds[2]) if len(tds) > 2 else []
        manga_links = re.findall(r'href="[^"]*?/manga/\d+', tds[3]) if len(tds) > 3 else []
        favorites = 0
        m_fav = re.search(r'([\d,]+)\s*favorites?', row, re.I)
        if m_fav:
            favorites = _parse_int(m_fav.group(1)) or 0
        results.append({
            "mal_id": mal_id, "name": name, "url": url, "image_url": image_url,
            "anime_count": len(anime_links), "manga_count": len(manga_links), "favorites": favorites,
        })
    return results


def parse_people_search(html: str) -> List[dict]:
    """Parse /people.php?q= search results.

    Each person block spans multiple <tr> rows. We identify the person from the
    first row that has their profile image with alt="Last, First" and a /people/ID/ URL.
    """
    results = []
    seen: set = set()
    for m in re.finditer(
        r'<a[^>]+href="(?:https?://myanimelist\.net)?/people/(\d+)/([^"?#]*)"[^>]*>\s*'
        r'<img[^>]+(?:data-src|src)="([^"]+)"[^>]+alt="([^"]*)"',
        html,
    ):
        mal_id = int(m.group(1))
        if mal_id in seen:
            continue
        seen.add(mal_id)
        url = f"{BASE_URL}/people/{m.group(1)}/{m.group(2)}"
        image_url = m.group(3)
        name = _clean(m.group(4)) or m.group(2).replace("_", " ")
        results.append({"mal_id": mal_id, "name": name, "url": url, "image_url": image_url})
    return results


# ---------------------------------------------------------------------------
# Top anime / manga listings
# ---------------------------------------------------------------------------

def parse_top_anime(html: str) -> List[dict]:
    results = []
    for m in re.finditer(
        r'<tr[^>]*class="[^"]*ranking-list[^"]*"[^>]*>(.*?)</tr>',
        html, re.DOTALL
    ):
        row = m.group(1)

        m_link = re.search(
            r'<a[^>]+href="(https?://myanimelist\.net/anime/(\d+)/([^"?#]+))"[^>]*class="[^"]*hoverinfo_trigger[^"]*"',
            row
        )
        if not m_link:
            m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/anime/(\d+)/([^"?#]+))"', row)
        if not m_link:
            continue
        url = m_link.group(1)
        mal_id = int(m_link.group(2))

        m_title = re.search(r'<h3[^>]*class="[^"]*anime_ranking_h3[^"]*"[^>]*>\s*<a[^>]*>([^<]+)</a>', row)
        if not m_title:
            m_title = re.search(r'<a[^>]+href="[^"]*anime/\d+[^"]*"[^>]*>([^<]+)</a>', row)
        title = _clean(m_title.group(1)) if m_title else ""

        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', row)
        image_url = m_img.group(1) if m_img else ""

        m_info = re.search(r'<div[^>]*class="[^"]*information[^"]*"[^>]*>(.*?)</div>', row, re.DOTALL)
        info_text = _clean(m_info.group(1)) if m_info else ""
        anime_type = ""
        episodes = None
        members = None

        m_type = re.search(r'(TV|Movie|OVA|ONA|Special|Music|Manga|Novel)[^(]*\((\d+)\s*ep', info_text, re.I)
        if m_type:
            anime_type = m_type.group(1)
            episodes = int(m_type.group(2))
        else:
            m_type2 = re.search(r'(TV|Movie|OVA|ONA|Special|Music)', info_text, re.I)
            if m_type2:
                anime_type = m_type2.group(1)

        m_mem = re.search(r'([\d,]+)\s*members', info_text, re.I)
        if m_mem:
            members = _parse_int(m_mem.group(1))

        score = None
        m_score = re.search(r'<span[^>]*class="[^"]*score-label[^"]*"[^>]*>([\d.N/A]+)</span>', row)
        if m_score and m_score.group(1) != "N/A":
            score = _parse_float(m_score.group(1))

        results.append({
            "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
            "score": score, "type": anime_type, "episodes": episodes,
            "status": "", "season": "", "members": members,
        })
    return results


def parse_top_manga(html: str) -> List[dict]:
    results = []
    for m in re.finditer(r'<tr[^>]*class="[^"]*ranking-list[^"]*"[^>]*>(.*?)</tr>', html, re.DOTALL):
        row = m.group(1)

        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/manga/(\d+)/[^"?#]+)"', row)
        if not m_link:
            continue
        url = m_link.group(1)
        mal_id = int(m_link.group(2))

        m_title = re.search(r'<h3[^>]*class="[^"]*anime_ranking_h3[^"]*"[^>]*>\s*<a[^>]*>([^<]+)</a>', row)
        if not m_title:
            m_title = re.search(r'<a[^>]+href="[^"]*manga/\d+[^"]*"[^>]*>([^<]+)</a>', row)
        title = _clean(m_title.group(1)) if m_title else ""

        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', row)
        image_url = m_img.group(1) if m_img else ""

        m_info = re.search(r'<div[^>]*class="[^"]*information[^"]*"[^>]*>(.*?)</div>', row, re.DOTALL)
        info_text = _clean(m_info.group(1)) if m_info else ""

        manga_type = ""
        volumes = None
        chapters = None
        members = None
        m_t = re.search(r'(Manga|Novel|One-shot|Doujinshi|Manhwa|Manhua|Light Novel)', info_text, re.I)
        if m_t:
            manga_type = m_t.group(1)
        m_v = re.search(r'(\d+)\s*vol', info_text, re.I)
        if m_v:
            volumes = int(m_v.group(1))
        m_ch = re.search(r'(\d+)\s*ch', info_text, re.I)
        if m_ch:
            chapters = int(m_ch.group(1))
        m_mem = re.search(r'([\d,]+)\s*members', info_text, re.I)
        if m_mem:
            members = _parse_int(m_mem.group(1))

        score = None
        m_score = re.search(r'<span[^>]*class="[^"]*score-label[^"]*"[^>]*>([\d.N/A]+)</span>', row)
        if m_score and m_score.group(1) != "N/A":
            score = _parse_float(m_score.group(1))

        results.append({
            "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
            "score": score, "type": manga_type, "volumes": volumes, "chapters": chapters,
            "status": "", "members": members,
        })
    return results


# ---------------------------------------------------------------------------
# Seasonal anime
# ---------------------------------------------------------------------------

def parse_seasonal_anime(html: str) -> List[dict]:
    results = []
    seen: set = set()

    for m in re.finditer(
        r'<div[^>]*class="[^"]*seasonal-anime[^"]+js-anime-category-producer[^"]*"[^>]*data-genre="[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
        html, re.DOTALL
    ):
        block = m.group(1)

        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/anime/(\d+)/[^"?#]+)"', block)
        if not m_link:
            continue
        url = m_link.group(1)
        mal_id = int(m_link.group(2))
        if mal_id in seen:
            continue
        seen.add(mal_id)

        m_title = re.search(r'<p[^>]*class="[^"]*title-name[^"]*"[^>]*>\s*<strong[^>]*>([^<]+)</strong>', block)
        if not m_title:
            m_title = re.search(r'<a[^>]+href="[^"]*anime/\d+[^"]*"[^>]*>([^<]+)</a>', block)
        title = _clean(m_title.group(1)) if m_title else ""

        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', block)
        image_url = m_img.group(1) if m_img else ""

        m_type = re.search(r'<span[^>]*class="[^"]*fal[^"]*"[^>]*>.*?</span>\s*([^\s<]+)', block, re.DOTALL)
        anime_type = _clean(m_type.group(1)) if m_type else ""

        m_source = re.search(r'<span[^>]*class="[^"]*source[^"]*"[^>]*>([^<]+)</span>', block)
        source = _clean(m_source.group(1)) if m_source else ""

        m_eps = re.search(r'(\d+)\s*ep', block, re.I)
        episodes = int(m_eps.group(1)) if m_eps else None

        m_prodsrc2 = re.search(r'<div[^>]*class="prodsrc"[^>]*>(.*?)</div>', block, re.DOTALL)
        prodsrc_block2 = m_prodsrc2.group(1) if m_prodsrc2 else block
        studios = re.findall(r'<a[^>]+href="[^"]*anime/producer/[^"]*"[^>]*>([^<]+)</a>', prodsrc_block2)
        studios = [_clean(s) for s in studios]

        m_genres_div2 = re.search(r'<div[^>]*class="genres[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        genres_block2 = m_genres_div2.group(1) if m_genres_div2 else ""
        genres = re.findall(r'<a[^>]+href="[^"]*anime/genre/[^"]*"[^>]*>([^<]+)</a>', genres_block2)
        genres = [_clean(g) for g in genres]

        m_score = re.search(r'<span[^>]*class="[^"]*score[^"]*"[^>]*>\s*([\d.N/A]+)\s*</span>', block)
        score = _parse_float(m_score.group(1)) if m_score and m_score.group(1) != "N/A" else None

        m_mem = re.search(r'<span[^>]*class="[^"]*member[^"]*"[^>]*>\s*([\d,]+)', block)
        members = _parse_int(m_mem.group(1)) if m_mem else None

        m_syn = re.search(r'<p[^>]*class="[^"]*preline[^"]*"[^>]*>([^<]+)</p>', block)
        synopsis = _clean(m_syn.group(1)) if m_syn else ""

        results.append({
            "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
            "type": anime_type, "source": source, "episodes": episodes,
            "studios": studios, "genres": genres, "score": score,
            "members": members, "synopsis": synopsis,
        })
    return results


# ---------------------------------------------------------------------------
# User profile page
# ---------------------------------------------------------------------------

def parse_user_profile(html: str, username: str) -> dict:
    url = f"{BASE_URL}/profile/{username}"

    m_img = re.search(r'<img[^>]+class="[^"]*user-image[^"]*"[^>]+src="([^"]+)"', html)
    if not m_img:
        m_img = re.search(r'<div[^>]*class="[^"]*user-image[^"]*"[^>]*>.*?<img[^>]+src="([^"]+)"', html, re.DOTALL)
    image_url = m_img.group(1) if m_img else ""

    # About
    m_about = re.search(r'<div[^>]*class="[^"]*profile-about[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    about = _clean(m_about.group(1))[:1000] if m_about else ""

    # Sidebar profile fields
    last_online = _profile_field(html, "Last Online")
    gender = _profile_field(html, "Gender")
    birthday = _profile_field(html, "Birthday")
    location = _profile_field(html, "Location")
    website = _profile_field(html, "Website")
    joined = _profile_field(html, "Joined")

    anime_stats = _parse_user_anime_stats(html)
    manga_stats = _parse_user_manga_stats(html)
    favorites = _parse_user_favorites(html)

    return {
        "username": username, "url": url, "image_url": image_url, "about": about,
        "last_online": last_online, "gender": gender, "birthday": birthday,
        "location": location, "website": website, "joined": joined,
        "anime_stats": anime_stats, "manga_stats": manga_stats, "favorites": favorites,
    }


def _profile_field(html: str, label: str) -> str:
    m = re.search(
        rf'<span[^>]*class="[^"]*user-status-title[^"]*"[^>]*>{re.escape(label)}</span>\s*<span[^>]*class="[^"]*user-status-data[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.I
    )
    return _clean(m.group(1)) if m else ""


def _parse_user_stats_block(html: str, section_label: str) -> dict:
    """Shared stat parser for Anime Stats and Manga Stats sections.

    Stats live in a ul.stats-status with li items:
      <a class="... watching">Watching</a><span>COUNT</span>
    Days/Mean Score in a div.stat-score with span text.
    """
    m = re.search(
        rf'<h5[^>]*>.*?{re.escape(section_label)}.*?</h5>(.*?)(?=<h5|$)',
        html, re.DOTALL | re.I,
    )
    if not m:
        return {}
    block = m.group(1)

    def _li_stat(label: str) -> int:
        mm = re.search(
            rf'class="[^"]*{re.escape(label.lower().replace(" ", "_").replace("-", "_"))}"[^>]*>'
            rf'{re.escape(label)}</a>\s*<span[^>]*>([\d,]+)</span>',
            block, re.I,
        )
        if not mm:
            mm = re.search(rf'>{re.escape(label)}</a>\s*<span[^>]*>([\d,]+)</span>', block, re.I)
        if not mm:
            # "Total Entries" / "Rewatched" / "Episodes" rows are plain
            # <span>label</span><span>count</span> pairs, not anchors.
            mm = re.search(rf'>{re.escape(label)}</span>\s*<span[^>]*>([\d,]+)</span>', block, re.I)
        return _parse_int(mm.group(1)) or 0 if mm else 0

    def _score_stat(label: str) -> float:
        mm = re.search(rf'{re.escape(label)}[:\s]*</span>\s*<span[^>]*>([\d.]+)</span>', block, re.I)
        if not mm:
            mm = re.search(rf'{re.escape(label)}[:\s]*([\d.]+)', block, re.I)
        return float(mm.group(1)) if mm else 0.0

    def _days_stat() -> float:
        mm = re.search(r'Days:\s*</span>\s*([\d.]+)', block, re.I)
        if not mm:
            mm = re.search(r'Days[:\s]*([\d.]+)', block, re.I)
        return float(mm.group(1)) if mm else 0.0

    if "Anime" in section_label:
        return {
            "watching": _li_stat("Watching"),
            "completed": _li_stat("Completed"),
            "on_hold": _li_stat("On-Hold"),
            "dropped": _li_stat("Dropped"),
            "plan_to_watch": _li_stat("Plan to Watch"),
            "total_entries": _li_stat("Total Entries"),
            "days_watched": _days_stat(),
            "mean_score": _score_stat("Mean Score"),
        }
    return {
        "reading": _li_stat("Reading"),
        "completed": _li_stat("Completed"),
        "on_hold": _li_stat("On-Hold"),
        "dropped": _li_stat("Dropped"),
        "plan_to_read": _li_stat("Plan to Read"),
        "total_entries": _li_stat("Total Entries"),
        "days_read": _days_stat(),
        "mean_score": _score_stat("Mean Score"),
    }


def _parse_user_anime_stats(html: str) -> dict:
    return _parse_user_stats_block(html, "Anime Stats")


def _parse_user_manga_stats(html: str) -> dict:
    return _parse_user_stats_block(html, "Manga Stats")


def _parse_user_favorites(html: str) -> dict:
    fav: dict = {"anime": [], "manga": [], "characters": [], "people": []}

    def _parse_fav_section(section_id: str, path_part: str) -> list:
        m = re.search(
            rf'<div[^>]*id="{section_id}"[^>]*>(.*?)(?=<div[^>]*id="[a-z_]+_favorites"|<div[^>]*class="[^"]*profile-stat|$)',
            html, re.DOTALL | re.I,
        )
        if not m:
            return []
        block = m.group(1)
        items = []
        seen: set = set()
        for mm in re.finditer(
            rf'<li[^>]*title="([^"]*)"[^>]*>\s*<a[^>]+href="(https?://myanimelist\.net/{path_part}/(\d+)/[^"]*)"',
            block,
        ):
            title = _clean(mm.group(1))
            url = mm.group(2)
            mid = int(mm.group(3))
            if mid in seen:
                continue
            seen.add(mid)
            m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', block[mm.start():mm.start()+500])
            items.append({
                "mal_id": mid, "title": title, "url": url,
                "image_url": m_img.group(1) if m_img else "",
                "type": "", "start_year": None,
            })
        return items

    fav["anime"] = _parse_fav_section("anime_favorites", "anime")
    fav["manga"] = _parse_fav_section("manga_favorites", "manga")
    # characters and people: title attribute has "Name"
    for char_m in re.finditer(
        r'id="character_favorites"[^>]*>(.*?)(?=<div[^>]*id="[a-z_]+_favorites"|<div[^>]*class="[^"]*profile-stat|$)',
        html, re.DOTALL | re.I,
    ):
        block = char_m.group(1)
        # character favorite links are relative (/character/{id}/{slug})
        for mm in re.finditer(
            r'<li[^>]*title="([^"]*)"[^>]*>\s*<a[^>]+href="(?:https?://myanimelist\.net)?(/character/(\d+)/[^"]*)"',
            block,
        ):
            item_html = block[mm.start():mm.start() + 700]
            m_anime = re.search(r'<span[^>]*class="[^"]*users[^"]*"[^>]*>([^<]+)</span>', item_html)
            m_img = re.search(r'<img[^>]+data-src="([^"]+)"', item_html)
            fav["characters"].append({
                "mal_id": int(mm.group(3)), "name": _clean(mm.group(1)),
                "url": f"{BASE_URL}{mm.group(2)}",
                "image_url": m_img.group(1) if m_img else "",
                "anime_title": _clean(m_anime.group(1)) if m_anime else "", "anime_url": "",
            })
    for ppl_m in re.finditer(
        r'id="person_favorites"[^>]*>(.*?)(?=<div[^>]*id="[a-z_]+_favorites"|<div[^>]*class="[^"]*profile-stat|$)',
        html, re.DOTALL | re.I,
    ):
        block = ppl_m.group(1)
        # people favorite links are relative (/people/{id}/{slug})
        for mm in re.finditer(
            r'<li[^>]*title="([^"]*)"[^>]*>\s*<a[^>]+href="(?:https?://myanimelist\.net)?(/people/(\d+)/[^"]*)"',
            block,
        ):
            item_html = block[mm.start():mm.start() + 700]
            m_img = re.search(r'<img[^>]+data-src="([^"]+)"', item_html)
            fav["people"].append({
                "mal_id": int(mm.group(3)), "name": _clean(mm.group(1)),
                "url": f"{BASE_URL}{mm.group(2)}",
                "image_url": m_img.group(1) if m_img else "",
            })
    return fav


# ---------------------------------------------------------------------------
# User anime/manga list JSON
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------

def parse_last_page(html: str) -> int:
    """Return the highest page number found in pagination links, or 1.

    MAL genre/producer pages use &page=N; top-list pages use &limit=N (offset).
    Both are detected here.
    """
    # genre / producer pages: &page=N or &amp;page=N
    page_nums = re.findall(r'[&?](?:amp;)?page=(\d+)', html)
    if page_nums:
        return max(int(n) for n in page_nums)
    # top-list pages: ?p=N (p is a positional offset, not a page number — not useful here)
    return 1


# ---------------------------------------------------------------------------
# Anime stats page  (/anime/{id}/stats)
# ---------------------------------------------------------------------------

def parse_anime_stats_page(html: str) -> dict:
    scores: Dict[int, int] = {}
    for m in re.finditer(
        r'<span[^>]*class="[^"]*score-label[^"]*"[^>]*>(\d+)</span>.*?'
        r'<span[^>]*class="[^"]*score-votes[^"]*"[^>]*>([\d,]+)',
        html, re.DOTALL,
    ):
        scores[int(m.group(1))] = _parse_int(m.group(2)) or 0

    if not scores:
        for m in re.finditer(
            r'<td[^>]*>(\d+)</td>.*?<small[^>]*>\(([\d,]+)\s*votes?\)',
            html, re.DOTALL,
        ):
            v = int(m.group(1))
            if 1 <= v <= 10:
                scores[v] = _parse_int(m.group(2)) or 0

    def _status_count(label: str) -> int:
        mm = re.search(
            rf'<span[^>]*class="[^"]*(?:dark_text|label)[^"]*"[^>]*>\s*{re.escape(label)}\s*</span>\s*'
            rf'<span[^>]*>([\d,]+)</span>',
            html, re.I,
        )
        if not mm:
            mm = re.search(rf'{re.escape(label)}</td>\s*<td[^>]*>([\d,]+)', html, re.I)
        return _parse_int(mm.group(1)) or 0 if mm else 0

    return {
        "scores": {i: scores.get(i, 0) for i in range(1, 11)},
        "watching": _status_count("Watching"),
        "completed": _status_count("Completed"),
        "on_hold": _status_count("On-Hold"),
        "dropped": _status_count("Dropped"),
        "plan_to_watch": _status_count("Plan to Watch"),
    }


# ---------------------------------------------------------------------------
# Pictures pages  (/anime/{id}/pics, /manga/{id}/pics, etc.)
# ---------------------------------------------------------------------------

def parse_pictures_page(html: str) -> List[str]:
    """Return all full-size image URLs from a /pics page."""
    urls = []
    seen: set = set()
    for m in re.finditer(r'<a[^>]+href="(https?://cdn\.myanimelist\.net/images/[^"]+\.(?:jpg|jpeg|png|webp))"', html, re.I):
        u = m.group(1)
        if u not in seen:
            seen.add(u)
            urls.append(u)
    if not urls:
        for m in re.finditer(r'<img[^>]+src="(https?://cdn\.myanimelist\.net/images/[^"]+\.(?:jpg|jpeg|png|webp))"', html, re.I):
            u = m.group(1)
            if u not in seen:
                seen.add(u)
                urls.append(u)
    return urls


# ---------------------------------------------------------------------------
# Videos page  (/anime/{id}/video)
# ---------------------------------------------------------------------------

def parse_videos_page(html: str) -> List[dict]:
    results = []
    for m in re.finditer(
        r'<div[^>]*class="[^"]*video-block[^"]*"[^>]*>(.*?)</div\s*>',
        html, re.DOTALL,
    ):
        block = m.group(1)
        m_link = re.search(r'<a[^>]+href="([^"]+)"', block)
        m_thumb = re.search(r'<img[^>]+src="([^"]+)"', block)
        m_title = re.search(r'<span[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</span>', block)
        if not m_link:
            continue
        url = m_link.group(1)
        if not url.startswith("http"):
            url = f"{BASE_URL}{url}"
        title = _clean(m_title.group(1)) if m_title else _clean(re.sub(r'<[^>]+>', '', block))
        thumbnail_url = m_thumb.group(1) if m_thumb else ""
        m_type = re.search(r'<span[^>]*class="[^"]*type[^"]*"[^>]*>([^<]+)</span>', block)
        video_type = _clean(m_type.group(1)) if m_type else "PV"
        results.append({"title": title, "url": url, "thumbnail_url": thumbnail_url, "video_type": video_type})

    if not results:
        for m in re.finditer(r'<div[^>]*class="[^"]*js-video[^"]*"[^>]*data-video-id="([^"]+)"[^>]*>(.*?)</div>', html, re.DOTALL):
            vid_id = m.group(1)
            block = m.group(2)
            m_title = re.search(r'(?:title|alt)="([^"]+)"', block)
            title = _clean(m_title.group(1)) if m_title else vid_id
            m_thumb = re.search(r'<img[^>]+src="([^"]+)"', block)
            thumbnail_url = m_thumb.group(1) if m_thumb else ""
            results.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "thumbnail_url": thumbnail_url,
                "video_type": "PV",
            })
    return results


# ---------------------------------------------------------------------------
# News page  (/anime/{id}/news, /manga/{id}/news)
# ---------------------------------------------------------------------------

def parse_news_page(html: str) -> List[dict]:
    results = []
    for m in re.finditer(
        r'<div[^>]*class="[^"]*news-unit[^"]*"[^>]*>(.*?)</div\s*>\s*</div\s*>',
        html, re.DOTALL,
    ):
        block = m.group(1)
        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/news/[^"]+)"[^>]*>([^<]+)</a>', block)
        if not m_link:
            continue
        url = m_link.group(1)
        title = _clean(m_link.group(2))
        m_img = re.search(r'<img[^>]+src="([^"]+)"', block)
        image_url = m_img.group(1) if m_img else ""
        m_author = re.search(r'by\s*<a[^>]+>([^<]+)</a>', block, re.I)
        author = _clean(m_author.group(1)) if m_author else ""
        m_date = re.search(r'<span[^>]*class="[^"]*date[^"]*"[^>]*>([^<]+)</span>', block)
        date = _clean(m_date.group(1)) if m_date else ""
        m_intro = re.search(r'<p[^>]*>([^<]{20,})</p>', block)
        intro = _clean(m_intro.group(1)) if m_intro else ""
        m_comments = re.search(r'(\d+)\s*comments?', block, re.I)
        comments = int(m_comments.group(1)) if m_comments else 0
        results.append({
            "title": title, "url": url, "author": author,
            "date": date, "intro": intro, "image_url": image_url, "comments": comments,
        })

    if not results:
        for m in re.finditer(
            r'<div[^>]*class="[^"]*clearfix[^"]*"[^>]*>(.*?)</div\s*>\s*</div',
            html, re.DOTALL,
        ):
            block = m.group(1)
            m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/news/\d+[^"]*)"[^>]*>([^<]+)</a>', block)
            if not m_link:
                continue
            url = m_link.group(1)
            title = _clean(m_link.group(2))
            m_author = re.search(r'by\s*<a[^>]+>([^<]+)</a>', block, re.I)
            author = _clean(m_author.group(1)) if m_author else ""
            m_date = re.search(r'<span[^>]*>(\w+ \d+, \d{4})</span>', block)
            date = _clean(m_date.group(1)) if m_date else ""
            m_intro = re.search(r'<p[^>]*>(.{20,300})</p>', block, re.DOTALL)
            intro = _clean(m_intro.group(1)) if m_intro else ""
            m_img = re.search(r'<img[^>]+src="([^"]+)"', block)
            image_url = m_img.group(1) if m_img else ""
            m_comments = re.search(r'(\d+)\s*comments?', block, re.I)
            comments = int(m_comments.group(1)) if m_comments else 0
            results.append({
                "title": title, "url": url, "author": author,
                "date": date, "intro": intro, "image_url": image_url, "comments": comments,
            })
    return results


# ---------------------------------------------------------------------------
# More info page  (/anime/{id}/moreinfo)
# ---------------------------------------------------------------------------

def parse_moreinfo_page(html: str) -> str:
    m = re.search(r'<div[^>]*class="[^"]*more-info[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.I)
    if m:
        return _clean(m.group(1))
    m = re.search(r'<p[^>]*id="[^"]*moreinfo[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL | re.I)
    if m:
        return _clean(m.group(1))
    m = re.search(r'No\s+additional\s+information', html, re.I)
    return "" if m else ""


# ---------------------------------------------------------------------------
# Producer page  (/anime/producer/{id}/{slug}?p={page})
# ---------------------------------------------------------------------------

def parse_genre_page(html: str) -> List[dict]:
    """Parse a /anime/genre/{id}/ page.

    The card grid uses class="js-anime-category-producer seasonal-anime ..."
    with hidden js-score / js-members spans and h2.h2_anime_title for the title.
    This is structurally different from both parse_top_anime and parse_seasonal_anime.
    """
    results = []
    seen: set = set()

    # Split on each card opening tag; the attribute order is stable across MAL pages
    card_starts = list(re.finditer(
        r'<div[^>]*class="[^"]*js-anime-category-producer\s+seasonal-anime[^"]*"[^>]*data-genre="([^"]*)"[^>]*>',
        html,
    ))

    for i, m_start in enumerate(card_starts):
        start = m_start.start()
        end = card_starts[i + 1].start() if i + 1 < len(card_starts) else len(html)
        block = html[start:end]

        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/anime/(\d+)/[^"?#]*)"', block)
        if not m_link:
            continue
        url = m_link.group(1)
        mal_id = int(m_link.group(2))
        if mal_id in seen:
            continue
        seen.add(mal_id)

        m_title = re.search(r'<span[^>]*class="js-title"[^>]*>([^<]+)</span>', block)
        if not m_title:
            m_title = re.search(r'<h2[^>]*class="[^"]*h2_anime_title[^"]*"[^>]*>\s*<a[^>]*>([^<]+)</a>', block)
        if not m_title:
            m_title = re.search(r'class="link-title"[^>]*>([^<]+)</a>', block)
        title = _clean(m_title.group(1)) if m_title else ""

        m_img = re.search(r'<img[^>]+(?:data-src|src)="(https?://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"', block, re.I)
        image_url = m_img.group(1) if m_img else ""

        m_score = re.search(r'<span[^>]*class="js-score"[^>]*>([\d.]+)</span>', block)
        score = _parse_float(m_score.group(1)) if m_score else None

        m_mem = re.search(r'<span[^>]*class="js-members"[^>]*>([\d,]+)</span>', block)
        members = _parse_int(m_mem.group(1)) if m_mem else None

        # type from js-anime-type-N class on the outer div (most reliable)
        _TYPE_MAP = {"1": "TV", "2": "OVA", "3": "Movie", "4": "Special", "5": "ONA", "6": "Music"}
        m_type_cls = re.search(r'js-anime-type-(\d+)', m_start.group(0))
        anime_type = _TYPE_MAP.get(m_type_cls.group(1), "") if m_type_cls else ""
        if not anime_type:
            # fallback: first item span when it's a type word (genre pages)
            m_info = re.search(r'<span[^>]*class="item"[^>]*>([A-Za-z]+[^<]*)</span>', block)
            info_text = _clean(m_info.group(1)) if m_info else ""
            m_type2 = re.match(r'([A-Za-z\-/ ]+?)(?:,\s*\d{4})?$', info_text.strip())
            anime_type = m_type2.group(1).strip() if m_type2 else ""

        m_eps = re.search(r'<span[^>]*>\s*(\d+)\s*ep', block, re.I)
        episodes = int(m_eps.group(1)) if m_eps else None

        m_status = re.search(r'<span[^>]*class="item\s+([^"]+)"[^>]*>', block)
        status = _clean(m_status.group(1)).replace("-", " ").title() if m_status else ""

        # restrict to dedicated divs to avoid capturing pagination links on the last card
        m_prodsrc = re.search(r'<div[^>]*class="prodsrc"[^>]*>(.*?)</div>', block, re.DOTALL)
        prodsrc_block = m_prodsrc.group(1) if m_prodsrc else ""
        studios = re.findall(r'<a[^>]+href="[^"]*anime/producer/[^"]*"[^>]*>([^<]+)</a>', prodsrc_block)
        studios = [_clean(s) for s in studios]

        m_genres_div = re.search(r'<div[^>]*class="genres[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        genres_block = m_genres_div.group(1) if m_genres_div else ""
        genres = re.findall(r'<a[^>]+href="[^"]*anime/genre/[^"]*"[^>]*>([^<]+)</a>', genres_block)
        genres = [_clean(g) for g in genres]

        m_syn = re.search(r'<p[^>]*class="[^"]*preline[^"]*"[^>]*>([^<]+)</p>', block)
        synopsis = _clean(m_syn.group(1)) if m_syn else ""

        results.append({
            "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
            "score": score, "type": anime_type, "episodes": episodes,
            "status": status, "season": "", "members": members,
            "studios": studios, "genres": genres, "synopsis": synopsis,
        })
    return results


def parse_manga_genre_page(html: str) -> List[dict]:
    """Parse a /manga/genre/{id}/ or /manga/magazine/{id}/ card grid page.

    Cards use class="seasonal-anime js-seasonal-anime" — structurally
    different from both the anime genre grid and the classic topmanga table.
    """
    results = []
    seen: set = set()

    card_starts = list(re.finditer(r'<div class="seasonal-anime js-seasonal-anime"[^>]*>', html))
    for i, m_start in enumerate(card_starts):
        start = m_start.start()
        end = card_starts[i + 1].start() if i + 1 < len(card_starts) else len(html)
        block = html[start:end]

        m_link = re.search(r'<a[^>]+href="(https?://myanimelist\.net/manga/(\d+)/[^"?#]*)"', block)
        if not m_link:
            continue
        url = m_link.group(1)
        mal_id = int(m_link.group(2))
        if mal_id in seen:
            continue
        seen.add(mal_id)

        m_title = re.search(r'<h2[^>]*class="h2_manga_title"[^>]*>\s*<a[^>]*>([^<]+)</a>', block)
        title = _clean(m_title.group(1)) if m_title else ""

        m_img = re.search(r'<img[^>]+(?:data-src|src)="([^"]+)"', block)
        image_url = m_img.group(1) if m_img else ""

        m_info = re.search(r'<span class="item">([^<]+)</span>', block)
        info_text = _clean(m_info.group(1)) if m_info else ""
        manga_type = info_text.split(",")[0].strip() if info_text else ""

        m_status = re.search(r'<span class="item ([a-z]+)"', block)
        status = _clean(m_status.group(1)).replace("-", " ").title() if m_status else ""

        m_vol = re.search(r'<span class="volume js-volume">([^<]*)</span>', block)
        volumes = _parse_int(m_vol.group(1)) if m_vol else None
        m_chp = re.search(r'<span class="chapter js-chapter">([^<]*)</span>', block)
        chapters = _parse_int(m_chp.group(1)) if m_chp else None

        m_genres_div = re.search(r'<div[^>]*class="genres[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        genres_block = m_genres_div.group(1) if m_genres_div else ""
        genres = [_clean(g) for g in re.findall(r'<a[^>]+href="[^"]*manga/genre/[^"]*"[^>]*>([^<]+)</a>', genres_block)]

        m_syn = re.search(r'<p[^>]*class="[^"]*preline[^"]*"[^>]*>([^<]+)</p>', block)
        synopsis = _clean(m_syn.group(1)) if m_syn else ""

        results.append({
            "mal_id": mal_id, "title": title, "url": url, "image_url": image_url,
            "score": None, "type": manga_type, "volumes": volumes, "chapters": chapters,
            "status": status, "members": None, "genres": genres, "synopsis": synopsis,
        })
    return results


def parse_producer_page(html: str) -> List[dict]:
    """Producer pages use the same card grid as genre pages."""
    results = parse_genre_page(html)
    if not results:
        results = parse_top_anime(html)
    return results


# ---------------------------------------------------------------------------
# Magazine page  (/manga/magazine/{id}/{slug}?p={page})
# ---------------------------------------------------------------------------

def parse_magazine_page(html: str) -> List[dict]:
    """Magazine pages use the same card grid as manga genre pages."""
    results = parse_manga_genre_page(html)
    if not results:
        results = parse_top_manga(html)
    if not results:
        results = parse_manga_search(html)
    return results


# ---------------------------------------------------------------------------
# Global reviews  (/reviews.php?t=anime|manga&p={page})
# ---------------------------------------------------------------------------

def parse_global_reviews(html: str) -> List[dict]:
    return parse_reviews_page(html)


# ---------------------------------------------------------------------------
# Global recommendations  (/recommendations.php?s=recentrecs&t=anime&p={page})
# ---------------------------------------------------------------------------

def parse_global_recommendations(html: str) -> List[dict]:
    results = []
    for m in re.finditer(
        r'<div[^>]*class="[^"]*borderClass[^"]*"[^>]*>(.*?)</div\s*>\s*(?=<div[^>]*class="[^"]*borderClass|$)',
        html, re.DOTALL,
    ):
        block = m.group(1)
        links = re.findall(r'<a[^>]+href="(https?://myanimelist\.net/(?:anime|manga)/(\d+)/[^"]*)"[^>]*>([^<]+)</a>', block)
        if len(links) < 2:
            continue
        src_url, src_id, src_title = links[0]
        rec_url, rec_id, rec_title = links[1]
        m_user = re.search(r'<a[^>]+href="/profile/[^"]*"[^>]*>([^<]+)</a>', block)
        username = _clean(m_user.group(1)) if m_user else ""
        m_text = re.search(r'<div[^>]*class="[^"]*text[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        text = _clean(m_text.group(1)) if m_text else ""
        results.append({
            "source_id": int(src_id), "source_title": _clean(src_title), "source_url": src_url,
            "rec_id": int(rec_id), "rec_title": _clean(rec_title), "rec_url": rec_url,
            "username": username, "text": text,
        })
    return results


def parse_anime_list_json(data: list) -> List[dict]:
    results = []
    for item in data:
        mal_id = item.get("anime_id") or item.get("series_animedb_id", 0)
        title = item.get("anime_title") or item.get("series_title", "")
        score = item.get("score") or None
        status = item.get("status", 0)
        episodes_watched = item.get("num_watched_episodes") or item.get("my_watched_episodes", 0)
        total_episodes = item.get("anime_num_episodes") or item.get("series_episodes") or None
        image_url = item.get("anime_image_path") or item.get("series_image", "")
        url = item.get("anime_url", "")
        if url and not url.startswith("http"):
            url = f"{BASE_URL}{url}"
        if not url and mal_id:
            url = f"{BASE_URL}/anime/{mal_id}"
        results.append({
            "mal_id": mal_id, "title": title, "score": score, "status": status,
            "episodes_watched": episodes_watched, "total_episodes": total_episodes,
            "image_url": image_url, "url": url,
        })
    return results


def parse_manga_list_json(data: list) -> List[dict]:
    results = []
    for item in data:
        mal_id = item.get("manga_id") or item.get("series_mangadb_id", 0)
        title = item.get("manga_title") or item.get("series_title", "")
        score = item.get("score") or None
        status = item.get("status", 0)
        chapters_read = item.get("num_read_chapters") or item.get("my_read_chapters", 0)
        total_chapters = item.get("manga_num_chapters") or item.get("series_chapters") or None
        volumes_read = item.get("num_read_volumes") or item.get("my_read_volumes", 0)
        total_volumes = item.get("manga_num_volumes") or item.get("series_volumes") or None
        image_url = item.get("manga_image_path") or item.get("series_image", "")
        url = item.get("manga_url", "")
        if url and not url.startswith("http"):
            url = f"{BASE_URL}{url}"
        if not url and mal_id:
            url = f"{BASE_URL}/manga/{mal_id}"
        results.append({
            "mal_id": mal_id, "title": title, "score": score, "status": status,
            "chapters_read": chapters_read, "total_chapters": total_chapters,
            "volumes_read": volumes_read, "total_volumes": total_volumes,
            "image_url": image_url, "url": url,
        })
    return results
