"""Streaming XMLTV parser.

XMLTV files are *huge* (BG1 is 200K, IT1 is 1.6M, ALL_SOURCES would be 189MB)
so we don't load them into memory fully. We do two passes:

1) ``list_channels`` — open the .xml.gz, yield (channel_id, primary_display_name).
2) ``list_programmes`` — open again, yield programmes that fall in [start, end)
   for the requested channel ids only.

Both pass through ``lxml`` if available (much faster), else stdlib ``xml.etree``.
"""
from __future__ import annotations

import gzip
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Iterator, Optional, Set, Tuple
from xml.etree import ElementTree as ET

LOG = logging.getLogger("egp.xmltv")


@dataclass
class XChannel:
    id: str
    name: str          # primary display-name (first wins)
    icon: Optional[str] = None


@dataclass
class XProgramme:
    channel: str
    start: datetime    # tz-aware UTC
    stop: datetime     # tz-aware UTC
    title: str
    desc: Optional[str] = None
    category: Optional[str] = None
    episode: Optional[str] = None

    def to_dict(self) -> dict:
        d = {
            "channel": self.channel,
            "start": self.start.astimezone(timezone.utc).isoformat(),
            "stop": self.stop.astimezone(timezone.utc).isoformat(),
            "title": self.title,
        }
        if self.desc is not None:
            d["description"] = self.desc
        if self.category is not None:
            d["category"] = self.category
        if self.episode is not None:
            d["episode"] = self.episode
        return d


# ``YYYYMMDDHHMMSS [+offset]`` — the standard XMLTV format.
_DT_RE = re.compile(r"^(\d{14})(?:\s*([+-]\d{4}))?$")


def _parse_dt(value: str) -> Optional[datetime]:
    """Convert an XMLTV start/stop attribute (UTC by default) to aware dt."""
    if not value:
        return None
    m = _DT_RE.match(value.strip())
    if not m:
        return None
    base = m.group(1)
    tz = m.group(2)
    try:
        dt = datetime.strptime(base, "%Y%m%d%H%M%S")
    except ValueError:
        return None
    if tz:
        sign = 1 if tz[0] == "+" else -1
        hh = int(tz[1:3])
        mm = int(tz[3:5])
        offset = timedelta(hours=sign * hh, minutes=sign * mm)
        dt = dt.replace(tzinfo=timezone(offset))
        # Convert to UTC for our internal use.
        dt = dt.astimezone(timezone.utc)
    else:
        # No offset → per XMLTV spec, assume UTC.
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _open(path: str | Path):
    """Open .xml.gz transparently."""
    p = str(path)
    if p.endswith(".gz"):
        return gzip.open(p, "rb")
    return open(p, "rb")


def list_channels(path: str | Path) -> Iterator[XChannel]:
    """Yield ``XChannel`` for every <channel> in the XMLTV file."""
    with _open(path) as f:
        context = ET.iterparse(f, events=("end",))
        for event, elem in context:
            if elem.tag != "channel":
                continue
            cid = elem.attrib.get("id", "").strip()
            if not cid:
                elem.clear()
                continue
            name: Optional[str] = None
            icon: Optional[str] = None
            for child in elem:
                tag = child.tag
                if tag == "display-name" and name is None:
                    name = (child.text or "").strip()
                elif tag == "icon" and icon is None:
                    icon = child.attrib.get("src")
            if name:
                yield XChannel(id=cid, name=name, icon=icon)
            elem.clear()


def list_programmes(path: str | Path,
                    channel_ids: Optional[Set[str]] = None,
                    window_start: Optional[datetime] = None,
                    window_end: Optional[datetime] = None
                    ) -> Iterator[XProgramme]:
    """Yield ``XProgramme`` for every <programme> in the XMLTV file.

    ``channel_ids``: when given, restrict to those channels (None = all).
    ``window_start`` / ``window_end``: filter programmes whose [start, stop)
    overlaps the window.
    """
    with _open(path) as f:
        context = ET.iterparse(f, events=("end",))
        for event, elem in context:
            if elem.tag != "programme":
                continue
            ch = elem.attrib.get("channel", "").strip()
            if channel_ids is not None and ch not in channel_ids:
                elem.clear()
                continue
            start = _parse_dt(elem.attrib.get("start", ""))
            stop = _parse_dt(elem.attrib.get("stop", ""))
            if start is None or stop is None:
                elem.clear()
                continue
            if window_end is not None and stop <= window_start if window_start else False:
                elem.clear()
                continue  # pragma: no cover
            if window_start is not None and start >= window_end:
                elem.clear()
                continue
            if window_start is not None and window_end is not None:
                if stop <= window_start or start >= window_end:
                    elem.clear()
                    continue
            title: Optional[str] = None
            desc: Optional[str] = None
            category: Optional[str] = None
            episode: Optional[str] = None
            for child in elem:
                tag = child.tag
                text = (child.text or "").strip()
                if tag == "title" and title is None:
                    title = text
                elif tag == "desc" and desc is None:
                    desc = text
                elif tag == "category" and category is None:
                    category = text
                elif tag == "episode-num" and episode is None:
                    episode = text
            if not title:
                elem.clear()
                continue
            yield XProgramme(channel=ch, start=start, stop=stop,
                             title=title, desc=desc, category=category,
                             episode=episode)
            elem.clear()


def channels_to_lookup(path: str | Path) -> dict[str, XChannel]:
    """Convenience: returns ``{channel_id: XChannel}`` after first pass."""
    out: dict[str, XChannel] = {}
    for ch in list_channels(path):
        out[ch.id] = ch
    return out
