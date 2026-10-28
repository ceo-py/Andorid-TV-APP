# API

Flask app serving TV channel data + EPG (Electronic Program Guide).

**Base URL:** `https://tv-api.ceo-py.eu`

## Endpoints

| Method | Path | Body / Query | Returns |
|---|---|---|---|
| `POST` | `/get-channel-video-url` | `{"channel_type": "...", "channel_name": "..."}` | Resolved live stream URL |
| `GET` | `/get-all-channels` | `?include_no_epg=1` (optional) | Channel catalog — only the EPG-covered channels (889) |
| `GET` | `/epg-status` | — | When EPG was last refreshed + coverage stats |
| `GET` | `/get-channel-epg` | `?channel_type=&channel_name=&date=YYYY-MM-DD` | All programmes for one channel |
| `GET` | `/get-channel-current` | `?channel_name=` | What's playing now + what's next |
| `GET` | `/get-current-all` | `?channel_type=` (optional) | What's airing on every channel right now |
| `GET` | `/get-all-epg` | `?source=&category=&channels=` (optional) | Full EPG dict (~17 MB). Client computes current locally. |
| `GET` | `/server-time` | — | Server's current UTC time. Clients use this to sync their clock. |

EPG responses are cacheable. `/get-all-epg` uses `Cache-Control: public, max-age=86400`
(24 h) since the data refreshes only once per day; other EPG endpoints use
`max-age=900` (15 min). `/get-all-epg` also returns `ETag` + `Last-Modified` so
clients can cheaply revalidate via `If-None-Match` / `If-Modified-Since`
(the server replies `304 Not Modified` when the daily fetch hasn't run since
the client's cached copy). `/server-time` is `Cache-Control: no-store`.

### Only EPG-covered channels are served

`/get-all-channels` returns **only the 889 channels the matcher actually
covered**. A channel with no schedule would render as an empty "now playing"
row, which is noise for the user — so the 383 unmatched ones are left out.

The filter is applied at request time, not in the catalog:

- The EPG pipeline still sees all 1,272 channels, so a channel can pick up a
  match on a later run.
- `/get-channel-video-url` still resolves any channel that was ever in the
  catalog.
- `/epg-status` still reports the full picture (total 1,272, covered 889,
  unmatched 383) plus the list of unmatched channels.

`?include_no_epg=1` returns the complete 1,272-channel catalog instead — useful
for debugging coverage and for clients that want to show a channel even
without a schedule.

```bash
# Default — 889 channels with EPG
curl https://tv-api.ceo-py.eu/get-all-channels

# Full catalog, EPG or not — 1,272 channels
curl 'https://tv-api.ceo-py.eu/get-all-channels?include_no_epg=1'
```

### Filtering `/get-all-epg`

The full payload grew to ~17 MB once the DLHD catalog was added (1,272
channels × 51 XMLTV sources). Clients that only need a slice can ask for
it instead of pulling everything. Filters combine with AND; with no filter
the response is byte-identical to the unfiltered one, so existing clients
are unaffected.

| Parameter | Example | Effect | Size |
|---|---|---|---|
| `source` | `?source=BG1,GLOBETV2,IPTVEPG_BG` | Only programmes from these XMLTV sources | 2.6 MB |
| `category` | `?category=Sport,Movie` | Only these catalog categories | 4.1 MB |
| `channels` | `?channels=AMC%20USA,BNT%203` | Only these channel names (exact) | 50 KB |

A filtered response gets its own `ETag` (refresh timestamp **+** the filter
set), so a client holding the full-payload ETag never gets a `304` for a
different slice.

## Quick examples

```bash
# Refresh status + unmatched list
curl https://tv-api.ceo-py.eu/epg-status | python3 -m json.tool

# What's playing now on AMC (single channel)
curl 'https://tv-api.ceo-py.eu/get-channel-current?channel_name=AMC' | python3 -m json.tool

# What's playing on a DLHD channel (e.g. from the international catalog)
curl 'https://tv-api.ceo-py.eu/get-channel-current?channel_name=AMC%20USA' | python3 -m json.tool

# What's airing on every channel right now (bulk)
curl https://tv-api.ceo-py.eu/get-current-all | python3 -m json.tool

# Full schedule for one channel
curl 'https://tv-api.ceo-py.eu/get-channel-epg?channel_type=Sport&channel_name=MATCH%21%20Futbol%201' | python3 -m json.tool

# Just the Bulgarian EPG — 2.6 MB instead of 17 MB
curl 'https://tv-api.ceo-py.eu/get-all-epg?source=BG1,GLOBETV2,IPTVEPG_BG' -o epg-bg.json

# Just one category
curl 'https://tv-api.ceo-py.eu/get-all-epg?category=Sport' -o epg-sport.json

# Server clock — sync before computing "now" locally
curl https://tv-api.ceo-py.eu/server-time | python3 -m json.tool
```

## Recommended client pattern

1. On app start, call `GET /server-time` to get the server's UTC clock and epoch_ms.
2. Call `GET /get-all-epg` once — full schedule, ~17 MB, cacheable for **24 h**
   (`Cache-Control: public, max-age=86400` since data refreshes only once a day).
   Pass `If-Modified-Since` or `If-None-Match` on subsequent fetches — the
   server returns `304 Not Modified` if the daily fetch hasn't run since your
   cached copy (cheap revalidation, no body transfer).

   On a mobile connection prefer a filtered fetch —
   `?source=BG1,GLOBETV2,IPTVEPG_BG` is 2.6 MB and covers the whole Bulgarian
   market, or `?category=Sport` is 4.1 MB. The unfiltered payload is only
   needed if the client wants every international channel.
3. Compute "what's on now" **locally** by walking each channel's programmes whose
   `[start, stop)` contains the synced server time. No further round-trips until
   the data goes stale (>24 h, or until the server returns 200 with new data).
4. On any user action that needs a single channel detail (`/get-channel-epg`),
   the server can do the heavy lifting.

This keeps the Android app snappy: one bulk fetch per session, then everything
is local computation.

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

The catalog has **two** sources, merged into one list at import time:

| Source | Channels | Where |
|---|---|---|
| Curated Bulgarian catalog | 167 | `tv_channels.ALL_CHANNELS_NOT_SORTED` |
| DLHD (DaddyLiveHD) international catalog | 1,105 | `dlhd-channels.json` → `dlhd_channels.build_dlhd_catalog()` |

`tv_channels.py` merges the DLHD catalog into `ALL_CHANNELS_NOT_SORTED` when it
is imported, so every downstream consumer (Flask API, EPG pipeline, Android
app) sees one unified list of **1,272 channels** in 7 categories. A DLHD entry
whose name already exists in the curated catalog is skipped, so no channel is
listed twice.

`fetch_epg_daily.py` builds an in-memory `fetch_epg.Catalog` from that merged
dict on every run and patches the pipeline to consume it instead of reading a
JSON file. No `catalog.json` is written or required.

#### DLHD catalog

The DLHD site carries ~1,100 additional international streams. They live
outside `tv_channels.py` so that file stays readable:

| File | Role |
|---|---|
| `dlhd-channels.json` | The raw channel list (`letter`, `name`, `id`, `watchUrl`) |
| `dlhd_epg_mapping.json` | Generated + hand-audited `name → {epg_id, epg_source}` table (683 entries) |
| `dlhd_channels.py` | Turns the two files above into catalog entries |

**Categories.** DLHD exposes no genre metadata, so the category is inferred
from the channel name using the keyword table in
`dlhd_channels._CATEGORY_RULES`. Anything unrecognised lands in `Worldwide`.

**Stream URLs** point at the site's current host,
`https://thedaddy.pk/watch.php?id=<id>` — `dlive.sx` 301-redirects there. The
raw id is kept in the `dlhd_id` field of each channel.

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

### Opting a channel out of matching entirely

Some channels have no trustworthy EPG at all. Adding a third field,
`epg_excluded: True`, keeps the channel out of the fuzzy matcher *and* out of
the explicit lookup — the pipeline publishes nothing for it rather than
publishing something wrong:

```python
"ASTRO SUPERSPORT 1": {
    "url": [...],
    "url_hd": "",
    "image": "",
    "epg_id": "",
    "epg_source": "",
    "epg_excluded": True,   # no trustworthy EPG exists — don't guess
},
```

Excluded channels still appear in `epg_unmatched.json` (and therefore in
`/epg-status`), so the coverage report stays truthful rather than silently
under-counting.

This matters most for the DLHD catalog, whose names contain many
near-collisions — `TNT USA` vs `TNT Brasil`, `RTP 3 Portugal` vs
`RTP 3 Switzerland`, `ABC USA` vs `ABC Australia`. A fuzzy matcher happily
picks one of them and shows the wrong country's schedule.

### First-time bootstrap

```bash
cd /opt/tv-api/api
python fetch_epg_daily.py
```

The first run downloads ~162 MB of XMLTV feeds across 77 sources (~60 s on a
fast link) into `cache/`. Subsequent runs reuse the cache.

### XMLTV sources

`sources.py` holds two lists:

- `SOURCE_IDS` — the curated set the daily job downloads (77 feeds). Order is
  priority for matching: earlier entries win ties.
- `ALL_SOURCE_IDS` — every id the upstream site is known to publish, used by
  `fetch_epg.py --list-sources`.

Most feeds live on `epgshare01.online` at
`https://epgshare01.online/epgshare01/epg_ripper_<ID>.xml.gz`. Three live
elsewhere and have hard-coded URLs in `sources.url_for()`:

| Source | URL | Why |
|---|---|---|
| `GLOBETV1` / `GLOBETV2` | `raw.githubusercontent.com/globetvapp/epg/main/Bulgaria/bulgaria{1,2}.xml.gz` | Bulgarian HD channel variants (BNT 3/4, Planeta HD/Folk, Balkanika, Fen, SKAT, Travel TV, 7/8 TV) |
| `IPTVEPG_BG` | `iptv-epg.org/files/epg-bg.xml.gz` | Bulgarian feed with Latin channel ids (fills E Kids) |

The curated list was widened from 21 to 77 feeds to cover the DLHD catalog
(`US_LOCALS1` alone contributes 4,471 channels, `US_SPORTS1`, `PLEX1`, `IN1`,
`AE1`, `CA2`, `CH1`, `BR1`/`BR2`, `MX1`, `TR3` and more).

Four ids were **removed** because they 404 upstream: `US1`, `ALL_AT1`,
`MK1`, and (newly added) `TW1` / `CN1`. Note `ALL_AT1` was a pre-existing bug
— Austria's feed is `AT1`.

### Stale upstream dates

The `globetvapp/epg` upstream generates its programme dates around **Nov 2025**
regardless of when the file is fetched. The pipeline normally keeps only
`today + N` days, so that whole file would be filtered out and the channels
would show no EPG.

`fetch_epg_daily._shift_source_dates_to_today()` fixes this: after each
download it shifts every programme date in the `GLOBETV1` / `GLOBETV2` cache
files forward so the earliest one lands on today. It is idempotent (a file
whose earliest date is already current is left alone), refuses shifts larger
than 400 days, and runs before the explicit-match merge step so the merge
sees already-shifted dates.

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

By default the script always re-downloads every source it uses (≈162 MB / day
across 77 feeds). Pass `--no-fetch` to skip the network and reuse the cached
XMLTV files instead.

Exit codes:
- `0` — success
- `1` — pipeline returned an error
- `2` — pipeline module not found / not importable
- `3` — publish step failed
- `4` — the DLHD catalog failed to load (corrupt or missing JSON). The run
  is abandoned rather than publishing a snapshot missing ~1,100 channels;
  the previous snapshot stays published and the API keeps serving it.
  Fix with `git checkout -- api/dlhd-channels.json api/dlhd_epg_mapping.json`
  and re-run.

### Runtime

The DLHD catalog pushed the run from ~8 minutes to ~13 seconds. Where the
time went, and what changed:

| Phase | Before | After | Fix |
|---|---|---|---|
| Channel pass (parse 1.7 GB of XML) | 52 s | ~0 s | Parsed channel index cached per feed in `cache/.chindex/`, keyed on the feed's `(size, mtime)` so a re-download invalidates it |
| Fuzzy matching | 71 s | 2 s | `matchers.prepare_candidates()` normalises each source channel once instead of once per comparison; token sets are pre-built too |
| Explicit-match merge | 414 s | 8 s | `list_programmes()` re-parsed the whole feed per channel. Now grouped by source and parsed **once** per feed |
| Programme pass (repeat runs) | 8 s | ~0 s | Wanted programmes cached per feed, same `(size, mtime)` key |
| Downloads | 4 threads | 8 threads | `config.PARALLEL_DOWNLOADS` — the fetch is network-bound |

A cold run (fresh downloads, empty cache) is ~1 min 50 s; a warm run
(reusing the cache) is ~13 s. The output is byte-identical either way.

The caches live in `api/cache/.chindex/` and are git-ignored with the rest
of `api/cache/`. Delete that directory to force a full re-parse.

## Directory layout

```
api/
├── api.py                  # Flask app + endpoints
├── tv_channels.py          # Curated channel catalog + video URL extractors
├── dlhd_channels.py        # DLHD catalog builder (categories + EPG mappings)
├── dlhd-channels.json      # Raw DLHD channel list (1,111 rows)
├── dlhd_epg_mapping.json   # Audited name → {epg_id, epg_source} table (683)
├── epg_service.py          # Read-side helpers for EPG JSON
├── fetch_epg_daily.py      # One-shot fetch + publish
│
├── # EPG pipeline modules (imported by fetch_epg_daily.py)
├── fetch_epg.py            # CLI entrypoint of the upstream pipeline
├── config.py               # Pipeline config (paths, threshold, parallelism)
├── matchers.py             # Fuzzy channel name matcher
├── sources.py              # XMLTV source ID list + per-source URLs
├── xmltv.py                # Streaming XMLTV parser
│                           # (channels come from tv_channels.ALL_CHANNELS_NOT_SORTED in-memory)
│
├── epg_data/
│   └── latest/             # Populated by fetch_epg_daily.py (consumed by API)
│       ├── epg.json        # {channel_name: [programmes]}
│       ├── epg_match.json  # {channel_name: {xmltv_id, source, score, …}}
│       ├── epg_unmatched.json
│       └── meta.json
│
├── cache/                  # Cached XMLTV feeds (~162 MB on first run)
├── data/                   # Per-run mirrors of the upstream pipeline output
│
├── assets/                 # Static category icons
├── test.py                 # Standalone Playwright test for video extraction
└── api.wsgi, myflaskapp.conf   # Apache mod_wsgi deployment configs
```

The `cache/` and `data/` directories are populated at runtime and should be
git-ignored.

## Current coverage

| Metric | Value |
|---|---|
| Channels in catalog | 1,272 |
| **Channels served by `/get-all-channels`** | **889** (EPG-covered only) |
| Programmes (2-day window) | ~41,900 |
| XMLTV sources used | 51 |
| Channels without EPG (not served) | 383 |
| Categories (served) | Sport 354 · Worldwide 314 · Movie 89 · News 41 · Music 53 · Science 25 · Kids 13 |

The 383 without EPG are channels no free feed carries — US local stations
addressed by market (`ABC NY`, `CW Philly`) rather than by name, country-
specific variants with no matching feed (`Canal+ Sport 1 Afrique`,
`Astro SuperSport 1-4`), reality-show multicams, and the 20 `18+` adult
player feeds. They stay in the catalog (so the pipeline keeps trying them)
but are not served to clients.

## Notes and caveats

- **DLHD has no free EPG of its own.** `dlive.sx` 301-redirects everything to
  `thedaddy.pk` (the rebranded site). There is no XMLTV feed — ~70 candidate
  paths were probed, all 404. The only schedule data on the platform is a
  live-sports fixture list keyed by hash ids (not the 24/7 channel ids), and
  the real per-channel API is key-gated. All EPG here comes from the free
  XMLTV feeds above.
- **212 of the 1,111 DLHD channel ids are dead** upstream — the site now
  lists 899 channels. The ids still resolve through the redirect, but the
  stream URLs should be re-verified against the site's
  `/stream/stream-<id>.php` structure.
- **Category labels for DLHD channels are inferred** from the name, not
  authoritative. `dlhd_channels._CATEGORY_RULES` is the single place to
  adjust them.
- **A few feeds carry out-of-range dates** (e.g. `EG1` has 2023 data,
  `US_SPORTS1` reaches 2027). Those simply fall outside the `today + N`
  window and contribute nothing — worth a staleness guard if coverage ever
  looks off.

## Deploying

`api.wsgi` and `myflaskapp.conf` are templates for an Apache mod_wsgi setup.
The `epg_service` module reads from `epg_data/latest/` relative to its own
location, so as long as `api/epg_data/latest/epg.json` is populated the API
works the same in development and in production.
