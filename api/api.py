from flask import Flask, request, jsonify
from tv_channels import ALL_CHANNELS, extract_video_url_default, extract_video_url_gledai_tv, remove_proxy_from_link
import asyncio
from datetime import datetime, timezone
import hashlib

from epg_service import (
    EPG_DIR,
    channels_with_epg,
    channels_with_epg_match,
    current_programmes,
    is_available,
    load_epg,
    load_match,
    load_meta,
    load_unmatched,
    now_playing_all,
    programmes_for_day,
    resolve_channel_match,
)

app = Flask(__name__)


@app.route("/get-channel-video-url", methods=["POST"])
def get_channel():
    data = request.get_json()

    channel_type = data.get("channel_type")
    channel_name = data.get("channel_name")

    if channel_type in ALL_CHANNELS and channel_name in ALL_CHANNELS[channel_type]:
        links = [
            *ALL_CHANNELS[channel_type][channel_name]["url"],
            ALL_CHANNELS[channel_type][channel_name]["url_hd"],
        ]
        url = None

        while links:
            link = links.pop()

            if not link:
                continue

            url = extract_video_url_default(link) if "gledaitv.fan" not in link else asyncio.run(extract_video_url_gledai_tv(link))
            # url = extract_video_url_default(link)

            if len(url) > 0:
                clean_url = remove_proxy_from_link(url)
                return jsonify({"success": True, "url": [clean_url]})

    return jsonify({"success": False, "error": "Channel not found"})


@app.route("/get-all-channels", methods=["GET"])
def get_all_channels():
    """The channel catalog.

    Only channels the EPG matcher actually covered are returned — a
    channel with no EPG shows an empty "now playing" row, which is noise
    for the user. The unmatched ones (383 of them: US local stations
    addressed by market rather than by name, country-specific variants
    with no matching feed, reality-show multicams, the 18+ adult
    players) are left out.

    ``?include_no_epg=1`` returns the full catalog instead — useful for
    debugging coverage and for clients that want to show a channel even
    without a schedule.

    The underlying ``ALL_CHANNELS`` dict is *not* modified: the EPG
    pipeline still sees every channel (so a channel can pick up a match
    tomorrow), and ``/get-channel-video-url`` still resolves any channel
    that was ever in the catalog.
    """
    if request.args.get("include_no_epg", "").lower() in ("1", "true", "yes"):
        return jsonify({"success": True, "channels": ALL_CHANNELS})

    covered = {name.upper() for name in channels_with_epg_match()}
    if not covered:
        # EPG not generated yet — fall back to the full catalog so the
        # app still shows the channels instead of an empty screen.
        return jsonify({"success": True, "channels": ALL_CHANNELS})

    out = {}
    for category, channels in ALL_CHANNELS.items():
        kept = {name: data for name, data in channels.items()
                if name.upper() in covered}
        if kept:
            out[category] = kept

    return jsonify({
        "success": True,
        "channels": out,
        "n_channels": sum(len(c) for c in out.values()),
    })


# -----------------------------------------------------------------------------
# EPG endpoints.
# -----------------------------------------------------------------------------
def _epg_not_ready():
    """Standard 503 response when the daily fetch hasn't run yet."""
    return jsonify({
        "success": False,
        "error": "EPG not yet generated — run fetch_epg_daily.py --run-once",
    }), 503


@app.route("/epg-status", methods=["GET"])
def epg_status():
    """When was the last refresh? How many channels are covered?

    Counts:
      - n_channels_with_epg        — fuzzy + explicit
      - n_channels_explicit_mapping — pinned in tv_channels.py
      - n_channels_fuzzy            — fuzzy matched
      - n_channels_total            — full catalog
      - n_channels_unmatched        — catalog minus covered
    """
    if not is_available():
        return _epg_not_ready()
    meta = load_meta()
    epg = load_epg()
    unmatched = load_unmatched()

    # Compute age in hours from meta timestamp if present.
    last_refresh = meta.get("last_refresh_utc", "")
    age_hours: float | None = None
    if last_refresh:
        try:
            from datetime import datetime, timezone
            ts = last_refresh.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_hours = round((datetime.now(tz=timezone.utc) - dt).total_seconds() / 3600, 2)
        except (ValueError, TypeError):
            age_hours = None

    # Count every channel across every category. ALL_CHANNELS is nested as
    # {category: {channel_name: {...}}}, so total = sum of per-category sizes.
    n_channels_total = sum(len(chs) for chs in ALL_CHANNELS.values())

    # Count explicit mappings declared in tv_channels.py.
    n_channels_explicit = 0
    for channels in ALL_CHANNELS.values():
        for ch_data in channels.values():
            epg_id = (ch_data.get("epg_id") or "").strip()
            epg_source = (ch_data.get("epg_source") or "").strip()
            if epg_id and epg_source:
                n_channels_explicit += 1

    n_channels_with_epg = meta.get("n_channels_with_epg", len(epg))
    n_channels_fuzzy = max(0, n_channels_with_epg - n_channels_explicit)
    n_channels_unmatched = max(0, n_channels_total - n_channels_with_epg)

    return jsonify({
        "success": True,
        "status": {
            "last_refresh_utc": last_refresh,
            "last_refresh_age_hours": age_hours,
            "n_channels_with_epg": n_channels_with_epg,
            "n_channels_total": n_channels_total,
            "n_channels_explicit_mapping": n_channels_explicit,
            "n_channels_fuzzy": n_channels_fuzzy,
            "n_channels_unmatched": n_channels_unmatched,
            "n_programmes": meta.get("n_programmes", sum(len(v) for v in epg.values())),
            "sources_used": meta.get("sources_used", []),
        },
        "unmatched": unmatched,
        "data_dir": str(EPG_DIR),
    })


@app.route("/get-channel-epg", methods=["GET"])
def get_channel_epg():
    """Full programme list for one channel.

    Query params:
        channel_type (optional) — looked up against ALL_CHANNELS to confirm
                                   the channel exists in the catalog.
        channel_name           — channel name (case-insensitive).

    EPG match resolution priority:
        1. Explicit mapping from ``tv_channels.ALL_CHANNELS`` (epg_id +
           epg_source) — when both fields are set, those are used as the
           source of truth for ``xmltv_id`` and ``source``.
        2. Fuzzy match from ``epg_match.json`` — used otherwise.

    Programmes themselves always come from ``epg.json`` (populated by the
    daily run).
    """
    channel_name = request.args.get("channel_name", "").strip()
    channel_type = request.args.get("channel_type", "").strip()
    date = request.args.get("date", "").strip() or None  # YYYY-MM-DD (UTC)

    if not channel_name:
        return jsonify({"success": False, "error": "channel_name is required"}), 400

    if not is_available():
        return _epg_not_ready()

    # Resolve canonical channel name from the catalog (upper-case keys).
    canonical_name: str | None = None
    category: str | None = None
    if channel_type and channel_type in ALL_CHANNELS:
        for name in ALL_CHANNELS[channel_type]:
            if name.upper() == channel_name.upper():
                canonical_name = name
                category = channel_type
                break
    if canonical_name is None:
        for cat, channels in ALL_CHANNELS.items():
            for name in channels:
                if name.upper() == channel_name.upper():
                    canonical_name = name
                    category = cat
                    break
            if canonical_name:
                break

    if canonical_name is None:
        return jsonify({"success": False, "error": f"Unknown channel: {channel_name}"}), 404

    # EPG match info: explicit > fuzzy.
    match = resolve_channel_match(canonical_name)
    if match is None:
        return jsonify({
            "success": False,
            "error": "No EPG for this channel",
            "channel": canonical_name,
            "category": category,
        }), 404

    # Programmes: full window by default; ?date=YYYY-MM-DD restricts to one day.
    if date:
        programmes = programmes_for_day(canonical_name, date)
        if not programmes:
            epg = load_epg()
            upper_canonical = canonical_name.upper()
            programmes = (
                epg.get(canonical_name)
                or epg.get(upper_canonical)
                or next((v for k, v in epg.items() if k.upper() == upper_canonical), [])
            )
    else:
        epg = load_epg()
        upper_canonical = canonical_name.upper()
        programmes = (
            epg.get(canonical_name)
            or epg.get(upper_canonical)
            or next((v for k, v in epg.items() if k.upper() == upper_canonical), [])
        )

    return jsonify({
        "success": True,
        "channel": canonical_name,
        "category": category,
        "xmltv_id": match.get("xmltv_id"),
        "source": match.get("source"),
        "score": match.get("score"),
        "match_type": match.get("match_type"),
        "date": date,
        "programmes": programmes,
    })


@app.route("/get-channel-current", methods=["GET"])
def get_channel_current():
    """What's playing now on a channel + what's next.

    Match info (``xmltv_id`` / ``source``) follows the same priority as
    ``/get-channel-epg``: explicit mapping in ``tv_channels.py`` first,
    then fuzzy match from ``epg_match.json``.
    """
    channel_name = request.args.get("channel_name", "").strip()
    if not channel_name:
        return jsonify({"success": False, "error": "channel_name is required"}), 400

    if not is_available():
        return _epg_not_ready()

    # Canonicalize via catalog (case-insensitive).
    canonical_name: str | None = None
    for channels in ALL_CHANNELS.values():
        for name in channels:
            if name.upper() == channel_name.upper():
                canonical_name = name
                break
        if canonical_name:
            break
    if canonical_name is None:
        return jsonify({"success": False, "error": f"Unknown channel: {channel_name}"}), 404

    current, nxt = current_programmes(canonical_name)
    if current is None and nxt is None:
        match = resolve_channel_match(canonical_name)
        return jsonify({
            "success": False,
            "error": "No EPG for this channel",
            "channel": canonical_name,
            "match_type": match.get("match_type") if match else None,
        }), 404

    # Surface the source/xmltv_id so the client can show "from BG1" etc.
    match = resolve_channel_match(canonical_name)
    return jsonify({
        "success": True,
        "channel": canonical_name,
        "xmltv_id": match.get("xmltv_id") if match else None,
        "source": match.get("source") if match else None,
        "match_type": match.get("match_type") if match else None,
        "current": current,
        "next": nxt,
    })


@app.route("/get-all-epg", methods=["GET"])
def get_all_epg():
    """Full EPG dict: ``{channel_name: [programmes]}``.

    Response can be large (~17 MB now that the DLHD catalog is in — 1,275
    channels across 51 XMLTV sources). Each programme has ISO-8601 ``start`` /
    ``stop`` in UTC. The Android app fetches this once per session, caches
    it locally, and computes "what's on now" from the device clock.

    Caching: ``Cache-Control: public, max-age=86400`` (24 h) since the data
    is refreshed once per day by the systemd timer. Conditional requests
    (ETag + ``If-None-Match`` / Last-Modified + ``If-Modified-Since``) let
    clients cheaply revalidate without re-downloading: the server returns
    ``304 Not Modified`` when the daily fetch hasn't run since the client's
    cached copy.

    Optional filters (combine with AND) so a client can pull a slice
    instead of the whole payload:

    ``?source=BG1,US2``       — only programmes from these XMLTV sources
    ``?category=Sport,Movie`` — only these catalog categories
    ``?channels=AMC USA,BNT 3`` — only these channel names (exact)

    With no filter the response is byte-identical to the unfiltered one,
    so existing clients are unaffected.
    """
    if not is_available():
        return _epg_not_ready()

    meta = load_meta()
    last_refresh = meta.get("last_refresh_utc", "")
    epg_data = load_epg()

    src_filter = _csv_param("source")
    cat_filter = _csv_param("category")
    chan_filter = _csv_param("channels")
    filtered = bool(src_filter or cat_filter or chan_filter)

    # Last-Modified: when the daily fetch wrote the data (UTC).
    last_modified_dt = None
    if last_refresh:
        try:
            last_modified_dt = datetime.fromisoformat(
                last_refresh.replace("Z", "+00:00"))
            if last_modified_dt.tzinfo is None:
                last_modified_dt = last_modified_dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    # ETag: stable hash of the refresh timestamp. Same data → same ETag.
    etag = hashlib.md5(last_refresh.encode("utf-8")).hexdigest()

    # A filtered request has its own ETag — a client holding the
    # full-payload ETag must not get a 304 for a different slice.
    if filtered:
        sig = repr(sorted(src_filter)) + repr(sorted(cat_filter)) + \
              repr(sorted(chan_filter))
        etag = hashlib.md5((last_refresh + sig).encode("utf-8")).hexdigest()

    # Conditional GET — short-circuit with 304 if the client's cached
    # copy is still current.
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match and if_none_match.strip('"') == etag:
        resp = jsonify({})
        resp.status_code = 304
        resp.headers["ETag"] = f'"{etag}"'
        resp.headers["Cache-Control"] = "public, max-age=86400"
        if last_modified_dt:
            resp.last_modified = last_modified_dt
        return resp

    if_modified_since = request.if_modified_since
    if if_modified_since and last_modified_dt:
        # Werkzeug gives us a datetime; compare timestamps.
        if last_modified_dt.timestamp() <= if_modified_since.timestamp():
            resp = jsonify({})
            resp.status_code = 304
            resp.headers["ETag"] = f'"{etag}"'
            resp.headers["Cache-Control"] = "public, max-age=86400"
            resp.last_modified = last_modified_dt
            return resp

    if filtered:
        match_data = load_match() or {}
        out_epg = {}
        for name, progs in epg_data.items():
            up = name.upper()
            if chan_filter and up not in chan_filter:
                continue
            if src_filter:
                progs = [p for p in progs
                         if (p.get("source") or "").upper() in src_filter]
                if not progs:
                    continue
            if cat_filter:
                rec = match_data.get(name) or {}
                if (rec.get("category") or "").upper() not in cat_filter:
                    continue
            out_epg[name] = progs
        resp = jsonify({
            "success": True,
            "channels": sorted(out_epg.keys()),
            "epg": out_epg,
        })
        resp.headers["Cache-Control"] = "public, max-age=900"
    else:
        resp = jsonify({
            "success": True,
            "channels": channels_with_epg(),
            "epg": epg_data,
        })
        resp.headers["Cache-Control"] = "public, max-age=86400"

    resp.headers["ETag"] = f'"{etag}"'
    if last_modified_dt:
        resp.last_modified = last_modified_dt
    return resp


def _csv_param(name: str) -> set[str]:
    """Parse a comma-separated query parameter into an upper-cased set."""
    raw = (request.args.get(name) or "").strip()
    if not raw:
        return set()
    return {p.strip().upper() for p in raw.split(",") if p.strip()}


@app.route("/server-time", methods=["GET"])
def server_time():
    """Server's current UTC time.

    Clients use this to sync their clock before computing "now playing"
    locally from /get-all-epg. Without sync, a device with a drifted
    clock would show the wrong programme for every channel.

    Response also includes the ``Date`` HTTP header (set by the WSGI
    server). Comparing those two is how the client measures clock skew.
    """
    now = datetime.now(tz=timezone.utc)
    return jsonify({
        "success": True,
        "now_utc": now.isoformat(),
        "epoch_ms": int(now.timestamp() * 1000),
    })


@app.route("/get-current-all", methods=["GET"])
def get_current_all():
    """What's airing right now on every channel with EPG data.

    One request returns ``{channel, current, next, progress}`` for every
    channel that has any programmes in the published window. Designed for
    the Android app's "what's on now" grid — replaces N individual
    ``/get-channel-current`` calls with one.

    Response includes ``now_utc`` (server time the snapshot was taken) so
    the client can show "as of HH:MM" labels.

    Optional ``?channel_type=Sport`` filters to one category.
    """
    if not is_available():
        return _epg_not_ready()

    channel_type = request.args.get("channel_type", "").strip()
    rows = now_playing_all()

    # Optional category filter — uses ALL_CHANNELS to know which keys
    # belong to each category.
    if channel_type:
        keys = set()
        if channel_type in ALL_CHANNELS:
            for name in ALL_CHANNELS[channel_type]:
                keys.add(name.upper())
        rows = [r for r in rows if r["channel"] in keys]

    with_current = sum(1 for r in rows if r["current"] is not None)
    return jsonify({
        "success": True,
        "now_utc": datetime.now(tz=timezone.utc).isoformat(),
        "total_channels": len(rows),
        "with_current_programme": with_current,
        "channels": rows,
    })


@app.after_request
def _cache_control(resp):
    """EPG data is refreshed daily — cacheable for 15 minutes."""
    if request.path.startswith(("/epg-status", "/get-channel-epg",
                                "/get-channel-current", "/get-all-epg",
                                "/get-current-all")):
        resp.headers["Cache-Control"] = "public, max-age=900"
    # /server-time must NOT be cached — clients use it to sync their clock.
    if request.path == "/server-time":
        resp.headers["Cache-Control"] = "no-store"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
