#!/usr/bin/env python3
"""fetch_epg_daily.py — one-shot EPG fetch + publish for systemd / cron.

Designed to be triggered externally (no in-process scheduler). Typical
deployment: a systemd timer fires this script once a day at noon, fetches the
EPG, copies it into ``epg_data/latest/`` for the API to read, and exits.

Wraps the existing pipeline at ``fetch_epg.py`` (vendored in this directory):

    1. Imports it.
    2. Builds an in-memory catalog from ``tv_channels.ALL_CHANNELS_NOT_SORTED``
       (single source of truth — no catalog.json on disk).
    3. Patches the pipeline so it consumes that catalog instead of reading
       from a file, then calls ``run()``.
    4. Copies ``epg.json`` / ``epg_match.json`` / ``epg_unmatched.json`` from
       the newest ``data/<UTC-ts>`` run directory into
       ``api/epg_data/latest/``.
    5. Writes a small ``meta.json`` next to them summarising the run.
    6. Exits 0 on success, non-zero on failure (systemd will log + alert).

Usage::

    python fetch_epg_daily.py                          # default: curated sources, 2 days, keep 7 runs
    python fetch_epg_daily.py --days 3                 # keep 3 days of programmes
    python fetch_epg_daily.py --source BG1 IT1         # restrict to a subset
    python fetch_epg_daily.py --keep-runs 3            # only keep the 3 newest data/<run-ts>/ dirs
    python fetch_epg_daily.py --keep-runs 0            # never prune (disk keeps growing)
    python fetch_epg_daily.py --epg-source /opt/egp    # override pipeline location

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
from datetime import datetime, timezone
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
# Catalog (built in-memory from tv_channels).
# -----------------------------------------------------------------------------
def _build_catalog():
    """Build a ``fetch_epg.Catalog`` from ``tv_channels.ALL_CHANNELS_NOT_SORTED``.

    No JSON on disk — the pipeline reads from disk only because we tell it to,
    and we don't tell it to.

    Channel names are upper-cased so epg.json / epg_match.json keys match the
    keys in ``tv_channels.ALL_CHANNELS`` (which the Flask API looks up against).
    Without this the two could drift if the source dict has mixed case.
    """
    import fetch_epg  # local import; fetch_epg may need sys.path setup first

    catalog = fetch_epg.Catalog(channels=[])
    for cat, chs in ALL_CHANNELS_NOT_SORTED.items():
        for ch_name, ch_data in chs.items():
            urls = list(ch_data.get("url") or [])
            url_hd = ch_data.get("url_hd")
            if url_hd:
                urls.append(url_hd)
            catalog.channels.append(fetch_epg.Catalog.Channel(
                category=cat, name=ch_name.upper(),
                image=ch_data.get("image"),
                urls=urls,
                url_hd=url_hd,
            ))
    catalog.by_name = {ch.name: ch for ch in catalog.channels}
    return catalog


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

    # Build the catalog in-memory and inject it into the pipeline.
    catalog = _build_catalog()
    LOG.info("loaded %d channels across %d categories from tv_channels",
             len(catalog.channels),
             len({ch.category for ch in catalog.channels}))

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
        return fetch_epg.run(inner)
    finally:
        fetch_epg.load_catalog = original_load_catalog
        fetch_epg.CATALOG_PATH = original_catalog_path


def _latest_run_dir(epg_source: Path) -> Path | None:
    """Find the most recent ``data/<UTC-ts>`` directory under ``epg_source``."""
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
