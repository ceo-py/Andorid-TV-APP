# Andorid-TV-APP

Android TV app plus the Flask API that serves its channel catalog and
Electronic Program Guide (EPG).

## Layout

| Path | What |
|---|---|
| [`api/`](api/) | Flask API + EPG pipeline — see **[api/README.md](api/README.md)** for endpoints, the daily refresh job, and how the DLHD catalog is wired in |
| [`api/EPG.md`](api/EPG.md) | Deep dive on the EPG pipeline: data layout, matching, caching, failure modes |
| `app/iLiveTV/` | React Native app (older build) |
| `app/TVApp/` | Android app workspace |
| `releases/` | Built APKs |

## API at a glance

**Base URL:** `https://tv-api.ceo-py.eu`

| Method | Path | Returns |
|---|---|---|
| `POST` | `/get-channel-video-url` | Resolved live stream URL |
| `GET` | `/get-all-channels` | Channel catalog — the 889 channels that have EPG (`?include_no_epg=1` for all 1,272) |
| `GET` | `/epg-status` | Last refresh time + coverage stats |
| `GET` | `/get-channel-epg` | Full schedule for one channel |
| `GET` | `/get-channel-current` | What's playing now + what's next |
| `GET` | `/get-current-all` | What's airing on every channel right now |
| `GET` | `/get-all-epg` | Full EPG dict (~17 MB, filterable by `?source=` / `?category=` / `?channels=`) |
| `GET` | `/server-time` | Server's UTC clock, for client clock-skew sync |

## Channel catalog

The catalog merges two sources into one list of **1,272 channels**:

- **167 curated Bulgarian channels** — hand-maintained in
  [`api/tv_channels.py`](api/tv_channels.py), each with stream URLs, a logo,
  and an optional explicit XMLTV mapping (`epg_id` + `epg_source`).
- **1,105 DLHD international channels** — the DaddyLiveHD catalog in
  [`api/dlhd-channels.json`](api/dlhd-channels.json), categorised and
  EPG-mapped by [`api/dlhd_channels.py`](api/dlhd_channels.py).

**889 channels have EPG** across 51 XMLTV sources, ~41,900 programmes in the
2-day window. `/get-all-channels` serves **only those 889** — a channel with
no schedule would render as an empty "now playing" row. The 383 without are
channels no free feed carries: US local stations addressed by market rather
than by name, country-specific variants with no matching feed, reality-show
multicams, and the 20 `18+` adult player feeds. They stay in the catalog so
the daily job keeps trying them, and `/epg-status` still reports them.

See [api/README.md](api/README.md) for the full picture: how matching works,
the `epg_excluded` opt-out, the 77 XMLTV feeds, the stale-date workaround for
`globetvapp`, and the `/get-all-epg` filters.

## Releases

- [iLiveTV-v1.apk](releases/iLiveTV-v1.apk) — Initial release
- [iLiveTV-v2.apk](releases/iLiveTV-v2.apk) — Initial release
- [iLiveTV-v3.apk](releases/iLiveTV-v3.apk) — Initial release
- [iLiveTV-v3.01.apk](releases/iLiveTV-v3.01.apk) — Initial release
- [iLiveTV-v3.02.apk](releases/iLiveTV-v3.02.apk) — Initial release
- [iLiveTV-v3.03.apk](releases/iLiveTV-v3.03.apk) — Initial release
- [iLiveTV-v3.04.apk](releases/iLiveTV-v3.04.apk) — Initial release
- [iLiveTV-v3.05.apk](releases/iLiveTV-v3.05.apk) — Initial release
- [iLiveTV-v3.06.apk](releases/iLiveTV-v3.06.apk) — Initial release
