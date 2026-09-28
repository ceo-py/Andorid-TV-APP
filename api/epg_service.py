"""epg_service.py — read-side helpers for the EPG API.

The daily scheduler (fetch_epg_daily.py) writes the latest EPG into
``epg_data/latest/``. This module loads those JSON files on demand,
with a tiny in-process mtime cache so repeated requests don't re-parse.

It also resolves a channel's EPG match info by combining two sources:

1. **Explicit mappings** from ``tv_channels.ALL_CHANNELS`` — when a channel
   has both ``epg_id`` and ``epg_source`` set, those are used directly. This
   gives 100 % accurate matching for channels the operator has pinned.

2. **Fuzzy matches** from ``epg_data/latest/epg_match.json`` — when no explicit
   mapping exists, we look up what the upstream fuzzy matcher found.

Public API:
    load_epg()          -> dict[channel_name, list[programme]]
    load_match()        -> dict[channel_name, match metadata]
    load_meta()         -> dict (timestamp, counts, sources)
    load_unmatched()    -> list[dict]
    is_available()      -> bool  (True once a run has produced data)
    current_programmes(channel_name, now=None)
                        -> (current_programme | None, next_programme | None)
    channels_with_epg() -> list[str]   (sorted)
    resolve_channel_match(channel_name)
                        -> dict | None   (explicit > fuzzy > None)
"""
import json
import logging
from datetime import datetime, timedelta, timezone
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

# Lazy import — tv_channels imports nodriver at module top which is broken on
# Python 3.14+ on some test boxes. We import inside the function so the API
# endpoints that don't need it (current_programmes, load_epg, …) still work.
_ALL_CHANNELS = None


def _get_all_channels():
    global _ALL_CHANNELS
    if _ALL_CHANNELS is None:
        from tv_channels import ALL_CHANNELS
        _ALL_CHANNELS = ALL_CHANNELS
    return _ALL_CHANNELS


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


def _find_channel_entry(channel_name):
    """Look up a channel's full entry dict from ``tv_channels.ALL_CHANNELS``.

    Returns ``(entry_dict, category_name, canonical_name)`` or ``(None, None, None)``
    if the channel is not in the catalog. Match is case-insensitive.
    """
    upper = channel_name.upper()
    for category, channels in _get_all_channels().items():
        for name, data in channels.items():
            if name.upper() == upper:
                return data, category, name
    return None, None, None


def resolve_channel_match(channel_name):
    # type: (str) -> Optional[dict]
    """Resolve a channel's EPG match info, prioritising explicit mappings.

    Resolution order:

    1. **Explicit** — if ``tv_channels.ALL_CHANNELS[...].epg_id`` and
       ``.epg_source`` are both set and non-empty, use them directly.
       ``match_type`` is ``"explicit"`` and ``score`` is ``1.0``.

    2. **Fuzzy** — otherwise look up the channel in ``epg_match.json``.
       ``match_type`` is ``"fuzzy"`` and ``score`` reflects the matcher's
       confidence.

    3. **None** — channel is in the catalog but has neither an explicit
       mapping nor a fuzzy match. Returns ``None``.

    Returned dict has keys ``xmltv_id``, ``source``, ``score``, ``match_type``,
    and (for fuzzy matches) ``reason``.
    """
    entry, _category, _canonical = _find_channel_entry(channel_name)

    # Priority 1: explicit mapping from tv_channels.py.
    if entry is not None:
        explicit_id = (entry.get("epg_id") or "").strip()
        explicit_source = (entry.get("epg_source") or "").strip()
        if explicit_id and explicit_source:
            return {
                "xmltv_id": explicit_id,
                "source": explicit_source,
                "score": 1.0,
                "match_type": "explicit",
            }

    # Priority 2: fuzzy match from epg_match.json.
    match_meta = load_match()
    if channel_name in match_meta:
        m = match_meta[channel_name]
    else:
        upper = channel_name.upper()
        fuzzy = None
        for k, v in match_meta.items():
            if k.upper() == upper:
                fuzzy = v
                break
        m = fuzzy
    if m is not None:
        return {
            "xmltv_id": m.get("matched_xmltv_id"),
            "source": m.get("matched_source"),
            "score": m.get("score"),
            "match_type": "fuzzy",
            "reason": m.get("reason"),
        }

    return None


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


def now_playing_all(now=None):
    # type: (Optional[datetime]) -> list
    """Return ``(channel, current, next)`` for every channel with EPG data.

    Each entry is a dict shaped::

        {
            "channel":    str,   # catalog key (upper-case)
            "current":    dict | None,  # programme airing right now, or None
            "next":       dict | None,  # the next programme after current
            "progress":   float | None, # 0.0 .. 1.0, current's elapsed fraction
        }

    Channels whose EPG data has no programme covering ``now`` get
    ``current=None, next=None``. The result is sorted by channel name.
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)

    epg = load_epg()
    if not epg:
        return []

    out = []
    for channel_name, progs in epg.items():
        if not progs:
            continue
        current = None
        nxt = None
        progress = None
        for p in progs:
            try:
                start, stop = _programme_window(p)
            except (KeyError, ValueError):
                continue
            if start <= now < stop:
                current = p
                total = (stop - start).total_seconds()
                elapsed = (now - start).total_seconds()
                if total > 0:
                    progress = round(elapsed / total, 4)
                break
            if start > now:
                nxt = p
                break
        out.append({
            "channel": channel_name,
            "current": current,
            "next": nxt,
            "progress": progress,
        })
    out.sort(key=lambda r: r["channel"])
    return out

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


def _parse_date(s):
    """Parse ``YYYY-MM-DD`` as a UTC midnight datetime. Returns None on bad input."""
    try:
        return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def programmes_for_day(channel_name, date_str):
    # type: (str, Optional[str]) -> list
    """Return programmes for ``channel_name`` that overlap the given calendar day.

    ``date_str`` is ``YYYY-MM-DD`` interpreted as UTC. Returns an empty list
    if the date is malformed, the channel is unknown, or no programmes
    overlap that day.

    A programme "overlaps the day" if ``start < day_end`` and ``stop > day_start``,
    where ``[day_start, day_end)`` is the 24-hour UTC window starting at
    midnight on the given date.
    """
    day_start = _parse_date(date_str) if date_str else None
    if day_start is None:
        return []
    day_end = day_start + timedelta(days=1)

    epg = load_epg()
    if not epg:
        return []

    progs = epg.get(channel_name)
    if progs is None:
        upper = channel_name.upper()
        for key, val in epg.items():
            if key.upper() == upper:
                progs = val
                break
    if not progs:
        return []

    out = []
    for p in progs:
        try:
            start, stop = _programme_window(p)
        except (KeyError, ValueError):
            continue
        if stop <= day_start or start >= day_end:
            continue
        out.append(p)
    return out
