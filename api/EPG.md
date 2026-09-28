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

# Full schedule for one channel
curl 'https://tv-api.ceo-py.eu/get-channel-epg?channel_type=Sport&channel_name=MATCH%21%20Futbol%201' | python3 -m json.tool
```

## 1 · What this is

Four new endpoints on the existing Flask API that return **what's playing now**,
**what's coming up**, and **the full schedule** for every channel in the
catalog at [api/tv_channels.py](api/tv_channels.py). The API itself does no
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
        |  2. runs api/fetch_epg.py (imported)        |
        |  3. matches 152 channels -> 145 (95 %)      |
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
| [api/fetch_epg_daily.py](api/fetch_epg_daily.py) | One-shot script. Imports and runs [api/fetch_epg.py](api/fetch_epg.py) (which lives in the same directory), then publishes the result into `api/epg_data/latest/`. Triggered by systemd / cron — no in-process scheduler. |
| [api/fetch_epg.py](api/fetch_epg.py) | CLI entrypoint of the upstream pipeline. Matches catalog channels against XMLTV feeds, emits `epg.json` + `epg_match.json` + `epg_unmatched.json` into `api/data/<run-ts>/`. |
| [api/config.py](api/config.py), [api/matchers.py](api/matchers.py), [api/sources.py](api/sources.py), [api/xmltv.py](api/xmltv.py) | Pipeline internals (paths, fuzzy matcher, source list, XMLTV parser). |
| [api/epg_service.py](api/epg_service.py) | Read-side helpers: `load_epg()`, `load_match()`, `load_meta()`, `load_unmatched()`, `current_programmes()`, `channels_with_epg()`, `is_available()`. In-process mtime cache so repeated requests don't re-parse JSON. |
| [api/api.py](api/api.py) | Flask app. Adds four EPG routes. Existing `/get-channel-video-url` and `/get-all-channels` are unchanged. |

The pipeline modules (`fetch_epg.py`, `config.py`, `matchers.py`, `sources.py`,
`xmltv.py`) live **in this directory** — the API repo is self-contained.
`--epg-source` defaults to `Path(__file__).parent`, so running
`python fetch_epg_daily.py` from anywhere Just Works as long as the script
lives next to those modules. See
[fetch_epg_daily.py:65](api/fetch_epg_daily.py#L65) for the default-path
logic.

The channel catalog comes from
[api/tv_channels.py:ALL_CHANNELS_NOT_SORTED](api/tv_channels.py) — no
`catalog.json` is required. [fetch_epg_daily._build_catalog()](api/fetch_epg_daily.py)
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

[fetch_epg_daily._collect_explicit_matches()](api/fetch_epg_daily.py) collects
the explicit mappings, [fetch_epg_daily._build_catalog()](api/fetch_epg_daily.py)
filters them out of the fuzzy catalog, and
[fetch_epg_daily._merge_explicit_matches()](api/fetch_epg_daily.py) merges
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

The full list of source IDs is in [sources.py:ALL_SOURCE_IDS](api/sources.py) —
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

The directory is populated by [fetch_epg_daily.py:_publish()](api/fetch_epg_daily.py). The API reads from it on every EPG request.

### `epg.json` shape

Top-level is a dict keyed by **catalog channel name** (matches the keys in
[api/tv_channels.py:ALL_CHANNELS](api/tv_channels.py)). Values are sorted
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
[api.py:_cache_control()](api/api.py).

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
    "n_channels_with_epg": 145,
    "n_channels_total": 152,
    "n_programmes": 5161,
    "sources_used": ["BG1", "IT1", "DE1", "..."]
  },
  "unmatched": [
    { "name": "PULSE ROCK", "category": "Music", "url": ["..."] }
  ],
  "data_dir": "D:\\VSC\\Andorid-TV-APP\\api\\epg_data\\latest"
}
```

**Response 503** — the daily job hasn't run yet:
```json
{ "success": false, "error": "EPG not yet generated — run fetch_epg_daily.py" }
```

### 4.2 · `GET /get-channel-epg`

Full programme list for one channel (today + tomorrow by default).

**Query params:**
- `channel_name` — case-insensitive
- `channel_type` — optional, speeds up the lookup

**Request:**
```
GET /get-channel-epg?channel_type=Sport&channel_name=MATCH!%20Futbol%201
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
  "programmes": [ { "...": "see epg.json shape" } ]
}
```

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

Full EPG dict. **Heavy — ~2 MB.** Clients should prefer
`/get-channel-epg` or `/get-channel-current` per channel and cache.

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

---

## 5 · Daily refresh pipeline

`fetch_epg_daily.py` does six things in order:

1. **Builds the catalog in-memory** from
   [api/tv_channels.py:ALL_CHANNELS_NOT_SORTED](api/tv_channels.py). No
   `catalog.json` is written or read. Channel names are upper-cased so the
   resulting `epg.json` keys match `tv_channels.ALL_CHANNELS` (which the Flask
   API looks up against). See
   [fetch_epg_daily.py:_build_catalog()](api/fetch_epg_daily.py).

2. **Imports the upstream pipeline.** `sys.path.insert(0, <epg_source>)`
   then `import fetch_epg`. Defaults `--epg-source` to the script's own
   directory (where the pipeline is vendored).

3. **Patches the pipeline** so it consumes our in-memory catalog instead of
   reading `catalog.json`, then calls `fetch_epg.run(ns)`. Defaults: curated
   21 sources, 2 days of programmes.

4. **Publishes.** `_latest_run_dir()` finds the newest
   `data/<UTC-ts>/` directory in the upstream pipeline. `_publish()` copies
   `epg.json`, `epg_match.json`, `epg_unmatched.json` into
   `api/epg_data/latest/` and writes `meta.json` summarising the run.

5. **Prunes old runs** if `--keep-runs N` is set (default 7). Each run mirror
   in `data/<run-ts>/` is ~60 MB; without pruning this directory grows by
   ~2 GB/month.

6. **Exits.** No loop, no in-process scheduler. Returns exit code 0 on success,
   non-zero on failure (1 = pipeline error, 2 = pipeline not importable,
   3 = publish failed). systemd `Type=oneshot` propagates the exit code into
   `systemctl status`.

### First run

The first invocation downloads ~58 MB of XMLTV feeds across 21 sources. After
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
| `--no-fetch` | off | Don't hit the network; reuse cached XMLTV |
| `--epg-source PATH` | script's directory | Override the upstream pipeline location |
| `--keep-runs N` | 7 | Keep the N most recent `data/<run-ts>/` directories. `0` = keep all |
| `--verbose` | off | DEBUG logging |

**Note on `--source`:** if you restrict to specific sources, channels that
have an explicit `epg_source` field pointing to an excluded source will fail
silently (their cache file won't exist). The default curated list covers
all 21 sources, which is the safe option.

---

## 6 · Caching strategy

There are two caches in play.

**Server side** — `epg_service.py` keeps an in-process mtime cache per JSON
file. After the first request, subsequent requests don't re-parse. The cache
auto-invalidates when the file's mtime changes (i.e. after the next daily
fetch). See [`_load_json()`](api/epg_service.py).

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
- **Disk space.** `api/epg_data/latest/` is small (~2 MB). The upstream pipeline
  retains a per-run mirror at `api/data/<run-ts>/` (~60 MB each) — without
  pruning this directory grows by ~2 GB/month. The script's `--keep-runs N`
  flag (default 7) prunes old run dirs at the end of every run.
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
| What does `/epg-status` actually return? | [api.py:epg_status()](api/api.py) |
| How does `/get-channel-current` find "now"? | [epg_service.py:current_programmes()](api/epg_service.py) |
| Where does the JSON come from? | [epg_service.py:_load_json()](api/epg_service.py) |
| How does the daily job publish? | [fetch_epg_daily.py:_publish()](api/fetch_epg_daily.py) |
| How is the upstream pipeline invoked? | [fetch_epg_daily.py:_run_pipeline()](api/fetch_epg_daily.py) |
| How is the catalog built in-memory? | [fetch_epg_daily.py:_build_catalog()](api/fetch_epg_daily.py) |
| Where do explicit `epg_id` mappings come from? | [fetch_epg_daily.py:_collect_explicit_matches()](api/fetch_epg_daily.py) |
| How do explicit mappings get merged back in? | [fetch_epg_daily.py:_merge_explicit_matches()](api/fetch_epg_daily.py) |
| How does old-run pruning work? | [fetch_epg_daily.py:_prune_old_runs()](api/fetch_epg_daily.py) |
| Channel catalog shape | [api/tv_channels.py](api/tv_channels.py) — `ALL_CHANNELS` |
| Upstream pipeline (vendored in this repo) | [api/fetch_epg.py](api/fetch_epg.py) |
