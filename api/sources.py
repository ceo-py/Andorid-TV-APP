"""XMLTV sources we know about + the ones we'll actually fetch.

Each entry is (source_id, country_code_or_label).
Sources are .xml.gz files at ``https://epgshare01.online/epgshare01/epg_ripper_<ID>.xml.gz``.

We do not fetch ``ALL_SOURCES1`` — it's 189 MB. We pick a curated list covering
Eastern Europe, Italy, Germany, France and the UK/US, which between them cover
most of the 152 channels in our catalog.
"""

from typing import Iterable, Tuple

# Curated list of source IDs to fetch. Order = priority for matching (later
# entries still score, but earlier entries are preferred ties).
SOURCE_IDS: Tuple[str, ...] = (
    # Bulgaria first — best coverage for the catalog (BNT/BTV/Balkanika…).
    "BG1",
    # Italy (Sky Italia, MTV Italy, Discovery Italy etc.).
    "IT1",
    # English-language Western Europe / US.
    "UK1",
    "US1",
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
    "ALL_AT1",   # Austria
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
    "MK1",       # North Macedonia
)

# Full list — used by ``list-only`` mode or for users who want every source.
ALL_SOURCE_IDS: Tuple[str, ...] = (
    "AE1", "AL1", "ALJAZEERA1", "ALL_SOURCES1", "AR1", "ASIANTELEVISION1",
    "AT1", "AU1", "AUDACY1", "BA1", "BB1", "BE2", "BEIN1", "BG1", "BR1",
    "BR2", "CA2", "CH1", "CL1", "CO1", "CR1", "CY1", "CZ1", "DE1",
    "DELUXEMUSIC1", "DIRECTVSPORTS1", "DISTROTV1", "DK1", "DO1",
    "DRAFTKINGS1", "DUMMY_CHANNELS", "EC1", "EG1", "ES1", "FANDUEL1",
    "FI1", "FR1", "GR1", "HK1", "HR1", "HU1", "ID1", "IE1", "IL1", "IN1",
    "IN2", "IN4", "IT1", "JM1", "JP1", "JP2", "KE1", "KR1", "KZ1", "LT1",
    "LU1", "LV1", "MN1", "MT1", "MUSICBOX1", "MX1", "MY1", "NG1", "NL1",
    "NO1", "NZ1", "PA1", "PE1", "PEACOCK1", "PH1", "PH2", "PK1", "PL1",
    "PLEX1", "PT1", "RAKUTEN1", "RALLY_TV1", "RO1", "RO2", "RS1", "SA1",
    "SA2", "SE1", "SG1", "SK1", "SPORTKLUB1", "SSPORTPLUS1", "SV1",
    "TBNPLUS1", "TH1", "THESPORTPLUS1", "TR1", "TR3", "UK1", "US2",
    "US_LOCALS1", "US_SPORTS1", "UY1", "VN1", "VOA1", "WHALETVPLUS1",
    "ZA1", "viva-russia.ru",
)


def filename_for(source_id: str) -> str:
    """File name we cache a source under."""
    return f"epg_ripper_{source_id}.xml.gz"


def url_for(source_id: str, base: str) -> str:
    """Full URL to download ``source_id`` from."""
    return f"{base}epg_ripper_{source_id}.xml.gz"


def curated() -> Iterable[str]:
    """Yields curated source IDs in priority order."""
    yield from SOURCE_IDS
