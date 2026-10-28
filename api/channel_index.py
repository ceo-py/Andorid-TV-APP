"""On-disk cache of parsed XMLTV channel indexes.

Parsing a source's ``<channel>`` elements means streaming the whole
``.xml.gz`` file. Across the 86 curated feeds that is ~1.7 GB of XML on
every run — about a minute of pure CPU, and it happens even though the
channel lists themselves change only every few days.

So we keep the parsed index next to the feed:

    cache/epg_ripper_<ID>.xml.gz          # the feed
    cache/.chindex/epg_ripper_<ID>.json   # parsed {id: display_name}

The cache key is the feed's ``(size, mtime)``. When the feed is
re-downloaded its mtime changes, the key no longer matches and the index
is rebuilt — so the cache can never go stale.

Reading the index back is a few hundred KB of JSON against a hundred
megabytes of XML: ~1 s instead of ~52 s for the whole source set.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

LOG = __import__("logging").getLogger("egp.chindex")

CACHE_SUBDIR = ".chindex"


def index_path_for(source_path: Path) -> Path:
    """Where the parsed index for ``source_path`` lives."""
    return source_path.parent / CACHE_SUBDIR / (source_path.name + ".json")


def _stamp(path: Path) -> Tuple[int, int]:
    """Identity of the feed file: (size, mtime_ns)."""
    st = path.stat()
    return (st.st_size, st.st_mtime_ns)


def load_index(source_path: Path) -> Optional[Dict[str, str]]:
    """Return ``{channel_id: display_name}`` from cache, or ``None``.

    ``None`` means "no usable cache" — the caller should parse the feed.
    """
    idx = index_path_for(source_path)
    try:
        with open(idx, "r", encoding="utf-8") as f:
            blob = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(blob, dict):
        return None
    size, mtime = blob.get("size"), blob.get("mtime_ns")
    try:
        cur_size, cur_mtime = _stamp(source_path)
    except OSError:
        return None
    if size != cur_size or mtime != cur_mtime:
        return None  # the feed changed — the index is stale
    names = blob.get("channels")
    if not isinstance(names, dict):
        return None
    return names


def store_index(source_path: Path, names: Dict[str, str]) -> None:
    """Write the parsed index to disk. Best-effort — never raises."""
    try:
        size, mtime = _stamp(source_path)
    except OSError:
        return
    idx = index_path_for(source_path)
    try:
        idx.parent.mkdir(parents=True, exist_ok=True)
        tmp = idx.with_suffix(idx.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"size": size, "mtime_ns": mtime, "channels": names},
                      f, ensure_ascii=False)
        os.replace(tmp, idx)
    except (OSError, TypeError, ValueError) as e:
        LOG.debug("channel index write failed for %s: %s", source_path, e)


# ---------------------------------------------------------------------------
# Programme cache.
#
# Same idea, for the programme side: the explicit-match merge needs the
# programmes of a handful of channel ids out of each source, but finding
# them means walking every <programme> element in the file — 30 s across
# the 50 sources the DLHD catalog touches. Caching the wanted programmes
# per source makes a repeat run (a retry, or --no-fetch) near-instant.
# ---------------------------------------------------------------------------
def programmes_path_for(source_path: Path) -> Path:
    """Where the cached programmes for ``source_path`` live."""
    return source_path.parent / CACHE_SUBDIR / (source_path.name + ".progs.json")


def load_programmes(source_path: Path) -> Optional[Dict[str, list]]:
    """Return ``{channel_id: [programme_dict, ...]}`` from cache, or ``None``.

    ``None`` means "no usable cache" — the caller should parse the feed.
    """
    idx = programmes_path_for(source_path)
    try:
        with open(idx, "r", encoding="utf-8") as f:
            blob = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(blob, dict):
        return None
    size, mtime = blob.get("size"), blob.get("mtime_ns")
    try:
        cur_size, cur_mtime = _stamp(source_path)
    except OSError:
        return None
    if size != cur_size or mtime != cur_mtime:
        return None  # the feed changed — the cache is stale
    progs = blob.get("programmes")
    if not isinstance(progs, dict):
        return None
    return progs


def store_programmes(source_path: Path,
                     progs: Dict[str, list]) -> None:
    """Write the cached programmes to disk. Best-effort — never raises."""
    try:
        size, mtime = _stamp(source_path)
    except OSError:
        return
    idx = programmes_path_for(source_path)
    try:
        idx.parent.mkdir(parents=True, exist_ok=True)
        tmp = idx.with_suffix(idx.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"size": size, "mtime_ns": mtime, "programmes": progs},
                      f, ensure_ascii=False)
        os.replace(tmp, idx)
    except (OSError, TypeError, ValueError) as e:
        LOG.debug("programme cache write failed for %s: %s", source_path, e)
