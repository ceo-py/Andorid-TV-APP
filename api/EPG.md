# EPG API

How the TV channel API exposes Electronic Program Guide (EPG) data to clients.

**Base URL:** `https://tv-api.ceo-py.eu`

All endpoint examples below are relative to this base.

### Quick examples

```bash
# Refresh status + unmatched list
curl https://tv-api.ceo-py.eu/epg-status | python3 -m json.tool

# What's playing now on AMC
curl 'https://tv-api.ceo-py.eu/get-channel-current?channel_name=AMC' | python3 -m json.tool

# What's playing on EVERY channel right now (single request)
curl https://tv-api.ceo-py.eu/get-current-all | python3 -m json.tool

# Just sport channels
curl 'https://tv-api.ceo-py.eu/get-current-all?channel_type=Sport' | python3 -m json.tool

# Full schedule for one channel
curl 'https://tv-api.ceo-py.eu/get-channel-epg?channel_type=Sport&channel_name=MATCH%21%20Futbol%201' | python3 -m json.tool

# Today's schedule for one channel (UTC date)
curl 'https://tv-api.ceo-py.eu/get-channel-epg?channel_name=AMC&date=2026-09-28' | python3 -m json.tool

# Server clock — sync before computing "now" locally
curl https://tv-api.ceo-py.eu/server-time | python3 -m json.tool
```

## 1 · What this is

Four new endpoints on the existing Flask API that return **what's playing now**,
**what's coming up**, and **the full schedule** for every channel in the
catalog at [api/tv_channels.py](tv_channels.py). The API itself does no
EPG work — it just serves JSON files that a separate daily job writes to disk.
The daily job reuses the existing pipeline at
`D:\ak47\mokup\egp\` (no rewrite).

```
                 +---------------------------+
                 |   XMLTV feeds             |
                 |   epgshare01.online       |
                 +-------------+-------------+
                               |
                               v  once per day
        +---------------------------------------------+
        |  fetch_epg_daily.py                         |
        |  (systemd timer @ 12:00)                    |
        |                                             |
        |  1. builds Catalog from tv_channels         |
        |     (curated 167 + DLHD 1,105 = 1,272)      |
        |  2. runs api/fetch_epg.py (imported)        |
        |  3. matches 1,272 -> 889 (70 %)             |
        |  4. copies outputs -> api/epg_data/latest/  |
        |  5. writes meta.json                        |
        +--------------------+------------------------+
                             |
                             v  (just files on disk)
                   +-----------------+
                   | epg_data/latest |
                   +--------+--------+
                            |
                            v  on each HTTP request
                   +-----------------+
                   |  Flask API      |
                   |  api.py         |
                   |  epg_service.py |
                   +--------+--------+
                            |
                            v  JSON
                     +-------------+
                     | Android app |
                     +-------------+
```

---

## 2 · Components

| File | Role |
|---|---|
| [api/fetch_epg_daily.py](fetch_epg_daily.py) | One-shot script. Imports and runs [api/fetch_epg.py](fetch_epg.py) (which lives in the same directory), then publishes the result into `api/epg_data/latest/`. Triggered by systemd / cron — no in-process scheduler. |
| [api/fetch_epg.py](fetch_epg.py) | CLI entrypoint of the upstream pipeline. Matches catalog channels against XMLTV feeds, emits `epg.json` + `epg_match.json` + `epg_unmatched.json` into `api/data/<run-ts>/`. |
| [api/config.py](config.py), [api/matchers.py](matchers.py), [api/sources.py](sources.py), [api/xmltv.py](xmltv.py) | Pipeline internals (paths, fuzzy matcher, source list, XMLTV parser). |
| [api/epg_service.py](epg_service.py) | Read-side helpers: `load_epg()`, `load_match()`, `load_meta()`, `load_unmatched()`, `current_programmes()`, `channels_with_epg()`, `is_available()`. In-process mtime cache so repeated requests don't re-parse JSON. |
| [api/api.py](api.py) | Flask app. Adds four EPG routes. Existing `/get-channel-video-url` and `/get-all-channels` are unchanged. |

The pipeline modules (`fetch_epg.py`, `config.py`, `matchers.py`, `sources.py`,
`xmltv.py`) live **in this directory** — the API repo is self-contained.
`--epg-source` defaults to `Path(__file__).parent`, so running
`python fetch_epg_daily.py` from anywhere Just Works as long as the script
lives next to those modules. See
[fetch_epg_daily.py:65](fetch_epg_daily.py#L65) for the default-path
logic.

The channel catalog comes from
[api/tv_channels.py:ALL_CHANNELS_NOT_SORTED](tv_channels.py) — no
`catalog.json` is required. [fetch_epg_daily._build_catalog()](fetch_epg_daily.py)
builds an in-memory `fetch_epg.Catalog` from that dict on every run.

### Explicit EPG IDs in `tv_channels.py`

The fuzzy matcher in the upstream pipeline gets ~95 % of channels right, but
the wrong 5 % matter — they show the wrong schedule to the user. To get
100 %-accurate matching for the channels you care most about, add two optional
fields to the channel entry:

```python
"AMC": {
    "url": [...],
    "url_hd": "...",
    "image": "...",
    "epg_id": "AMC.bg",          # XMLTV channel id from the source feed
    "epg_source": "BG1",         # XMLTV source id (e.g. BG1, IT1, US2, ...)
},
```

When both `epg_id` and `epg_source` are set:

- The channel is excluded from the fuzzy matcher entirely.
- Its programmes are pulled directly from `cache/epg_ripper_<epg_source>.xml.gz`.
- The match record's `reason` is `"explicit-mapping"` and `score` is `1.0`.

When either field is missing or empty, the channel falls through to the normal
fuzzy matcher. This means you can gradually opt channels in over time without
touching every entry.

[fetch_epg_daily._collect_explicit_matches()](fetch_epg_daily.py) collects
the explicit mappings, [fetch_epg_daily._build_catalog()](fetch_epg_daily.py)
filters them out of the fuzzy catalog, and
[fetch_epg_daily._merge_explicit_matches()](fetch_epg_daily.py) merges
their programmes + match records into the pipeline output after `run()`
completes.

#### How to find the right `epg_id`

The XMLTV feeds are in `api/cache/epg_ripper_<SOURCE>.xml.gz` after the first
network run. To discover the channel id for a given channel name:

```bash
# Example: find AMC's id in the BG1 feed
python -c "
import gzip, re
with gzip.open('cache/epg_ripper_BG1.xml.gz', 'rt', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'<channel id=\"([^\"]+)\">[^<]*<display-name[^>]*>AMC[^<]*</display-name>', content)
print(m.group(1) if m else 'not found')
"
```

To see ALL channel ids in a source, list the `<channel id="...">` entries:

```bash
python -c "
import gzip, re
with gzip.open('cache/epg_ripper_BG1.xml.gz', 'rt', encoding='utf-8') as f:
    content = f.read()
print('\n'.join(re.findall(r'<channel id=\"([^\"]+)\">[^<]*<display-name[^>]*>([^<]+)</display-name>', content)))
" | head -30
```

The full list of source IDs is in [sources.py:ALL_SOURCE_IDS](sources.py) —
commonly useful ones are `BG1` (Bulgaria), `IT1` (Italy), `DE1` (Germany),
`ES1` (Spain), `FR1` (France), `RO1` (Romania), `UK1` (UK), `US2` (US),
`GR1` (Greece), `TR1` (Turkey), `AL1` (Albania).

---

## 3 · Data layout

```
api/epg_data/
└── latest/
    ├── epg.json            # {channel_name: [programmes]}     <- the main payload
    ├── epg_match.json      # {channel_name: {xmltv_id, source, score, …}}
    ├── epg_unmatched.json  # [ {name, category, url, url_hd} ]   <- channels with no EPG
    └── meta.json           # {last_refresh_utc, n_channels_with_epg, n_programmes, sources_used}
```

The directory is populated by [fetch_epg_daily.py:_publish()](fetch_epg_daily.py). The API reads from it on every EPG request.

### `epg.json` shape

Top-level is a dict keyed by **catalog channel name** (matches the keys in
[api/tv_channels.py:ALL_CHANNELS](tv_channels.py)). Values are sorted
ascending by `start`.

```json
{
  "AMC": [
    {
      "channel": "AMC",
      "start": "2026-09-28T01:15:00+00:00",
      "stop":  "2026-09-28T04:00:00+00:00",
      "title": "Scarface",
      "description": "(1983) In 1980 Miami, a determined Cuban immigrant…",
      "category": "Филм",
      "xmltv_id": "AMC.bg",
      "source": "BG1"
    },
    { "...": "more programmes" }
  ],
  "DISNEY CHANNEL": [ "..." ]
}
```

Times are always **UTC**, ISO-8601. The XMLTV source file determines the
timezone of the original data, but `_emit_programmes()` in the upstream
pipeline converts to UTC before writing.

### `meta.json` shape

```json
{
  "last_refresh_utc": "2026-09-28T07:47:49+00:00",
  "n_channels_with_epg": 145,
  "n_programmes": 5161,
  "sources_used": ["BG1", "IT1", "UK1", "..."],
  "run_dir": "D:\\ak47\\mokup\\egp\\data\\20260928T074710Z",
  "files": ["epg.json", "epg_match.json", "epg_unmatched.json"]
}
```

---

## 4 · Endpoints

All four return JSON. Common error shape:

```json
{ "success": false, "error": "human-readable message" }
```

EPG responses set `Cache-Control: public, max-age=900` (15 minutes) — see
[api.py:_cache_control()](api.py).

### 4.1 · `GET /epg-status`

Last refresh time, coverage stats, unmatched channels.

**Request:** none.

**Response 200:**
```json
{
  "success": true,
  "status": {
    "last_refresh_utc": "2026-09-28T07:47:49+00:00",
    "last_refresh_age_hours": 4.2,
    "n_channels_with_epg": 889,
    "n_channels_total": 1272,
    "n_channels_explicit_mapping": 840,
    "n_channels_fuzzy": 49,
    "n_channels_unmatched": 383,
    "n_programmes": 41898,
    "sources_used": ["BG1", "IT1", "DE1", "..."]
  },
  "unmatched": [
    { "name": "PULSE ROCK", "category": "Music", "url": ["..."] }
  ],
  "data_dir": "D:\\VSC\\Andorid-TV-APP\\api\\epg_data\\latest"
}
```

`n_channels_total` counts the **whole** catalog (1,272), not just the served
subset — see §4.6.

**Response 503** — the daily job hasn't run yet:
```json
{ "success": false, "error": "EPG not yet generated — run fetch_epg_daily.py" }
```

### 4.2 · `GET /get-channel-epg`

Full programme list for one channel (today + tomorrow by default).

**Query params:**
- `channel_name` — case-insensitive
- `channel_type` — optional, speeds up the lookup
- `date` — optional `YYYY-MM-DD` (UTC). Restricts `programmes` to that one
  calendar day only. Useful for "show me today's full schedule" without
  pulling tomorrow's data.

**Request:**
```
GET /get-channel-epg?channel_type=Sport&channel_name=MATCH!%20Futbol%201
GET /get-channel-epg?channel_name=AMC&date=2026-09-28
```

**Response 200:**
```json
{
  "success": true,
  "channel": "MATCH! FUTBOL 1",
  "category": "Sport",
  "xmltv_id": "MatchTV.ru",
  "source": "RU1",
  "score": 0.83,
  "match_type": "fuzzy",
  "programmes": [ { "...": "see epg.json shape" } ]
}
```

`match_type` is `"explicit"` when the channel has `epg_id` + `epg_source` set
in `tv_channels.ALL_CHANNELS`, otherwise `"fuzzy"`.

**Response 200 with empty programmes** — channel is matched by the upstream
pipeline but has no programmes in the current date window (e.g. a channel
whose XMLTV feed only schedules future content):
```json
{
  "success": true,
  "channel": "MATCH! FUTBOL 1",
  "category": "Sport",
  "xmltv_id": "БНТ1.bg",
  "source": "BG1",
  "score": 0.78,
  "programmes": []
}
```

**Response 404** — channel is in the catalog but the matcher couldn't find an
XMLTV counterpart at all:
```json
{
  "success": false,
  "error": "No EPG for this channel",
  "channel": "PULSE ROCK",
  "category": "Music"
}
```

### 4.3 · `GET /get-channel-current`

What's playing on a channel right now + what's next. Designed for cheap polling
from the Android app.

**Query params:**
- `channel_name` — case-insensitive

**Response 200:**
```json
{
  "success": true,
  "channel": "AMC",
  "current": {
    "channel": "AMC",
    "start":  "2026-09-28T08:10:00+00:00",
    "stop":   "2026-09-28T10:05:00+00:00",
    "title":  "Луда бъркотия",
    "description": "...",
    "category": "Филм",
    "xmltv_id": "AMC.bg",
    "source": "BG1"
  },
  "next": {
    "channel": "AMC",
    "start":  "2026-09-28T10:05:00+00:00",
    "stop":   "2026-09-28T12:30:00+00:00",
    "title":  "Blackbeard 2/2",
    "description": "...",
    "category": "Филм",
    "xmltv_id": "AMC.bg",
    "source": "BG1"
  }
}
```

If a channel has no programme covering "now" but has upcoming ones, `current`
is `null` and `next` is populated. If the channel has no EPG at all, both are
`null` and the endpoint returns **404**.

### 4.4 · `GET /get-all-epg`

Full EPG dict. **Heavy — ~17 MB** (1,272 channels × 51 XMLTV sources).
Each programme has ISO-8601 `start` / `stop` in UTC. Clients are expected
to fetch this once, cache it locally, and compute "what's on now" from
the device clock.

**Caching:** `Cache-Control: public, max-age=86400` (24 h) since the data
is refreshed once per day. Response also includes `ETag` and
`Last-Modified` — pass `If-None-Match` / `If-Modified-Since` on subsequent
fetches and the server returns `304 Not Modified` (empty body) when the
data hasn't been refreshed since the client's cached copy.

**Optional filters.** A client that only needs a slice can ask for it
instead of pulling the whole payload. Filters combine with AND; with no
filter the response is unchanged.

| Parameter | Example | Effect |
|---|---|---|
| `source` | `?source=BG1,US2` | Only programmes from these XMLTV sources |
| `category` | `?category=Sport,Movie` | Only these catalog categories |
| `channels` | `?channels=AMC%20USA,BNT%203` | Only these channel names (exact, case-insensitive) |

```bash
# Bulgarian set only — ~2.6 MB instead of 17 MB
curl 'https://tv-api.ceo-py.eu/get-all-epg?source=BG1,GLOBETV2,IPTVEPG_BG'

# One category — ~4 MB
curl 'https://tv-api.ceo-py.eu/get-all-epg?category=Sport'

# Two channels — ~50 KB
curl 'https://tv-api.ceo-py.eu/get-all-epg?channels=AMC%20USA,BNT%203'
```

A filtered response gets its own `ETag` (derived from the refresh
timestamp **plus** the filter set), so a client holding the full-payload
ETag never gets a `304` for a different slice.

**Response 200:**
```json
{
  "success": true,
  "channels": ["AMC", "DISNEY CHANNEL", "..."],
  "epg": {
    "AMC":             [ { "...": "programmes" } ],
    "DISNEY CHANNEL":  [ { "...": "programmes" } ]
  }
}
```

### 4.5 · `GET /server-time`

Server's current UTC clock. Clients call this once on app start to measure
clock skew before computing "what's on now" locally from `/get-all-epg`.

**Response 200:**
```json
{
  "success": true,
  "now_utc": "2026-09-28T15:30:00.123456+00:00",
  "epoch_ms": 1759068600123
}
```

`Cache-Control: no-store` — never cached, always fresh.

The HTTP `Date` response header carries the server's clock independently;
clients compare it against `epoch_ms` to compute the skew to apply.
```

### 4.6 · `GET /get-all-channels`

The channel catalog. **Only the channels the matcher covered are returned** —
889 of the 1,272 in the catalog. A channel with no schedule would render as
an empty "now playing" row in the app, which is noise for the user, so the
383 unmatched ones are left out.

**Request:** none. `?include_no_epg=1` returns the complete 1,272-channel
catalog instead (useful for debugging coverage, or for a client that wants
to show a channel even without a schedule).

**Response 200:**
```json
{
  "success": true,
  "channels": {
    "Sport": { "NBA TV": { "url": ["..."], "url_hd": "", "image": "", "epg_id": "...", "epg_source": "..." } },
    "Movie": { "...": "..." }
  },
  "n_channels": 889
}
```

The filter is applied **at request time**, not in the catalog:

- The EPG pipeline still sees all 1,272 channels, so a channel can pick up a
  match on a later run.
- `/get-channel-video-url` still resolves any channel that was ever in the
  catalog (it looks up `ALL_CHANNELS`, not the filtered response).
- `/epg-status` still reports the full picture — total 1,272, covered 889,
  unmatched 383 — plus the list of unmatched names.

Categories that end up empty after filtering are omitted entirely.

---

## 5 · Daily refresh pipeline

`fetch_epg_daily.py` does six things in order:

1. **Builds the catalog in-memory** from
   [api/tv_channels.py:ALL_CHANNELS_NOT_SORTED](tv_channels.py). No
   `catalog.json` is written or read. Channel names are upper-cased so the
   resulting `epg.json` keys match `tv_channels.ALL_CHANNELS` (which the Flask
   API looks up against). See
   [fetch_epg_daily.py:_build_catalog()](fetch_epg_daily.py).

2. **Imports the upstream pipeline.** `sys.path.insert(0, <epg_source>)`
   then `import fetch_epg`. Defaults `--epg-source` to the script's own
   directory (where the pipeline is vendored).

3. **Patches the pipeline** so it consumes our in-memory catalog instead of
   reading `catalog.json`, then calls `fetch_epg.run(ns)`. Defaults: curated
   77 sources, 2 days of programmes.

4. **Publishes.** `_latest_run_dir()` finds the newest
   `data/<UTC-ts>/` directory in the upstream pipeline. `_publish()` copies
   `epg.json`, `epg_match.json`, `epg_unmatched.json` into
   `api/epg_data/latest/` and writes `meta.json` summarising the run.

5. **Prunes old runs** if `--keep-runs N` is set (default 1). Each run mirror
   in `data/<run-ts>/` is ~60 MB; the default keeps only the latest one so
   disk usage stays flat. Pass `--keep-runs 7` to retain a week of history.

6. **Exits.** No loop, no in-process scheduler. Returns exit code 0 on success,
   non-zero on failure (1 = pipeline error, 2 = pipeline not importable,
   3 = publish failed). systemd `Type=oneshot` propagates the exit code into
   `systemctl status`.

### First run

The first invocation downloads ~162 MB of XMLTV feeds across 77 sources. After
that `D:\ak47\mokup\egp\cache\` keeps subsequent runs to a few seconds.

### systemd timer (production)

`/etc/systemd/system/epg-fetch.service`:
```ini
[Unit]
Description=TV API EPG fetch
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=epg
WorkingDirectory=/opt/tv-api/api
ExecStart=/usr/bin/python3 /opt/tv-api/api/fetch_epg_daily.py
StandardOutput=journal
StandardError=journal
```

`/etc/systemd/system/epg-fetch.timer`:
```ini
[Unit]
Description=Run EPG fetch daily at 12:00

[Timer]
OnCalendar=*-*-* 12:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now epg-fetch.timer
systemctl list-timers epg-fetch
journalctl -u epg-fetch.service -n 50
```

`Persistent=true` means a missed run (server was off at noon) still fires on
the next boot.

### cron alternative

```cron
0 12 * * * cd /opt/tv-api/api && /usr/bin/python3 fetch_epg_daily.py >> /var/log/epg-fetch.log 2>&1
```

### CLI flags

| Flag | Default | Effect |
|---|---|---|
| `--days N` | 2 | Today + N-1 more days of programmes |
| `--source ID …` | curated | Restrict to specific XMLTV source IDs |
| `--refresh-source ID …` | none | Force re-download of these sources even if cached |
| `--no-fetch` | off | Don't hit the network; reuse cached XMLTV. Default is to re-download every source. |
| `--epg-source PATH` | script's directory | Override the upstream pipeline location |
| `--keep-runs N` | 1 | Keep the N most recent `data/<run-ts>/` directories. Default 1 = overwrite each run, no history. `0` = keep all runs |
| `--verbose` | off | DEBUG logging |

**Note on `--source`:** if you restrict to specific sources, channels that
have an explicit `epg_source` field pointing to an excluded source will fail
silently (their cache file won't exist). The default curated list covers
all 77 sources, which is the safe option.

---

## 6 · Caching strategy

There are two caches in play.

**Server side** — `epg_service.py` keeps an in-process mtime cache per JSON
file. After the first request, subsequent requests don't re-parse. The cache
auto-invalidates when the file's mtime changes (i.e. after the next daily
fetch). See [`_load_json()`](epg_service.py).

**Client side** — every EPG response sets
`Cache-Control: public, max-age=900`. The Android app can poll
`/get-channel-current` every 15 minutes cheaply; the API will reply with
`304 Not Modified` for unchanged data.

---

## 7 · Failure modes

| Symptom | Likely cause |
|---|---|
| `/epg-status` returns 503 | `epg_data/latest/epg.json` doesn't exist — daily job hasn't run yet. Run `python fetch_epg_daily.py` manually. |
| `/get-channel-epg` returns 404 for a known channel | Channel is in `ALL_CHANNELS` but the matcher couldn't find an XMLTV counterpart. Check `epg_data/latest/epg_unmatched.json` — if it's there, the upstream pipeline doesn't have data for that channel. (If you see a 200 with `"programmes": []`, the channel *is* matched but has no programmes in the date window — that's normal, not an error.) |
| `/epg-status` reports an old `last_refresh_utc` | systemd timer / cron is not running. `systemctl status epg-fetch.timer` or check cron logs. |
| Pipeline runs but `meta.json` shows `n_channels_with_epg: 0` | EPG XMLTV feeds unreachable. Check `journalctl -u epg-fetch.service` for HTTP errors. The cache is still updated, just empty. |
| First request is slow | First call to `_load_json()` reads + parses the JSON file (~50 ms for 2 MB). Subsequent requests hit the mtime cache. |

---

## 8 · Operational notes

- **No secrets.** Every XMLTV endpoint hit is plaintext HTTPS — no API keys, no
  cookies, no signing.
- **Disk space.** `api/epg_data/latest/` is ~19 MB (it holds the full 1,272-channel
  catalog). The upstream pipeline retains a per-run mirror at
  `api/data/<run-ts>/` (~60 MB each) — without pruning this directory grows by
  ~2 GB/month. The script's `--keep-runs N` flag (default 1) prunes old run
  dirs at the end of every run. The XMLTV feed cache is ~162 MB and is reused
  between runs.
- **Idempotent re-runs.** Re-running `fetch_epg_daily.py` is safe. The new
  run's outputs overwrite the previous publish; old run dirs in
  `D:\ak47\mokup\egp\data\` stay untouched until pruned.
- **Stale data after a failed run.** If the daily job crashes mid-publish, the
  `epg_data/latest/` directory keeps the previous successful snapshot — the
  API stays up.
- **Channel name casing.** Catalog keys are upper-case (e.g. `"MATCH! FUTBOL 1"`).
  All EPG endpoints accept case-insensitive input and normalise via
  `ALL_CHANNELS` before lookup.

---

## 9 · Where to look in the code

| Question | Look at |
|---|---|
| What does `/epg-status` actually return? | [api.py:epg_status()](api.py) |
| How does `/get-channel-current` find "now"? | [epg_service.py:current_programmes()](epg_service.py) |
| Where does the JSON come from? | [epg_service.py:_load_json()](epg_service.py) |
| How does the daily job publish? | [fetch_epg_daily.py:_publish()](fetch_epg_daily.py) |
| How is the upstream pipeline invoked? | [fetch_epg_daily.py:_run_pipeline()](fetch_epg_daily.py) |
| How is the catalog built in-memory? | [fetch_epg_daily.py:_build_catalog()](fetch_epg_daily.py) |
| Where do explicit `epg_id` mappings come from? | [fetch_epg_daily.py:_collect_explicit_matches()](fetch_epg_daily.py) |
| How do explicit mappings get merged back in? | [fetch_epg_daily.py:_merge_explicit_matches()](fetch_epg_daily.py) |
| How does old-run pruning work? | [fetch_epg_daily.py:_prune_old_runs()](fetch_epg_daily.py) |
| Channel catalog shape | [api/tv_channels.py](tv_channels.py) — `ALL_CHANNELS` |
| Upstream pipeline (vendored in this repo) | [api/fetch_epg.py](fetch_epg.py) |

---

## 10 · DLHD catalog

The DLHD (DaddyLiveHD) site carries ~1,100 additional international
streams. They live outside `tv_channels.py` so that file stays readable:

| File | Role |
|---|---|
| [api/dlhd-channels.json](dlhd-channels.json) | The raw channel list (`letter`, `name`, `id`, `watchUrl`) |
| [api/dlhd_epg_mapping.json](dlhd_epg_mapping.json) | Generated + hand-audited `name → {epg_id, epg_source}` table (683 entries) |
| [api/dlhd_channels.py](dlhd_channels.py) | Turns the two files above into catalog entries |

`tv_channels.py` merges the DLHD catalog into `ALL_CHANNELS_NOT_SORTED`
at import time, so every consumer (Flask API, EPG pipeline, Android
app) sees one unified list of **1,272 channels**. A DLHD entry whose name
already exists anywhere in the curated catalog is skipped, so no channel is
listed twice (the DLHD list duplicates `BTV ACTION`, `TLC` and
`TRAVEL CHANNEL`).

**Categories.** DLHD exposes no genre metadata, so the category is
inferred from the channel name using the keyword table in
`dlhd_channels._CATEGORY_RULES`. Anything unrecognised lands in
`Worldwide`.

**Explicit vs fuzzy matching.** Every DLHD channel with a mapping in
`dlhd_epg_mapping.json` gets an explicit `epg_id` / `epg_source` and
bypasses the fuzzy matcher. The 428 channels without a mapping carry the
marker `epg_excluded: True` — `fetch_epg_daily._build_catalog()` keeps
them out of the fuzzy catalog entirely, because the DLHD names contain
many near-collisions ("TNT USA" vs "TNT Brasil", "RTP 3 Portugal" vs
"RTP 3 Switzerland") that a fuzzy matcher gets wrong. They still show up
in `epg_unmatched.json` (and therefore in `/epg-status`) so the coverage
report stays truthful.

**Stream URLs** point at the site's current host,
`https://thedaddy.pk/watch.php?id=<id>` — `dlive.sx` 301-redirects
there. The `dlhd_id` field on each channel carries the raw id.

**Sources.** Covering the DLHD catalog needs far broader EPG coverage
than the original 21 curated feeds, so `sources.SOURCE_IDS` was widened
to **77 feeds** (US_LOCALS1, US_SPORTS1, PLEX1, IN1, AE1, CA2, CH1,
BR1/BR2, MX1, TR3, …). Four ids were dropped because they 404 upstream:
`US1`, `ALL_AT1`, `MK1`, plus `TW1` / `CN1`. (`ALL_AT1` was a
pre-existing bug — Austria's feed is `AT1`.)

**Date shifting.** The `globetvapp/epg` upstream generates its dates
around Nov 2025, so the standard today+N-day window would filter the
whole file out. `fetch_epg_daily._shift_source_dates_to_today()` shifts
all programme dates in the `GLOBETV1` / `GLOBETV2` cache files forward so
the earliest one lands on today. It runs after each download and is
idempotent.

**What the client sees.** Only the EPG-covered channels are served —
`/get-all-channels` returns 889, not 1,272 (see §4.6). The 383 channels
with no usable schedule are dropped from the response so the app doesn't
render empty "now playing" rows, but they stay in the catalog so the daily
job keeps trying them.

