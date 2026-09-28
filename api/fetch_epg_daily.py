#!/usr/bin/env python3
"""fetch_epg_daily.py — one-shot EPG fetch + publish for systemd / cron.

Designed to be triggered externally (no in-process scheduler). Typical
deployment: a systemd timer fires this script once a day at noon, fetches the
EPG, copies it into ``epg_data/latest/`` for the API to read, and exits.

Wraps the existing pipeline at ``fetch_epg.py`` (vendored in this directory):

    1. Imports it.
    2. Reads ``tv_channels.ALL_CHANNELS_NOT_SORTED`` and finds channels that
       declare explicit ``epg_id`` / ``epg_source`` fields. These get a
       100 %-accurate direct lookup — fuzzy matching is bypassed.
    3. Builds an in-memory catalog from the remaining channels (those without
       explicit IDs) and patches the pipeline to consume it.
    4. Runs ``fetch_epg.run()`` on the filtered catalog.
    5. Merges the explicit-ID channels' programmes + match records back into
       the pipeline's output files (``epg.json``, ``epg_match.json``,
       ``epg_unmatched.json``).
    6. Copies everything into ``api/epg_data/latest/`` and writes ``meta.json``.
    7. Prunes old run directories per ``--keep-runs`` (default 7).
    8. Exits 0 on success, non-zero on failure (systemd will log + alert).

Usage::

    python fetch_epg_daily.py                          # default: curated sources, 2 days, keep 7 runs
    python fetch_epg_daily.py --days 3                 # keep 3 days of programmes
    python fetch_epg_daily.py --source BG1 IT1         # restrict to a subset
    python fetch_epg_daily.py --keep-runs 3            # only keep the 3 newest data/<run-ts>/ dirs
    python fetch_epg_daily.py --keep-runs 0            # never prune (disk keeps growing)
    python fetch_epg_daily.py --epg-source /opt/egp    # override pipeline location

Explicit IDs in ``tv_channels.py``::

    "AMC": {
        "url": [...],
        "url_hd": "...",
        "image": "...",
        "epg_id": "AMC.bg",        # <- new, optional. XMLTV channel id.
        "epg_source": "BG1",       # <- new, optional. XMLTV source id.
    },

When both fields are set, the pipeline uses the exact ``epg_id`` from the
named ``epg_source`` instead of fuzzy-matching. When either field is missing,
the channel goes through the normal fuzzy matcher.

Systemd timer example::

    # /etc/systemd/system/epg-fetch.service
    [Service]
    Type=oneshot
    User=epg
    WorkingDirectory=/opt/tv-api/api
    ExecStart=/usr/bin/python3 fetch_epg_daily.py
    StandardOutput=journal
    StandardError=journal

    # /etc/systemd/system/epg-fetch.timer
    [Timer]
    OnCalendar=*-*-* 12:00:00
    Persistent=true

    [Install]
    WantedBy=timers.target

Enable with::

    sudo systemctl daemon-reload
    sudo systemctl enable --now epg-fetch.timer
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# tv_channels.py lives next to this script — that's the single source of truth
# for the channel catalog. We import it before fetch_epg so its catalog can be
# built without touching disk.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tv_channels import ALL_CHANNELS_NOT_SORTED  # noqa: E402

# -----------------------------------------------------------------------------
# Paths.
# -----------------------------------------------------------------------------
THIS_DIR = Path(__file__).resolve().parent
# Default: the upstream pipeline lives next to this script. Override with
# --epg-source if it's elsewhere on the host.
DEFAULT_EGP_SOURCE = THIS_DIR

EPG_DATA_DIR = THIS_DIR / "epg_data"
EPG_LATEST_DIR = EPG_DATA_DIR / "latest"

# -----------------------------------------------------------------------------
# Logging.
# -----------------------------------------------------------------------------
LOG = logging.getLogger("fetch_epg_daily")


def _setup_logging(verbose: bool = False) -> None:
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format=fmt,
        stream=sys.stderr,
    )


# -----------------------------------------------------------------------------
# Catalog + explicit-ID handling.
# -----------------------------------------------------------------------------
def _build_catalog(skip_upper_names: set[str] | None = None):
    """Build a ``fetch_epg.Catalog`` from ``tv_channels.ALL_CHANNELS_NOT_SORTED``.

    No JSON on disk — the pipeline reads from disk only because we tell it to,
    and we don't tell it to.

    Channel names are upper-cased so epg.json / epg_match.json keys match the
    keys in ``tv_channels.ALL_CHANNELS`` (which the Flask API looks up against).
    Without this the two could drift if the source dict has mixed case.

    ``skip_upper_names`` — channel names (uppercase) to exclude from the
    catalog. Used to filter out channels that have explicit ``epg_id``
    mappings (they get handled by the direct lookup path, not fuzzy match).
    """
    import fetch_epg  # local import; fetch_epg may need sys.path setup first

    skip = skip_upper_names or set()
    catalog = fetch_epg.Catalog(channels=[])
    for cat, chs in ALL_CHANNELS_NOT_SORTED.items():
        for ch_name, ch_data in chs.items():
            upper = ch_name.upper()
            if upper in skip:
                continue
            urls = list(ch_data.get("url") or [])
            url_hd = ch_data.get("url_hd")
            if url_hd:
                urls.append(url_hd)
            catalog.channels.append(fetch_epg.Catalog.Channel(
                category=cat, name=upper,
                image=ch_data.get("image"),
                urls=urls,
                url_hd=url_hd,
            ))
    catalog.by_name = {ch.name: ch for ch in catalog.channels}
    return catalog


def _collect_explicit_matches():
    """Find channels in tv_channels.py that declare ``epg_id`` and ``epg_source``.

    Returns ``(matches, sources)`` where:
      - matches: dict[str, ChannelMatch] keyed by upper-case channel name
      - sources: dict[str, Path]      keyed by source ID -> cached .xml.gz path

    A channel is "explicit" only when both ``epg_id`` and ``epg_source`` are
    present and non-empty. Anything else falls through to the fuzzy matcher.
    """
    import fetch_epg

    matches: dict[str, fetch_epg.ChannelMatch] = {}
    sources: dict[str, Path] = {}

    cache_dir = THIS_DIR / "cache"

    for cat, chs in ALL_CHANNELS_NOT_SORTED.items():
        for ch_name, ch_data in chs.items():
            epg_id = (ch_data.get("epg_id") or "").strip()
            epg_source = (ch_data.get("epg_source") or "").strip()
            if not epg_id or not epg_source:
                continue
            upper = ch_name.upper()
            src_path = cache_dir / f"epg_ripper_{epg_source}.xml.gz"
            matches[upper] = fetch_epg.ChannelMatch(
                channel=upper,
                category=cat,
                matched_xmltv_id=epg_id,
                matched_xmltv_name=epg_id,
                matched_source=epg_source,
                score=1.0,
                reason="explicit-mapping",
                alternatives=[],
                n_programmes=0,
            )
            sources[epg_source] = src_path

    return matches, sources


# -----------------------------------------------------------------------------
# Run the upstream pipeline.
# -----------------------------------------------------------------------------
class _AlwaysExistsPath:
    """Stand-in for a ``Path`` whose ``.exists()`` returns True.

    ``fetch_epg.run()`` checks ``CATALOG_PATH.exists()`` before loading. Since
    we feed it a pre-built catalog, the actual path value doesn't matter — we
    just need ``exists()`` to be true so the early-exit branch doesn't fire.
    """

    def exists(self) -> bool:
        return True


def _run_pipeline(args: argparse.Namespace) -> int:
    """Import fetch_epg from --epg-source and invoke its ``run()``.

    Returns fetch_epg's exit code.
    """
    epg_source = args.epg_source
    if not epg_source.exists():
        LOG.error("EPG source directory not found: %s", epg_source)
        return 2
    sys.path.insert(0, str(epg_source))
    try:
        import fetch_epg  # type: ignore[import-not-found]
    except ImportError as e:
        LOG.error("failed to import fetch_epg from %s: %s", epg_source, e)
        return 2

    # Build the catalog excluding channels that have explicit epg_id mappings.
    explicit_matches, explicit_sources = _collect_explicit_matches()
    explicit_names = set(explicit_matches.keys())
    catalog = _build_catalog(skip_upper_names=explicit_names)
    LOG.info("loaded %d channels from tv_channels (%d explicit, %d fuzzy)",
             len(catalog.channels) + len(explicit_names),
             len(explicit_names),
             len(catalog.channels))
    if explicit_sources:
        LOG.info("explicit EPG sources required: %s",
                 sorted(explicit_sources.keys()))

    original_load_catalog = fetch_epg.load_catalog
    original_catalog_path = fetch_epg.CATALOG_PATH
    fetch_epg.load_catalog = lambda _path: catalog
    fetch_epg.CATALOG_PATH = _AlwaysExistsPath()

    inner = argparse.Namespace(
        source=args.source,
        refresh_source=args.refresh_source,
        days=args.days,
        no_fetch=args.no_fetch,
        list_sources=False,
    )
    LOG.info("starting EPG pipeline (days=%s, sources=%s)",
             args.days,
             args.source if args.source else "curated")
    try:
        rc = fetch_epg.run(inner)
    finally:
        fetch_epg.load_catalog = original_load_catalog
        fetch_epg.CATALOG_PATH = original_catalog_path

    if rc == 0 and explicit_matches:
        _merge_explicit_matches(epg_source, explicit_matches, explicit_sources,
                                args.days)
    return rc


def _merge_explicit_matches(epg_source: Path, explicit_matches, explicit_sources,
                            days: int) -> None:
    """Add explicit-ID channels' programmes + match records to the run output.

    After the pipeline writes epg.json / epg_match.json / epg_unmatched.json
    for the fuzzy-matched channels, this function reads those files, extracts
    programmes for each explicit match from the named source XMLTV file, and
    writes the merged result back. Channel names in the explicit set are also
    stripped from epg_unmatched.json.
    """
    import fetch_epg
    from xmltv import list_programmes  # vendored in this directory

    run_dir = _latest_run_dir(epg_source)
    if run_dir is None:
        LOG.warning("merge: no run dir found, explicit matches not added")
        return

    epg_path = run_dir / "epg.json"
    match_path = run_dir / "epg_match.json"
    unmatched_path = run_dir / "epg_unmatched.json"

    try:
        with open(epg_path, encoding="utf-8") as f:
            epg = json.load(f)
        with open(match_path, encoding="utf-8") as f:
            matches = json.load(f)
        with open(unmatched_path, encoding="utf-8") as f:
            unmatched = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        LOG.warning("merge: failed to read pipeline outputs: %s", e)
        return

    days = max(1, days)
    window_start = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=days)

    added = 0
    matched_now = 0
    for name, cm in explicit_matches.items():
        src_path = explicit_sources[cm.matched_source]
        if not src_path.exists():
            LOG.warning("merge: source file %s missing for '%s' — skipped",
                        src_path, name)
            continue

        wanted = {cm.matched_xmltv_id: cm}
        try:
            progs_iter = list_programmes(src_path, channel_ids=set(wanted),
                                         window_start=window_start,
                                         window_end=window_end)
        except Exception as e:
            LOG.warning("merge: list_programmes failed for '%s': %s", name, e)
            continue

        for prog in progs_iter:
            if prog.channel != cm.matched_xmltv_id:
                continue
            d = prog.to_dict()
            d["channel"] = name
            d["xmltv_id"] = prog.channel
            d["source"] = cm.matched_source
            epg.setdefault(name, []).append(d)
            added += 1

        matches[name] = {
            "channel": name,
            "category": cm.category,
            "matched_xmltv_id": cm.matched_xmltv_id,
            "matched_xmltv_name": cm.matched_xmltv_name,
            "matched_source": cm.matched_source,
            "score": cm.score,
            "reason": cm.reason,
            "alternatives": [],
            "n_programmes": 0,
        }
        matched_now += 1
        # Strip from unmatched list (matched via direct mapping, not fuzzy).
        unmatched = [u for u in unmatched
                     if u.get("name", "").upper() != name]

    # Sort programmes by start time per channel.
    for lst in epg.values():
        lst.sort(key=lambda p: p["start"])

    # Refresh n_programmes on every match record.
    for n in matches:
        matches[n]["n_programmes"] = len(epg.get(n, []))

    # Write back the merged files.
    with open(epg_path, "w", encoding="utf-8") as f:
        json.dump(epg, f, indent=2, ensure_ascii=False)
    with open(match_path, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    with open(unmatched_path, "w", encoding="utf-8") as f:
        json.dump(unmatched, f, indent=2, ensure_ascii=False)

    LOG.info("merged %d programmes across %d explicit matches",
             added, matched_now)


def _latest_run_dir(epg_source: Path) -> Path | None:
    """Find the most recent ``data/<UTC-ts>/`` directory under ``epg_source``."""
    data_dir = epg_source / "data"
    if not data_dir.is_dir():
        return None
    candidates = [p for p in data_dir.iterdir() if p.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.name)


def _publish(epg_source: Path) -> dict:
    """Copy the latest run's outputs into ``epg_data/latest/`` and write meta.

    Returns the meta dict that was written.
    """
    run_dir = _latest_run_dir(epg_source)
    if run_dir is None:
        raise RuntimeError(f"no run directory under {epg_source / 'data'}")

    EPG_LATEST_DIR.mkdir(parents=True, exist_ok=True)

    sources_copied: list[str] = []
    for fname in ("epg.json", "epg_match.json", "epg_unmatched.json"):
        src = run_dir / fname
        if not src.exists():
            LOG.warning("missing %s in run dir", src)
            continue
        shutil.copy2(src, EPG_LATEST_DIR / fname)
        sources_copied.append(fname)

    # Build meta.json from epg_match.json + run_dir timestamp.
    match_path = EPG_LATEST_DIR / "epg_match.json"
    n_matched = 0
    sources_used: set[str] = set()
    if match_path.exists():
        try:
            with open(match_path, encoding="utf-8") as f:
                match = json.load(f)
            n_matched = len(match)
            for v in match.values():
                src_id = v.get("matched_source")
                if src_id:
                    sources_used.add(src_id)
        except (OSError, json.JSONDecodeError) as e:
            LOG.warning("epg_match.json is invalid: %s", e)

    n_programmes = 0
    epg_path = EPG_LATEST_DIR / "epg.json"
    if epg_path.exists():
        try:
            with open(epg_path, encoding="utf-8") as f:
                epg = json.load(f)
            n_programmes = sum(len(v) for v in epg.values() if isinstance(v, list))
        except (OSError, json.JSONDecodeError) as e:
            LOG.warning("epg.json is invalid: %s", e)

    # run_dir name format: YYYYMMDDTHHMMSSZ.
    try:
        finished_at = datetime.strptime(run_dir.name, "%Y%m%dT%H%M%SZ").replace(
            tzinfo=timezone.utc)
    except ValueError:
        finished_at = datetime.now(tz=timezone.utc)

    meta = {
        "last_refresh_utc": finished_at.isoformat(),
        "n_channels_with_epg": n_matched,
        "n_programmes": n_programmes,
        "sources_used": sorted(sources_used),
        "run_dir": str(run_dir),
        "files": sources_copied,
    }
    with open(EPG_LATEST_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    LOG.info("published %s to %s (channels=%d programmes=%d)",
             ", ".join(sources_copied) or "(nothing)",
             EPG_LATEST_DIR, n_matched, n_programmes)
    return meta


def _prune_old_runs(epg_source: Path, keep: int) -> int:
    """Delete old ``data/<run-ts>/`` directories, keeping the newest ``keep``.

    Returns the number of directories pruned.
    """
    if keep <= 0:
        return 0
    data_dir = epg_source / "data"
    if not data_dir.is_dir():
        return 0
    candidates = sorted(
        (p for p in data_dir.iterdir() if p.is_dir()),
        key=lambda p: p.name,
        reverse=True,  # newest first (timestamps sort lexicographically)
    )
    to_remove = candidates[keep:]
    pruned = 0
    for p in to_remove:
        try:
            shutil.rmtree(p)
            LOG.info("pruned old run dir: %s", p)
            pruned += 1
        except OSError as e:
            LOG.warning("failed to prune %s: %s", p, e)
    return pruned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=2,
                        help="Days of programmes to keep (default 2 = today + tomorrow).")
    parser.add_argument("--source", nargs="+", default=None,
                        help="Restrict to these XMLTV source IDs (e.g. BG1 IT1). "
                             "Default: the curated list inside fetch_epg.py.")
    parser.add_argument("--refresh-source", nargs="+", default=None,
                        help="Force re-download of these source IDs even if cached.")
    parser.add_argument("--no-fetch", action="store_true",
                        help="Do not hit the network; reuse cached XMLTV files.")
    parser.add_argument("--epg-source", type=Path, default=DEFAULT_EGP_SOURCE,
                        help=f"Path to the upstream EPG pipeline "
                             f"(default: {DEFAULT_EGP_SOURCE}).")
    parser.add_argument("--keep-runs", type=int, default=7,
                        help="Keep the N most recent data/<run-ts>/ directories "
                             "(default 7). 0 = keep all.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose logging.")
    args = parser.parse_args(argv)
    _setup_logging(args.verbose)

    EPG_DATA_DIR.mkdir(parents=True, exist_ok=True)
    EPG_LATEST_DIR.mkdir(parents=True, exist_ok=True)

    rc = _run_pipeline(args)
    if rc != 0:
        LOG.error("pipeline exited with rc=%d", rc)
        return rc
    try:
        _publish(args.epg_source)
    except Exception as e:
        LOG.error("publish failed: %s", e)
        return 3
    pruned = _prune_old_runs(args.epg_source, args.keep_runs)
    if pruned:
        LOG.info("pruned %d old run dir(s); keeping %d",
                 pruned, args.keep_runs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
