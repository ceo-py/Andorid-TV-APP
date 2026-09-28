# API

Flask app serving TV channel data + EPG (Electronic Program Guide).

**Base URL:** `https://tv-api.ceo-py.eu`

## Endpoints

| Method | Path | Body / Query | Returns |
|---|---|---|---|
| `POST` | `/get-channel-video-url` | `{"channel_type": "...", "channel_name": "..."}` | Resolved live stream URL |
| `GET` | `/get-all-channels` | — | Full channel catalog |
| `GET` | `/epg-status` | — | When EPG was last refreshed + coverage stats |
| `GET` | `/get-channel-epg` | `?channel_type=&channel_name=&date=YYYY-MM-DD` | All programmes for one channel |
| `GET` | `/get-channel-current` | `?channel_name=` | What's playing now + what's next |
| `GET` | `/get-current-all` | `?channel_type=` (optional) | What's airing on every channel right now |
| `GET` | `/get-all-epg` | — | Full EPG dict (large; ~2 MB) |

EPG responses include a `Cache-Control: public, max-age=900` header.

## Quick examples

```bash
# Refresh status + unmatched list
curl https://tv-api.ceo-py.eu/epg-status | python3 -m json.tool

# What's playing now on AMC
curl 'https://tv-api.ceo-py.eu/get-channel-current?channel_name=AMC' | python3 -m json.tool

# Full schedule for one channel
curl 'https://tv-api.ceo-py.eu/get-channel-epg?channel_type=Sport&channel_name=MATCH%21%20Futbol%201' | python3 -m json.tool
```

## Run the API

```bash
cd /opt/tv-api/api     # or wherever you deploy it
python api.py
```

## EPG daily refresh

The EPG pipeline modules (`config.py`, `fetch_epg.py`, `matchers.py`,
`sources.py`, `xmltv.py`) live **in this directory** alongside the Flask app.
`fetch_epg_daily.py` imports them in-place — `--epg-source` defaults to the
directory the script itself lives in.

The script is **one-shot**: fetch → publish → exit. Trigger it from systemd,
cron, or run it manually.

### Where channels come from

`tv_channels.ALL_CHANNELS_NOT_SORTED` is the single source of truth for the
channel catalog. `fetch_epg_daily.py` builds an in-memory `fetch_epg.Catalog`
from it on every run and patches the pipeline to consume that catalog instead
of reading a JSON file. No `catalog.json` is written or required.

### 100 %-accurate matching for specific channels

The upstream fuzzy matcher gets ~95 % of channels right, but the wrong 5 %
matter — they show the wrong schedule. To pin a channel to a specific XMLTV
feed entry, add two optional fields to its `tv_channels.py` entry:

```python
"AMC": {
    "url": [...],
    "url_hd": "...",
    "image": "...",
    "epg_id": "AMC.bg",          # XMLTV channel id
    "epg_source": "BG1",         # XMLTV source id (BG1, IT1, DE1, ...)
},
```

When both fields are set, the channel bypasses fuzzy matching entirely and
uses the exact id from the named source. The full workflow + tips for finding
the right `epg_id` are in [EPG.md](EPG.md#explicit-epg-ids-in-tv_channelspy).

### First-time bootstrap

```bash
cd /opt/tv-api/api
python fetch_epg_daily.py
```

The first run downloads ~58 MB of XMLTV feeds (~30 s on a fast link) into
`cache/`. Subsequent runs reuse the cache.

### systemd timer (recommended on Linux)

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

# Useful commands
systemctl list-timers epg-fetch
systemctl status epg-fetch.service
journalctl -u epg-fetch.service -n 50
```

`Persistent=true` catches up on missed runs after the box was off, so the
12:00 trigger will still fire if the server was down at noon.

### cron alternative

```cron
0 12 * * * cd /opt/tv-api/api && /usr/bin/python3 fetch_epg_daily.py >> /var/log/epg-fetch.log 2>&1
```

### CLI options

```
python fetch_epg_daily.py                          # default: re-download every source (fresh data), 2 days, no history
python fetch_epg_daily.py --days 3                 # keep 3 days of programmes
python fetch_epg_daily.py --source BG1 IT1         # restrict to a subset (still re-downloads them)
python fetch_epg_daily.py --refresh-source BG1     # force re-download only BG1 (others use cache)
python fetch_epg_daily.py --keep-runs 7            # retain last 7 data/<run-ts>/ dirs as history
python fetch_epg_daily.py --keep-runs 0            # never prune (disk keeps growing)
python fetch_epg_daily.py --no-fetch               # use cache, skip network
python fetch_epg_daily.py --epg-source /opt/egp    # point at a different location
```

By default the script always re-downloads every source it uses (≈58 MB / day).
Pass `--no-fetch` to skip the network and reuse the cached XMLTV files instead.

Exit codes:
- `0` — success
- `1` — pipeline returned an error
- `2` — pipeline module not found / not importable
- `3` — publish step failed

## Directory layout

```
api/
├── api.py                  # Flask app + endpoints
├── tv_channels.py          # Channel catalog + video URL extractors
├── epg_service.py          # Read-side helpers for EPG JSON
├── fetch_epg_daily.py      # One-shot fetch + publish
│
├── # EPG pipeline modules (imported by fetch_epg_daily.py)
├── fetch_epg.py            # CLI entrypoint of the upstream pipeline
├── config.py               # Pipeline config (paths, threshold, parallelism)
├── matchers.py             # Fuzzy channel name matcher
├── sources.py              # XMLTV source ID list
├── xmltv.py                # Streaming XMLTV parser
│                           # (channels come from tv_channels.ALL_CHANNELS_NOT_SORTED in-memory)
│
├── epg_data/
│   └── latest/             # Populated by fetch_epg_daily.py (consumed by API)
│       ├── epg.json
│       ├── epg_match.json
│       ├── epg_unmatched.json
│       └── meta.json
│
├── cache/                  # Cached XMLTV feeds (~58 MB on first run)
├── data/                   # Per-run mirrors of the upstream pipeline output
│
├── assets/                 # Static category icons
├── test.py                 # Standalone Playwright test for video extraction
└── api.wsgi, myflaskapp.conf   # Apache mod_wsgi deployment configs
```

The `cache/` and `data/` directories are populated at runtime and should be
git-ignored.

## Deploying

`api.wsgi` and `myflaskapp.conf` are templates for an Apache mod_wsgi setup.
The `epg_service` module reads from `epg_data/latest/` relative to its own
location, so as long as `api/epg_data/latest/epg.json` is populated the API
works the same in development and in production.
