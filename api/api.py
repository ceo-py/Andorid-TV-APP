from flask import Flask, request, jsonify
from tv_channels import ALL_CHANNELS, extract_video_url_default, extract_video_url_gledai_tv, remove_proxy_from_link
import asyncio
from datetime import datetime, timezone

from epg_service import (
    EPG_DIR,
    channels_with_epg,
    current_programmes,
    is_available,
    load_epg,
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

    return jsonify({"success": True, "channels": ALL_CHANNELS})


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

    Response can be large (~2 MB). Use /get-channel-epg for a single channel.

    Each programme has ISO-8601 ``start`` / ``stop`` in UTC. The Android app
    is expected to fetch this once, cache it for 15+ minutes (server sends
    ``Cache-Control: public, max-age=900``), and compute "what's on now"
    locally by walking the programmes whose ``[start, stop)`` contains
    the current time. Use ``/server-time`` to sync the device clock before
    computing — avoids client-clock drift over a long session.
    """
    if not is_available():
        return _epg_not_ready()
    return jsonify({
        "success": True,
        "channels": channels_with_epg(),
        "epg": load_epg(),
    })


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
