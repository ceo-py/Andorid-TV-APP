"""XMLTV sources we know about + the ones we'll actually fetch.

Each entry is (source_id, country_code_or_label).
Sources are .xml.gz files at ``https://epgshare01.online/epgshare01/epg_ripper_<ID>.xml.gz``.

We do not fetch ``ALL_SOURCES1`` — it's 189 MB. We pick a curated list covering
Eastern Europe, Italy, Germany, France and the UK/US, which between them cover
most of the 152 channels in our catalog.

The DLHD catalog (~1,100 international streams) needs far broader coverage, so
the curated list was widened to 76 feeds. ``US1`` was dropped: it 404s upstream.
"""

from typing import Iterable, Tuple

# Curated list of source IDs to fetch. Order = priority for matching (later
# entries still score, but earlier entries are preferred ties).
SOURCE_IDS: Tuple[str, ...] = (
    # Bulgaria first — best coverage for the catalog (BNT/BTV/Balkanika…).
    "BG1",
    # Globetvapp/epg - HD variants of Bulgarian channels (BNT 3/4, Planeta HD/Folk, Balkanika, Fen, SKAT, Travel TV, 7/8 TV).
    # Lives on GitHub, not epgshare01. Source-specific URL is set in url_for() below.
    "GLOBETV2",
    # iptv-epg.org - Bulgarian feed with Latin channel IDs. Source-specific URL in url_for().
    # Fills E Kids (EKids.bg) which BG1 leaves empty.
    "IPTVEPG_BG",
    # Italy (Sky Italia, MTV Italy, Discovery Italy etc.).
    "IT1",
    # English-language Western Europe / US.
    "UK1",
    "US2",
    "DE1",
    # BeIN sports, French, Spanish, Romanian — covers a chunk of the
    # Worldwide + Sport categories.
    "BEIN1",
    "FR1",
    "ES1",
    "RO1",
    "RO2",
    # Specific add-ons.
    # NOTE: "ALL_AT1" and "MK1" used to be here but both 404 upstream —
    # Austria's feed is "AT1" (listed below), and there is no Macedonian feed.
    "HR1",       # Croatia
    "RS1",       # Serbia
    "AL1",       # Albania
    "GR1",       # Greece
    "TR1",       # Turkey
    "HU1",       # Hungary
    "CZ1",       # Czechia
    "SK1",       # Slovakia
    "NL1",       # Netherlands
    "BE2",       # Belgium (French)
    "BA1",       # Bosnia
    # --- Extra coverage for the DLHD catalog --------------------------
    # Americas
    "CA2",       # Canada
    "MX1",       # Mexico
    "BR1",       # Brazil
    "BR2",       # Brazil (regional)
    "UY1",       # Uruguay
    "AR1",       # Argentina
    "CL1",       # Chile
    "CO1",       # Colombia
    "PE1",       # Peru
    # US extras (US1 is dead upstream)
    "US_LOCALS1",  # 4,471 US local stations
    "US_SPORTS1",  # US sports networks
    "PLEX1",       # PLEX free-to-air bundles
    "FANDUEL1",    # FanDuel sports network
    "DIRECTVSPORTS1",
    "RALLY_TV1",
    "TBNPLUS1",
    "THESPORTPLUS1",
    # Western Europe
    "CH1",       # Switzerland
    "AT1",       # Austria
    "DK1",       # Denmark
    "SE1",       # Sweden
    "NO1",       # Norway
    "FI1",       # Finland
    "PL1",       # Poland
    "PT1",       # Portugal
    "LU1",       # Luxembourg
    "LV1",       # Latvia
    "LT1",       # Lithuania
    "MT1",       # Malta
    "CY1",       # Cyprus
    "IE1",       # Ireland
    # Southern Europe / Balkans
    "TR3",       # Turkey (extra)
    "ALJAZEERA1",
    # Middle East / Africa
    "AE1",       # Arabic (912 channels)
    "IL1",       # Israel
    "ZA1",       # South Africa
    "EG1",       # Egypt
    "EC1",       # Ecuador
    "DO1",       # Dominican Republic
    "NG1",       # Nigeria
    "KE1",       # Kenya
    # Asia
    "IN1",       # India
    "IN2",
    "IN4",
    "ID1",       # Indonesia
    "MY1",       # Malaysia
    "SG1",       # Singapore
    "VN1",       # Vietnam
    "PH2",       # Philippines
    "JP1",       # Japan
    "JP2",
    "KR1",       # Korea
    "HK1",       # Hong Kong
    # Latin America extras
    "PEACOCK1",
)

# Full list — used by ``list-only`` mode or for users who want every source.
ALL_SOURCE_IDS: Tuple[str, ...] = (
    "AE1", "AL1", "ALJAZEERA1", "ALL_SOURCES1", "AR1", "ASIANTELEVISION1",
    "AT1", "AU1", "AUDACY1", "BA1", "BB1", "BE2", "BEIN1", "BG1", "BR1",
    "BR2", "CA2", "CH1", "CL1", "CN1", "CO1", "CR1", "CY1", "CZ1", "DE1",
    "DELUXEMUSIC1", "DIRECTVSPORTS1", "DISTROTV1", "DK1", "DO1",
    "DRAFTKINGS1", "DUMMY_CHANNELS", "EC1", "EG1", "ES1", "FANDUEL1",
    "FI1", "FR1", "GLOBETV1", "GLOBETV2", "GR1", "HK1", "HR1", "HU1", "ID1",
    "IE1", "IL1", "IN1", "IN2", "IN4", "IPTVEPG_BG", "IT1", "JM1", "JP1",
    "JP2", "KE1", "KR1", "KZ1", "LT1", "LU1", "LV1", "MN1", "MT1",
    "MUSICBOX1", "MX1", "MY1", "NG1", "NL1", "NO1", "NZ1", "PA1", "PE1",
    "PEACOCK1", "PH1", "PH2", "PK1", "PL1", "PLEX1", "PT1", "RAKUTEN1",
    "RALLY_TV1", "RO1", "RO2", "RS1", "SA1", "SA2", "SE1", "SG1", "SK1",
    "SPORTKLUB1", "SSPORTPLUS1", "SV1", "TBNPLUS1", "TH1", "THESPORTPLUS1",
    "TR1", "TR3", "TW1", "UK1", "US2", "US_LOCALS1", "US_SPORTS1", "UY1",
    "VN1", "VOA1", "WHALETVPLUS1", "ZA1", "viva-russia.ru",
)


def filename_for(source_id: str) -> str:
    """File name we cache a source under."""
    return f"epg_ripper_{source_id}.xml.gz"


def url_for(source_id: str, base: str) -> str:
    """Full URL to download ``source_id`` from.

    Most sources live on epgshare01 (``base`` = ``https://epgshare01.online/epgshare01/``).
    A few third-party feeds (globetvapp/epg, iptv-epg.org) live elsewhere — those
    have hard-coded URLs here and ignore ``base``.
    """
    # globetvapp/epg — Bulgarian channels in HD variant (Bulgaria folder, two
    # xml.gz files updated daily on GitHub).
    if source_id == "GLOBETV2":
        return "https://raw.githubusercontent.com/globetvapp/epg/main/Bulgaria/bulgaria2.xml.gz"
    if source_id == "GLOBETV1":
        return "https://raw.githubusercontent.com/globetvapp/epg/main/Bulgaria/bulgaria1.xml.gz"
    # iptv-epg.org — per-country XMLTV files, refreshed every few hours.
    if source_id == "IPTVEPG_BG":
        return "https://iptv-epg.org/files/epg-bg.xml.gz"
    return f"{base}epg_ripper_{source_id}.xml.gz"


def curated() -> Iterable[str]:
    """Yields curated source IDs in priority order."""
    yield from SOURCE_IDS
