"""Defaults for the EPG pipeline. Keep behaviour changes here so callers
do not need to know implementation details."""

from pathlib import Path

# Where on disk everything lives.
ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "catalog.json"
CACHE_DIR = ROOT / "cache"
DATA_DIR = ROOT / "data"

# Where remote XMLTV files come from.
EPGSHARE_BASE = "https://epgshare01.online/epgshare01/"

# How many days of programming to keep per channel (today + N-1 more).
DEFAULT_DAYS = 2  # today + tomorrow

# Fuzzy-match threshold below which a candidate is dropped.
MATCH_THRESHOLD = 0.78

# Concurrent fetches when downloading new XMLTV sources.
PARALLEL_DOWNLOADS = 4
