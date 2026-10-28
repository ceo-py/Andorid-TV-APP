"""DLHD (DaddyLiveHD) channel catalog + EPG mappings.

``dlhd-channels.json`` is a flat list of the streams the DLHD site carries::

    [{"letter": "A", "name": "AMC USA", "id": "303",
      "watchUrl": "https://dlive.sx/watch.php?id=303"}, ...]

This module turns that into the same shape as
``tv_channels.ALL_CHANNELS_NOT_SORTED`` so the daily EPG pipeline can treat
DLHD channels like any other catalog entry::

    {
        "Movie": {
            "AMC USA": {
                "url": ["https://dlive.sx/watch.php?id=303"],
                "url_hd": "",
                "image": "",
                "epg_id": "AMC+.us2",
                "epg_source": "US2",
            },
        },
    }

Two things make this work:

*   ``dlhd_epg_mapping.json`` — a generated, hand-auditable table of
    ``name -> {epg_id, epg_source}``. It was produced by
    ``tools/build_dlhd_mapping.py`` and checked by hand; it is the authority
    for which DLHD channel maps to which XMLTV channel. Channels *not* in
    the table get ``epg_excluded: True`` so the fuzzy matcher never guesses
    a wrong answer for them (the DLHD names contain many near-collisions
    like "TNT USA" vs "TNT Brasil" that a fuzzy matcher gets wrong).

*   Category inference. DLHD exposes no genre metadata, so the category is
    derived from the channel name with the keyword table in
    ``_CATEGORY_RULES``. Anything unrecognised lands in ``Worldwide``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional

THIS_DIR = Path(__file__).resolve().parent
CHANNELS_JSON = THIS_DIR / "dlhd-channels.json"
MAPPING_JSON = THIS_DIR / "dlhd_epg_mapping.json"

# Categories used by the rest of the catalog. Keep in sync with
# ``tv_channels.ALL_CHANNELS_NOT_SORTED``'s keys.
CATEGORIES = ("Sport", "Movie", "Science", "News", "Kids", "Music", "Worldwide")

# Keyword -> category. Checked in order, so put the most specific first:
# "super sport" must win over "sport", "music tv" over "tv", etc.
_CATEGORY_RULES: tuple[tuple[str, str], ...] = (
    # --- Sport -------------------------------------------------------
    ("super sport", "Sport"),
    ("supersport", "Sport"),
    ("astro cricket", "Sport"),
    ("sportsnet", "Sport"),
    ("sport tv", "Sport"),
    ("sports", "Sport"),
    ("sport", "Sport"),
    ("arena", "Sport"),
    ("dazn", "Sport"),
    ("espn", "Sport"),
    ("beIN sports", "Sport"),
    ("bein sports", "Sport"),
    ("tnt sports", "Sport"),
    ("nba", "Sport"),
    ("nhl", "Sport"),
    ("fifa", "Sport"),
    ("formula 1", "Sport"),
    ("motogp", "Sport"),
    ("grand prix", "Sport"),
    ("football", "Sport"),
    ("futbol", "Sport"),
    ("tennis", "Sport"),
    ("tenis", "Sport"),
    ("golf", "Sport"),
    ("rugby", "Sport"),
    ("cricket", "Sport"),
    ("boxing", "Sport"),
    ("wrestling", "Sport"),
    ("horse racing", "Sport"),
    ("darts", "Sport"),
    ("snooker", "Sport"),
    ("athletics", "Sport"),
    ("olympic", "Sport"),
    ("swimming", "Sport"),
    ("volleyball", "Sport"),
    ("basketball", "Sport"),
    ("ice hockey", "Sport"),
    ("hockey", "Sport"),
    ("baseball", "Sport"),
    ("motorsport", "Sport"),
    ("racing", "Sport"),
    ("speedway", "Sport"),
    ("rally", "Sport"),
    ("skate", "Sport"),
    ("surf", "Sport"),
    ("cycling", "Sport"),
    ("league", "Sport"),
    ("liga", "Sport"),
    ("bundesliga", "Sport"),
    ("serie a", "Sport"),
    ("ligue 1", "Sport"),
    ("eredivisie", "Sport"),
    ("premier league", "Sport"),
    ("champions league", "Sport"),
    ("world cup", "Sport"),
    ("kriket", "Sport"),
    ("tenis", "Sport"),
    ("gimnastika", "Sport"),
    ("soccer", "Sport"),
    ("baloncentro", "Sport"),
    ("baloncesto", "Sport"),
    ("basquete", "Sport"),
    ("mlb", "Sport"),
    ("nfl", "Sport"),
    ("wwe", "Sport"),
    ("mma", "Sport"),
    ("ufc", "Sport"),
    ("boxe", "Sport"),
    ("badminton", "Sport"),
    ("ski", "Sport"),
    ("snow", "Sport"),
    ("biathlon", "Sport"),
    ("climbing", "Sport"),
    ("cycling", "Sport"),
    ("kayak", "Sport"),
    ("sailing", "Sport"),
    # --- Kids --------------------------------------------------------
    ("kids", "Kids"),
    ("junior", "Kids"),
    ("cartoon", "Kids"),
    ("nickelodeon", "Kids"),
    ("nick jr", "Kids"),
    ("disney", "Kids"),
    ("boomerang", "Kids"),
    ("baby tv", "Kids"),
    ("toon", "Kids"),
    ("jetix", "Kids"),
    ("kix", "Kids"),
    ("minimax", "Kids"),
    ("sprout", "Kids"),
    ("sesame", "Kids"),
    ("puzzle", "Kids"),
    ("jim jam", "Kids"),
    ("paolino", "Kids"),
    ("mickey", "Kids"),
    ("looney", "Kids"),
    ("tom and jerry", "Kids"),
    ("yu yu", "Kids"),
    # --- Movie -------------------------------------------------------
    # "cinema" / "movie" before the music rules below, otherwise
    # "Sky Cinema Romance" lands in Music.
    ("cinema", "Movie"),
    ("cinemania", "Movie"),
    ("movie", "Movie"),
    ("movies", "Movie"),
    ("film", "Movie"),
    ("kino", "Movie"),
    ("cinemax", "Movie"),
    ("4k", "Movie"),
    ("paramount", "Movie"),
    ("mgm", "Movie"),
    ("epic drama", "Movie"),
    ("star channel", "Movie"),
    ("star life", "Movie"),
    ("star crime", "Movie"),
    ("tele", "Movie"),
    # --- Music -------------------------------------------------------
    ("music", "Music"),
    ("radio", "Music"),
    ("mtv", "Music"),
    ("rock", "Music"),
    ("pop", "Music"),
    ("country", "Music"),
    ("jazz", "Music"),
    ("blues", "Music"),
    ("folk", "Music"),
    ("hits", "Music"),
    ("party", "Music"),
    ("romance", "Music"),
    ("classic", "Music"),
    ("metal", "Music"),
    ("k-love", "Music"),
    ("zmusic", "Music"),
    ("muziek", "Music"),
    ("música", "Music"),
    ("musica", "Music"),
    ("top music", "Music"),
    ("dance", "Music"),
    ("retro music", "Music"),
    ("vh1", "Music"),
    ("song", "Music"),
    ("clips", "Music"),
    # --- Science -----------------------------------------------------
    ("discovery", "Science"),
    ("national geographic", "Science"),
    ("nat geo", "Science"),
    ("history", "Science"),
    ("animal planet", "Science"),
    ("nat geo wild", "Science"),
    ("science", "Science"),
    ("cosmos", "Science"),
    ("curiosity", "Science"),
    ("wild", "Science"),
    ("planet", "Science"),
    ("earth", "Science"),
    ("zoo", "Science"),
    ("travel", "Science"),
    ("food network", "Science"),
    ("cooking", "Science"),
    # --- News --------------------------------------------------------
    ("news", "News"),
    ("cnn", "News"),
    ("world news", "News"),
    ("euronews", "News"),
    ("france 24", "News"),
    ("al jazeera", "News"),
    ("aljazeera", "News"),
    ("arabiya", "News"),
    ("arabic news", "News"),
    ("al iraqiya", "News"),
    ("sky news", "News"),
    ("nbc", "News"),
    ("cbs", "News"),
    ("abc", "News"),
    ("cbc", "News"),
    ("tvn", "News"),
    ("rtp", "News"),
    ("rtv", "News"),
    ("ert", "News"),
    ("ntv", "News"),
    ("tvp", "News"),
    ("rtl", "News"),
    ("trt haber", "News"),
    ("sbt", "News"),
    ("globo", "News"),
    ("record tv", "News"),
    ("tv cultura", "News"),
    ("tve", "News"),
    ("cnt", "News"),
    ("24h", "News"),
    ("mundo", "News"),
    ("noticias", "News"),
    ("i24", "News"),
)

# Stream hosts DLHD moved to. ``dlive.sx`` 301-redirects here.
_DLHD_WATCH_BASE = "https://thedaddy.pk/watch.php?id="


def _infer_category(name: str) -> str:
    """Best-guess genre for a DLHD channel name."""
    low = name.lower()
    for kw, cat in _CATEGORY_RULES:
        if kw in low:
            return cat
    return "Worldwide"


def _load_channels() -> list[dict]:
    with open(CHANNELS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_mapping() -> Dict[str, dict]:
    if not MAPPING_JSON.exists():
        return {}
    with open(MAPPING_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def build_dlhd_catalog() -> Dict[str, Dict[str, dict]]:
    """Build the DLHD catalog in ``ALL_CHANNELS_NOT_SORTED`` shape.

    Channel names are upper-cased to match the rest of the catalog (the
    API normalises lookups to upper case).

    Channels present in ``dlhd_epg_mapping.json`` get their explicit
    ``epg_id`` / ``epg_source``. Channels absent from it get
    ``epg_excluded: True`` — a marker the daily pipeline honours by
    keeping them out of the fuzzy matcher entirely, so a wrong guess can
    never be published for them.
    """
    mapping = _load_mapping()
    catalog: Dict[str, Dict[str, dict]] = {cat: {} for cat in CATEGORIES}

    for entry in _load_channels():
        raw_name = (entry.get("name") or "").strip()
        if not raw_name:
            continue
        name = raw_name.upper()
        channel_id = str(entry.get("id") or "")

        # Prefer the site's own current host; fall back to the stored
        # watchUrl (which still 301s there) when no id is present.
        if channel_id:
            watch_url = f"{_DLHD_WATCH_BASE}{channel_id}"
        else:
            watch_url = entry.get("watchUrl") or ""

        epg = mapping.get(raw_name)
        if epg:
            epg_id = epg.get("epg_id") or ""
            epg_source = epg.get("epg_source") or ""
        else:
            epg_id = ""
            epg_source = ""

        record = {
            "url": [watch_url] if watch_url else [],
            "url_hd": "",
            "image": "",
            "epg_id": epg_id,
            "epg_source": epg_source,
            # DLHD channel id — useful for the stream resolver and for
            # de-duplicating against the live site.
            "dlhd_id": channel_id,
        }
        if not epg_id:
            # No trustworthy EPG mapping — keep it away from the fuzzy
            # matcher so nothing incorrect is published for it.
            record["epg_excluded"] = True

        cat = _infer_category(raw_name)
        # Name collisions inside one category (the list has duplicates).
        key = name
        n = 1
        while key in catalog[cat]:
            n += 1
            key = f"{name} #{n}"
        catalog[cat][key] = record

    # Drop categories that ended up empty so the API doesn't advertise them.
    return {cat: chs for cat, chs in catalog.items() if chs}


def dlhd_channel_count() -> int:
    """Total number of DLHD channels in the generated catalog."""
    return sum(len(chs) for chs in build_dlhd_catalog().values())


if __name__ == "__main__":  # pragma: no cover - manual inspection helper
    cat = build_dlhd_catalog()
    total = 0
    for name, chs in cat.items():
        with_epg = sum(1 for c in chs.values() if c.get("epg_id"))
        total += len(chs)
        print(f"{name:<12} {len(chs):>5} channels  ({with_epg} with EPG)")
    print(f"{'TOTAL':<12} {total:>5} channels")
