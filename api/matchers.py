"""Channel-name normalisation + fuzzy matching for XMLTV feeds.

We need to match our catalog names (often UPPER-CASE English short forms:
"CARTOON NETWORK", "DISNEY CHANNEL", "BTV", "AMC", ...) against XMLTV's
display-names which come in many flavours:

  "Sky Uno +", "Sky Atlantic", "AMC.bg", "24Kitchen", "MTV HD"
  "National Geographic Wild HD", "Cartoon Network", "beIN Sports HD"

The matchers here give a single score 0..1.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Optional


# Words that don't help distinguish a channel — we strip them before scoring.
_GENERIC_TOKENS = {
    "hd", "uhd", "fhd", "sd",
    "tv", "channel", "television",
    "live",
    "east", "west",
    "uk", "us", "int", "international",
    "eu", "europe", "european",
    "global", "world", "worldwide",
}

# Common suffix patterns we strip to get a canonical name.
_SUFFIX_RE = re.compile(
    r"\s*("
    r"hd|sd|uhd|fhd|4k|1080p?|720p?|full\s*hd|high\s*definition|"
    r"\+\s*\d+|\+\s*hd|\+1|"
    r"\(\d+\)|"
    r"intl?\.?|international|"
    r"\.bg|\.it|\.ro|\.rs|\.hr|\.si|\.de|\.fr|\.es|\.us|\.uk|\.gr|\.tr|"
    r"\.com|\.tv|"
    r"live"
    r")\s*$",
    re.IGNORECASE,
)

# Country code suffix to strip from the END only (XMLTV often encodes country
# in the channel id like "AMC.bg").
_TAIL_COUNTRY_RE = re.compile(r"\.[a-z]{2}(?:\.[a-z]+)?\s*$", re.IGNORECASE)

# Diacritics to ASCII (we try NFKD then encode ascii).
_DIACRITIC_TABLE = str.maketrans({
    "ı": "i", "İ": "i",
    "ß": "ss", "ø": "o", "æ": "ae", "œ": "oe",
    "đ": "d", "ħ": "h", "ł": "l", "ð": "d", "þ": "th",
    "ć": "c", "č": "c", "ç": "c",
    "ş": "s", "š": "s", "ś": "s", "ș": "s",
    "ğ": "g", "ġ": "g",
    "ž": "z", "ź": "z", "ż": "z",
    "ñ": "n", "ń": "n", "ņ": "n",
    "ë": "e", "é": "e", "è": "e", "ê": "e",
    "ä": "a", "á": "a", "à": "a", "â": "a", "ã": "a", "å": "a",
    "ö": "o", "ó": "o", "ò": "o", "ô": "o", "õ": "o",
    "ü": "u", "ú": "u", "ù": "u", "û": "u",
    "ï": "i", "í": "i", "ì": "i", "î": "i",
    "ý": "y", "ÿ": "y",
    "á": "a", "í": "i",
})


def strip_accents(s: str) -> str:
    """Best-effort diacritic strip: try ``str.translate`` first (fast, common),
    fall back to NFKD normalisation."""
    try:
        out = s.translate(_DIACRITIC_TABLE)
        # Anything left over? Force NFKD for stragglers.
        if any(ord(c) > 127 for c in out):
            out = unicodedata.normalize("NFKD", out).encode("ascii", "ignore").decode("ascii")
        return out
    except Exception:
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def normalise(name: str) -> str:
    """Lower-case, diacritics off, suffix noise stripped, single-spaced.

    >>> normalise("CARTOON NETWORK")
    'cartoon network'
    >>> normalise("MTV HD")
    'mtv'
    >>> normalise("Sky Uno +1 HD")
    'sky uno'
    """
    if not name:
        return ""
    s = strip_accents(str(name)).lower().strip()
    # XMLTV IDs come dotted — extract the human-readable part only.
    s = s.replace(".", " ").replace("_", " ").replace("-", " ")
    s = re.sub(r"\(\s*[a-z]{2}\s*\)", " ", s)          # strip "(bg)" tags
    s = re.sub(r"\s+", " ", s).strip()
    s = _SUFFIX_RE.sub("", s)
    s = _TAIL_COUNTRY_RE.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenise(name: str) -> list[str]:
    """Return meaningful tokens only (drops ``_GENERIC_TOKENS``)."""
    n = normalise(name)
    if not n:
        return []
    out = []
    for tok in n.split():
        if tok in _GENERIC_TOKENS:
            continue
        if len(tok) < 2:
            continue
        out.append(tok)
    return out


def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    union = sa | sb
    if not union:
        return 0.0
    return len(sa & sb) / len(union)


@dataclass
class Match:
    channel_id: str               # the XMLTV channel id we matched against
    display_name: str             # the XMLTV display-name we matched against
    score: float                  # 0..1
    reason: str = ""              # human-readable scoring explanation

    def __lt__(self, other):
        return self.score < other.score


def score(query_name: str, candidate_name: str) -> Match:
    """Return a scored ``Match`` for ``query_name`` against ``candidate_name``.

    Score components:
      * 1.0 — exact normalised name equality
      * 0.9 — token set equality after normalisation
      * 0.85 — one is a strict substring of the other (e.g. "Cartoon" vs "Cartoon Network")
      * 0.6–0.85 — Jaccard token overlap
      * 0–0.6 — lower
    """
    qn = normalise(query_name)
    cn = normalise(candidate_name)
    reason = []

    if qn == cn:
        return Match(candidate_name, candidate_name, 1.0, "exact-normalised")

    qt = tokenise(query_name)
    ct = tokenise(candidate_name)
    if not qt and not ct:
        return Match(candidate_name, candidate_name, 0.0, "both-empty")

    # Exact token-set equality after dropping generic words.
    if qt and ct and set(qt) == set(ct):
        return Match(candidate_name, candidate_name, 0.9, "token-set-equal")

    # Substring containment: one fully inside the other after normalisation.
    if qn and cn and (qn in cn or cn in qn):
        longer = max(len(qn), len(cn))
        shorter = min(len(qn), len(cn))
        bonus = shorter / longer  # longer containment scores higher
        return Match(candidate_name, candidate_name,
                     0.78 + 0.07 * bonus, "substring")

    # Token overlap (Jaccard).
    j = jaccard(qt, ct)
    if j >= 0.5:
        return Match(candidate_name, candidate_name,
                     0.6 + 0.25 * j, f"jaccard={j:.2f}")

    # Bonus for shared first token (helps with "24Kitchen" / "24 Kitchen").
    if qt and ct and qt[0] == ct[0] and len(qt[0]) >= 3:
        partial = 0.45 + 0.30 * j
        return Match(candidate_name, candidate_name,
                     partial, f"first-token-match+jaccard={j:.2f}")

    reason_str = "no-signal" if j < 0.2 else f"low-jaccard={j:.2f}"
    return Match(candidate_name, candidate_name, j * 0.5, reason_str)


def best_match(query_name: str,
               candidates: Iterable[tuple[str, str]],
               threshold: float = 0.78) -> Optional[Match]:
    """Given ``[(xmltv_channel_id, display_name), ...]``, return the best one
    that meets the threshold. ``None`` if nothing crosses the bar."""
    best: Optional[Match] = None
    for cid, dname in candidates:
        m = score(query_name, dname)
        # Remember the channel id in the match object.
        m.channel_id = cid
        m.display_name = dname
        if best is None or m.score > best.score:
            best = m
    if best is not None and best.score >= threshold:
        return best
    return None
