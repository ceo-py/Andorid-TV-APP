#!/usr/bin/env python3
"""fetch_epg.py — pull EPG for as many of our catalog's channels as we can.

Examples::

    python fetch_epg.py                             # full default run
    python fetch_epg.py --source BG1 IT1            # only these two sources
    python fetch_epg.py --refresh-source BG1        # nuke BG1's cached .xml.gz
    python fetch_epg.py --days 3                    # today + next 2 days
    python fetch_epg.py --list-sources              # print curated source IDs
    python fetch_epg.py --no-fetch                  # reuse cache only, no network

Outputs land in::

    egp/data/<UTC-ts>/
        epg.json            # {channel_name: [programmes...]}
        epg_match.json      # how each catalog channel was matched
        epg_unmatched.json  # the ones we couldn't cover
        source_<NAME>.xml.gz  # cached files (also in cache/)
        run.log
"""
from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import json
import logging
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

# Local modules.
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config import (                       # noqa: E402
    CATALOG_PATH, CACHE_DIR, DATA_DIR, DEFAULT_DAYS,
    EPGSHARE_BASE, MATCH_THRESHOLD, PARALLEL_DOWNLOADS,
)
from sources import SOURCE_IDS, ALL_SOURCE_IDS, filename_for, url_for, curated  # noqa: E402
from matchers import best_match, normalise, score                          # noqa: E402
from xmltv import XChannel, XProgramme, list_channels, list_programmes      # noqa: E402


# -----------------------------------------------------------------------------
# Logging setup.

LOG = logging.getLogger("egp")


def _setup_logging(log_path: Path) -> None:
    LOG.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    # File
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    LOG.addHandler(fh)
    # Console (we control stdout ourselves; only attach a StreamHandler for errors).
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.WARNING)
    sh.setFormatter(fmt)
    LOG.addHandler(sh)


# -----------------------------------------------------------------------------
# Catalog loader.

@dataclass
class Catalog:
    """In-memory shape of catalog.json."""

    @dataclass
    class Channel:
        category: str
        name: str
        image: Optional[str] = None
        urls: list[str] = field(default_factory=list)
        url_hd: Optional[str] = None

    channels: list[Channel]
    by_name: dict[str, Channel] = field(default_factory=dict)


def load_catalog(path: Path) -> Catalog:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = Catalog(channels=[])
    cats = raw.get("channels", {})
    for cat, chs in cats.items():
        for ch_name, ch_data in chs.items():
            urls = list(ch_data.get("url") or [])
            url_hd = ch_data.get("url_hd")
            if url_hd:
                urls.append(url_hd)
            out.channels.append(Catalog.Channel(
                category=cat, name=ch_name,
                image=ch_data.get("image"),
                urls=urls,
                url_hd=url_hd,
            ))
    out.by_name = {ch.name.upper(): ch for ch in out.channels}
    return out


# -----------------------------------------------------------------------------
# Source download.

def _download_one(source_id: str, dest: Path, refresh: bool = False,
                  timeout: int = 60) -> tuple[str, Path, bool]:
    """Download a single source file. Returns (source_id, path, downloaded)."""
    if dest.exists() and not refresh:
        return source_id, dest, False
    url = url_for(source_id, EPGSHARE_BASE)
    LOG.info("downloading %s", url)
    req = urllib.request.Request(url, headers={"User-Agent": "egp/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{source_id}: HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"{source_id}: {e.reason}") from e
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return source_id, dest, True


def download_sources(source_ids: Iterable[str], cache: Path,
                     refresh: set[str] | None = None,
                     parallel: int = PARALLEL_DOWNLOADS) -> dict[str, Path]:
    """Download requested XMLTV sources. Skips files already cached unless
    ``refresh`` contains their ID."""
    refresh = refresh or set()
    out: dict[str, Path] = {}
    srcs = list(source_ids)
    LOG.info("ensuring %d source file(s) in %s", len(srcs), cache)
    cache.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as pool:
        futs = {pool.submit(_download_one, s, cache / filename_for(s),
                            s in refresh): s for s in srcs}
        for fut in concurrent.futures.as_completed(futs):
            sid = futs[fut]
            try:
                _, path, _ = fut.result()
            except Exception as e:
                LOG.warning("source %s failed: %s", sid, e)
                continue
            out[sid] = path
    return out


# -----------------------------------------------------------------------------
# Matching + dump.

@dataclass
class ChannelMatch:
    """How a single catalog channel was matched to XMLTV channels."""
    channel: str
    category: str
    matched_xmltv_id: str
    matched_xmltv_name: str
    matched_source: str
    score: float
    reason: str
    alternatives: list[tuple[str, float, str]] = field(default_factory=list)
    n_programmes: int = 0


@dataclass
class CatalogueRow:
    """Per-source pass: ranking of an XMLTV channel vs all catalog channels."""
    catalog_name: str
    catalog_score: float


@dataclass
class RunStats:
    """Top-level run summary."""
    n_catalog: int = 0
    n_matched: int = 0
    n_unmatched: int = 0
    n_sources: int = 0
    n_programmes_total: int = 0
    started_at: str = ""
    finished_at: str = ""


def _materialize_channels(path: Path) -> dict[str, XChannel]:
    """Materialise channels (small per file, BG is ~86, IT is ~193)."""
    return {ch.id: ch for ch in list_channels(path)}


def _pick_universe() -> dict[str, str]:
    """Return the candidate ``{xmltv_id: display_name}`` map across all sources."""
    return {}  # we keep it per-source in the real flow


def _collect_candidates_one_source(path: Path) -> list[tuple[str, str]]:
    """Yield ``(xmltv_channel_id, display_name)`` for one source file."""
    return [(ch.id, ch.name) for ch in list_channels(path)]


def _best_for_catalog(catalog: Catalog, source_path: Path,
                      source_id: str, threshold: float = MATCH_THRESHOLD
                      ) -> tuple[dict[str, ChannelMatch], list[tuple[str, XChannel, float]]]:
    """For a single source, find the best XMLTV channel for each catalog name.

    Returns:
        matches — catalog-name → ChannelMatch (only when best candidate passed threshold)
        candidates — list of (catalog_name, XChannel, best_score) for this source,
                     including non-winning candidates (so we can include them as
                     ``alternatives`` in matched entries).
    """
    chs = _materialize_channels(source_path)
    candidates = list(chs.values())

    matches: dict[str, ChannelMatch] = {}
    per_cat_info: list[tuple[str, XChannel, float]] = []

    # Build a candidate list once per source; iterate catalog and score.
    cands = [(ch.id, ch.name) for ch in candidates]

    for ch in catalog.channels:
        scores = [
            (score(ch.name, dname), cid) for cid, dname in cands
        ]
        scores.sort(key=lambda t: t[0].score, reverse=True)
        # Track all candidates as alternatives we evaluated.
        top = scores[:5] if scores else []
        if not top:
            continue
        best_m, best_cid = top[0]
        per_cat_info.append((ch.name, chs.get(best_cid), best_m.score))
        if best_m.score >= threshold:
            cat_ch = catalog.by_name[ch.name.upper()]
            alt = [(cid, score_obj.score, score_obj.reason)
                   for score_obj, cid in top[1:]]
            matches[ch.name] = ChannelMatch(
                channel=ch.name, category=cat_ch.category,
                matched_xmltv_id=best_cid, matched_xmltv_name=chs[best_cid].name,
                matched_source=source_id, score=best_m.score,
                reason=best_m.reason, alternatives=alt,
            )
    return matches, per_cat_info


def _emit_programmes(epg: dict[str, list], matches: dict[str, ChannelMatch],
                     channel_to_source: dict[str, Path],
                     window_start: datetime, window_end: datetime) -> int:
    """Pull programmes for every matched channel, in its source file, within the
    window. Mutates ``epg`` and returns total programme count.

    Each emitted programme's ``channel`` field is rewritten to the catalog
    channel name (not the XMLTV id) so consumers don't need a second lookup.
    """
    total = 0
    by_source: dict[Path, list[ChannelMatch]] = {}
    for cm in matches.values():
        by_source.setdefault(channel_to_source[cm.matched_source], []).append(cm)

    for src_path, ms in by_source.items():
        wanted = {m.matched_xmltv_id: m for m in ms}
        for prog in list_programmes(src_path,
                                   channel_ids=set(wanted),
                                   window_start=window_start,
                                   window_end=window_end):
            cm = wanted.get(prog.channel)
            if cm is None:
                continue
            d = prog.to_dict()
            d["channel"] = cm.channel          # rewrite: catalog name
            d["xmltv_id"] = prog.channel       # keep raw id for debugging
            d["source"] = cm.matched_source    # provenance
            epg.setdefault(cm.channel, []).append(d)
            total += 1
    return total


def _dump_unmatched(catalog: Catalog, matches: dict[str, ChannelMatch]) -> list[dict]:
    out = []
    matched_names = {m.channel.upper() for m in matches.values()}
    for ch in catalog.channels:
        if ch.name.upper() not in matched_names:
            out.append({
                "name": ch.name,
                "category": ch.category,
                "url_hd": ch.url_hd,
                "url": ch.urls,
            })
    return out


# -----------------------------------------------------------------------------
# Main run.

def run(args: argparse.Namespace) -> int:
    run_started = datetime.now(tz=timezone.utc)
    run_dir = DATA_DIR / run_started.strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=True)
    _setup_logging(run_dir / "run.log")
    LOG.info("run dir: %s", run_dir)

    if args.list_sources:
        print("# curated (priority order):")
        for s in SOURCE_IDS:
            print(s)
        print()
        print("# all available on epgshare01:")
        for s in ALL_SOURCE_IDS:
            print(s)
        return 0

    if not CATALOG_PATH.exists():
        LOG.error("catalog.json not found at %s", CATALOG_PATH)
        return 1

    catalog = load_catalog(CATALOG_PATH)
    LOG.info("loaded catalog: %d channels across %d categories",
             len(catalog.channels),
             len({ch.category for ch in catalog.channels}))

    # Decide which sources to fetch.
    source_ids = list(args.source) if args.source else list(curated())
    refresh = set(args.refresh_source or [])
    LOG.info("sources: %d (refresh=%s)", len(source_ids), sorted(refresh))

    # Download/ensure each source.
    sources: dict[str, Path] = {}
    if not args.no_fetch:
        sources = download_sources(source_ids, CACHE_DIR, refresh=refresh)
        LOG.info("downloaded/loaded %d source files", len(sources))
    else:
        for s in source_ids:
            p = CACHE_DIR / filename_for(s)
            if p.exists():
                sources[s] = p
        LOG.info("using %d cached source files (no_fetch)", len(sources))

    # Mirror the cache into the run dir so a single run is self-contained.
    for sid, p in sources.items():
        dst = run_dir / p.name
        if not dst.exists():
            try:
                dst.write_bytes(p.read_bytes())
            except Exception as e:
                LOG.warning("mirror %s: %s", dst, e)

    # Match across sources (first match wins; we keep alternatives for context).
    all_matches: dict[str, ChannelMatch] = {}
    channel_to_source: dict[str, Path] = {}
    # We process sources in the curated order; first match locks.
    for sid in source_ids:
        p = sources.get(sid)
        if not p or not p.exists():
            continue
        try:
            ms, _ = _best_for_catalog(catalog, p, sid, MATCH_THRESHOLD)
        except Exception as e:
            LOG.warning("scan %s failed: %s", sid, e)
            continue
        for name, cm in ms.items():
            if name not in all_matches:
                all_matches[name] = cm
                channel_to_source[sid] = p

    LOG.info("matched: %d / %d channels", len(all_matches), len(catalog.channels))

    # Window: from today's 00:00 UTC, span N days.
    days = max(1, args.days)
    window_start = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=days)

    # Pull programmes.
    epg: dict[str, list] = {}
    total_prog = _emit_programmes(
        epg, all_matches, channel_to_source, window_start, window_end)
    # Sort programmes by start time per channel.
    for lst in epg.values():
        lst.sort(key=lambda p: p["start"])

    # Update n_programmes per match for visibility.
    for name, cm in all_matches.items():
        cm.n_programmes = len(epg.get(name, []))

    # Write outputs.
    out_match = run_dir / "epg_match.json"
    out_epg = run_dir / "epg.json"
    out_unmatched = run_dir / "epg_unmatched.json"
    out_summary = run_dir / "summary.json"

    out_match.write_text(json.dumps(
        {name: asdict(cm) for name, cm in all_matches.items()},
        indent=2, ensure_ascii=False), encoding="utf-8")
    out_epg.write_text(json.dumps(epg, indent=2, ensure_ascii=False),
                       encoding="utf-8")
    unmatched = _dump_unmatched(catalog, all_matches)
    out_unmatched.write_text(json.dumps(unmatched, indent=2, ensure_ascii=False),
                             encoding="utf-8")

    stats = RunStats(
        n_catalog=len(catalog.channels),
        n_matched=len(all_matches),
        n_unmatched=len(unmatched),
        n_sources=len(sources),
        n_programmes_total=total_prog,
        started_at=run_started.isoformat(),
        finished_at=datetime.now(tz=timezone.utc).isoformat(),
    )
    out_summary.write_text(json.dumps(asdict(stats), indent=2),
                           encoding="utf-8")

    # Console summary.
    print()
    print(f"Run:           {run_dir}")
    print(f"Catalog:       {stats.n_catalog} channels")
    print(f"Matched:       {stats.n_matched} ({stats.n_matched * 100 // max(1, stats.n_catalog)}%)")
    print(f"Unmatched:     {stats.n_unmatched} (see epg_unmatched.json)")
    print(f"Sources used:  {stats.n_sources}")
    print(f"Programmes:    {stats.n_programmes_total} (next {days} day(s))")
    print()
    print("Top 10 matched channels by programme count:")
    for name, cm in sorted(all_matches.items(),
                           key=lambda kv: kv[1].n_programmes,
                           reverse=True)[:10]:
        print(f"  {cm.n_programmes:>5} progs  score={cm.score:.2f}  "
              f"src={cm.matched_source:<6} {name}")
    print()
    print(f"Wrote: epg.json, epg_match.json, epg_unmatched.json, summary.json")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="EPG fetch for catalog.json")
    parser.add_argument("--source", nargs="+", default=None,
                        help="Restrict to these source IDs (e.g. BG1 IT1). "
                             "Default: curated list.")
    parser.add_argument("--refresh-source", nargs="+", default=None,
                        help="Force re-download these sources even if cached.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS,
                        help=f"Include programmes for today + N-1 days "
                             f"(default {DEFAULT_DAYS}).")
    parser.add_argument("--no-fetch", action="store_true",
                        help="Do not hit the network; reuse any cached XMLTV files.")
    parser.add_argument("--list-sources", action="store_true",
                        help="Print the curated + full source ID lists and exit.")
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
