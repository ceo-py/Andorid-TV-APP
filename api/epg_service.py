"""epg_service.py — read-side helpers for the EPG API.

The daily scheduler (fetch_epg_daily.py) writes the latest EPG into
``epg_data/latest/``. This module loads those JSON files on demand,
with a tiny in-process mtime cache so repeated requests don't re-parse.

Public API:
    load_epg()          -> dict[channel_name, list[programme]]
    load_match()        -> dict[channel_name, match metadata]
    load_meta()         -> dict (timestamp, counts, sources)
    load_unmatched()    -> list[dict]
    is_available()      -> bool  (True once a run has produced data)
    current_programmes(channel_name, now=None)
                        -> (current_programme | None, next_programme | None)
    channels_with_epg() -> list[str]   (sorted)
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LOG = logging.getLogger("epg_service")

# Canonical data location. fetch_epg_daily.py populates this directory.
EPG_DIR = Path(__file__).resolve().parent / "epg_data" / "latest"
EPG_FILE = EPG_DIR / "epg.json"
MATCH_FILE = EPG_DIR / "epg_match.json"
UNMATCHED_FILE = EPG_DIR / "epg_unmatched.json"
META_FILE = EPG_DIR / "meta.json"

# Module-level cache: (mtime, parsed). Invalidated when the file changes.
_epg_cache = None
_match_cache = None
_meta_cache = None
_unmatched_cache = None


def _load_json(path, cache_attr):
    # type: (Path, str) -> Optional[Any]
    """Load ``path`` as JSON, caching by mtime. Returns None if file missing."""
    if not path.exists():
        return None
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    cache = globals().get(cache_attr)
    if cache is not None and cache[0] == mtime:
        return cache[1]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        LOG.warning("failed to read %s: %s", path, e)
        return None
    globals()[cache_attr] = (mtime, data)
    return data


def is_available():
    # type: () -> bool
    """True once ``epg.json`` exists in the canonical location."""
    return EPG_FILE.exists()


def load_epg():
    # type: () -> dict
    """Return ``{channel_name: [programme, ...]}`` or an empty dict if not ready."""
    data = _load_json(EPG_FILE, "_epg_cache")
    return data if isinstance(data, dict) else {}


def load_match():
    # type: () -> dict
    """Return ``{channel_name: match metadata}`` from epg_match.json."""
    data = _load_json(MATCH_FILE, "_match_cache")
    return data if isinstance(data, dict) else {}


def load_meta():
    # type: () -> dict
    """Return the run's meta dict (timestamp, counts, sources, ...)."""
    data = _load_json(META_FILE, "_meta_cache")
    return data if isinstance(data, dict) else {}


def load_unmatched():
    # type: () -> list
    """Return the list of channels the matcher couldn't cover."""
    data = _load_json(UNMATCHED_FILE, "_unmatched_cache")
    return data if isinstance(data, list) else []


def channels_with_epg():
    # type: () -> list
    """Channel names that have at least one programme, sorted."""
    return sorted(name for name, progs in load_epg().items() if progs)


def _programme_window(p):
    # type: (dict) -> tuple
    """Parse ISO-8601 start/stop of a programme. Always returns UTC datetimes."""
    def _to_dt(s):
        # Python 3.11+ understands "Z" but we tolerate it explicitly for older versions.
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s).astimezone(timezone.utc)
    return _to_dt(p["start"]), _to_dt(p["stop"])


def current_programmes(channel_name, now=None):
    # type: (str, Optional[datetime]) -> tuple
    """Return ``(current, next)`` programme for ``channel_name``.

    ``current`` is the programme whose ``[start, stop)`` contains ``now``;
    ``next`` is the one immediately after. Either may be ``None``.

    Channel name is matched case-insensitively against the EPG keys.
    """
    epg = load_epg()
    if not epg:
        return None, None

    # Locate the channel's programmes, trying exact match first then upper-case.
    progs = epg.get(channel_name)
    if progs is None:
        upper = channel_name.upper()
        for key, val in epg.items():
            if key.upper() == upper:
                progs = val
                break
    if not progs:
        return None, None

    if now is None:
        now = datetime.now(tz=timezone.utc)

    current = None
    for p in progs:
        try:
            start, stop = _programme_window(p)
        except (KeyError, ValueError):
            continue
        if start <= now < stop:
            current = p
            break
        if start > now:
            # Programmes are sorted by start ascending in epg.json, so this is
            # the first one in the future.
            return current, p
    # ``now`` is past the last programme in the file.
    return current, None
