"""
NLTK-powered hint parser for the AI Detective mode.

The player types free-text hints such as

    "Ravi is innocent"
    "It wasn't the rope"
    "The murder happened in the Library"
    "I think the butler did it"

and this module turns them into structured constraints:

    ("exclude", "WHO", "Ravi")
    ("confirm", "WHERE", "Library")

It uses NLTK's tokenizer (Punkt when the data package is present, otherwise
the rule-based Treebank tokenizer, which needs no download) plus the Porter
stemmer and NLTK's stopword list when available. A small built-in fallback
keeps the app working completely offline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from nltk.stem import PorterStemmer

# ---------------------------------------------------------------- tokenizer
try:  # Punkt gives sentence-aware tokenisation when the data is installed
    import nltk
    from nltk.tokenize import word_tokenize as _punkt_tokenize

    try:
        nltk.data.find("tokenizers/punkt_tab")
        _HAS_PUNKT = True
    except LookupError:
        _HAS_PUNKT = False
except Exception:  # pragma: no cover - nltk is a hard dependency here
    _HAS_PUNKT = False

from nltk.tokenize import TreebankWordTokenizer

_TREEBANK = TreebankWordTokenizer()

try:
    from nltk.corpus import stopwords as _nltk_stopwords

    _STOPWORDS = set(_nltk_stopwords.words("english"))
except Exception:
    _STOPWORDS = {
        "a", "an", "the", "is", "was", "were", "are", "am", "be", "been", "being",
        "it", "this", "that", "these", "those", "of", "to", "in", "on", "at", "for",
        "with", "and", "or", "but", "if", "then", "so", "as", "by", "from", "he",
        "she", "they", "them", "his", "her", "their", "i", "you", "we", "my", "me",
        "do", "does", "did", "has", "have", "had", "will", "would", "can", "could",
        "should", "there", "here", "who", "what", "where", "when", "why", "how",
    }

_STEMMER = PorterStemmer()

TOKENIZER_NAME = "NLTK Punkt" if _HAS_PUNKT else "NLTK Treebank"

# ---------------------------------------------------------------- vocabulary
ALIASES: Dict[str, Dict[str, List[str]]] = {
    "WHO": {
        "Ravi": ["ravi", "dealer", "antiquities dealer", "collector"],
        "Meera": ["meera", "chemist", "toxicologist", "scientist"],
        "Kabir": ["kabir", "tycoon", "magnate", "businessman"],
        "Zara": ["zara", "novelist", "writer", "author"],
        "Dev": ["dev", "butler", "servant", "manservant"],
    },
    "WHERE": {
        "Library": ["library", "bookshelves", "books"],
        "Kitchen": ["kitchen", "pantry"],
        "Garden": ["garden", "rose garden", "courtyard"],
        "Study": ["study", "private office", "bureau"],
        "Ballroom": ["ballroom", "ball room", "dance floor"],
    },
    "WHAT": {
        "Knife": ["knife", "blade", "dagger"],
        "Candlestick": ["candlestick", "candle", "candelabra", "candelabrum"],
        "Poison": ["poison", "aconite", "toxin", "dropper"],
        "Rope": ["rope", "cord", "noose"],
        "Revolver": ["revolver", "gun", "pistol", "firearm"],
    },
}

CONTRACTIONS = {
    "isn't": "is not", "wasn't": "was not", "weren't": "were not",
    "didn't": "did not", "doesn't": "does not", "don't": "do not",
    "can't": "cannot", "couldn't": "could not", "won't": "will not",
    "wouldn't": "would not", "hasn't": "has not", "haven't": "have not",
    "it's": "it is", "that's": "that is", "he's": "he is", "she's": "she is",
    "i'm": "i am", "im": "i am", "you're": "you are", "they're": "they are",
}

NEGATORS = {
    "not", "never", "nor", "neither", "innocent", "cleared",
    "exclude", "excluded", "except", "without", "cannot", "false",
    "wrong", "absolve", "absolved",
}

POSITIVES = {
    "guilty", "killer", "murderer", "culprit", "confess", "confessed",
    "did", "done", "accuse", "accused", "sure", "certain", "think",
    "believe", "yes", "correct", "right", "exactly", "definitely",
}

POSITIVE_PATTERNS = [
    r"\bit (was|is)\b",
    r"\bthe (killer|murderer|culprit) (is|was)\b",
    r"\b(happened|occurred|took place) (in|at)\b",
    r"\bthe (crime scene|scene|body) (is|was|in|at)\b",
    r"\bthe weapon (is|was)\b",
    r"\b(killed|murdered|struck|hit) (him|her|them)? ?(with|using|by)\b",
    r"\b(did it|is guilty|was guilty|is the killer|was the killer)\b",
    r"\bi (think|believe|am sure|am certain)\b",
    r"\buse(d)? the\b",
]

NEGATIVE_PATTERNS = [
    r"\b(not|never)\b",
    r"\binnocent\b",
    r"\b(rule|ruled) (him |her |them )?out\b",
    r"\b(did not|was not|is not|were not)\b",
    r"\b(cleared|absolved)\b",
    r"\bno way\b",
]

WHERE_PREPS = {"in", "at", "inside", "near", "outside", "around", "within"}
WHAT_PREPS = {"with", "using", "by", "via"}


@dataclass
class HintResult:
    """Structured reading of one free-text hint."""

    text: str
    effects: List[Tuple[str, str, str]] = field(default_factory=list)  # (sign, cat, item)
    noted: List[Tuple[str, str]] = field(default_factory=list)       # mentioned, no action
    tokens: List[str] = field(default_factory=list)
    engine: str = TOKENIZER_NAME
    summary: str = ""

    @property
    def understood(self) -> bool:
        return bool(self.effects)


def _normalise(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.lower()
    for short, full in CONTRACTIONS.items():
        text = re.sub(rf"\b{re.escape(short)}\b", full, text)
    return text


def _tokenize(text: str) -> List[str]:
    if _HAS_PUNKT:
        try:
            toks = _punkt_tokenize(text)
        except Exception:
            toks = _TREEBANK.tokenize(text)
    else:
        toks = _TREEBANK.tokenize(text)
    return [t for t in toks if re.search(r"[a-z0-9]", t)]


def _alias_phrases() -> List[Tuple[str, str, Tuple[str, ...]]]:
    """Flatten the alias table into (category, item, stemmed token tuple)."""
    out = []
    for cat, items in ALIASES.items():
        for item, names in items.items():
            for name in names:
                parts = tuple(_STEMMER.stem(w) for w in name.split())
                out.append((cat, item, parts))
    # longest phrases first so "rose garden" beats "garden"
    return sorted(out, key=lambda t: -len(t[2]))


_PHRASES = _alias_phrases()


def _find_mentions(tokens: List[str]) -> List[Tuple[str, str, int, int]]:
    stems = [_STEMMER.stem(t) for t in tokens]
    mentions: List[Tuple[str, str, int, int]] = []
    taken = set()
    for cat, item, parts in _PHRASES:
        n = len(parts)
        for i in range(len(stems) - n + 1):
            if tuple(stems[i:i + n]) == parts:
                span = range(i, i + n)
                if any(j in taken for j in span):
                    continue
                taken.update(span)
                mentions.append((cat, item, i, i + n))
    return sorted(mentions, key=lambda m: m[2])


def _window(tokens: List[str], start: int, end: int, before: int = 7, after: int = 5) -> Tuple[List[str], str]:
    lo = max(0, start - before)
    hi = min(len(tokens), end + after)
    words = tokens[lo:hi]
    return words, " ".join(words)


def _has_pattern(patterns: List[str], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def _describe(sign: str, cat: str, item: str) -> str:
    if sign == "exclude":
        if cat == "WHO":
            return f"**{item}** is innocent \u2014 removed from the suspect list."
        if cat == "WHERE":
            return f"It did not happen in the **{item}** \u2014 scene ruled out."
        return f"The **{item}** was not the weapon \u2014 ruled out."
    if cat == "WHO":
        return f"**{item}** is the killer \u2014 locked in as the prime suspect."
    if cat == "WHERE":
        return f"The crime happened in the **{item}** \u2014 scene locked in."
    return f"The weapon was the **{item}** \u2014 locked in."


def parse_hint(text: str) -> HintResult:
    """Turn one free-text hint into zero or more logical constraints."""
    raw = (text or "").strip()
    if not raw:
        return HintResult(text=raw, summary="I did not receive a hint.")

    normalised = _normalise(raw)
    tokens = _tokenize(normalised)
    result = HintResult(text=raw, tokens=tokens[:14])

    mentions = _find_mentions(tokens)
    if not mentions:
        result.summary = (
            "I could not find a suspect, place or weapon in that sentence. "
            "Try naming one of the case files, for example \u201cRavi is innocent\u201d "
            "or \u201cit happened in the Library\u201d."
        )
        return result

    seen = set()
    for cat, item, start, end in mentions:
        words, phrase = _window(tokens, start, end)

        negated = _has_pattern(NEGATIVE_PATTERNS, phrase) or any(w in NEGATORS for w in words)
        positive = _has_pattern(POSITIVE_PATTERNS, phrase) or any(w in POSITIVES for w in words)

        sign: Optional[str] = None
        if negated and not re.search(r"\bnot only\b", phrase):
            sign = "exclude"
        elif positive:
            sign = "confirm"
        elif cat == "WHERE" and any(w in WHERE_PREPS for w in words):
            sign = "confirm"
        elif cat == "WHAT" and any(w in WHAT_PREPS for w in words):
            sign = "confirm"

        key = (sign, cat, item)
        if sign is None:
            if (cat, item) not in seen:
                result.noted.append((cat, item))
                seen.add((cat, item))
            continue
        if key in seen:
            continue
        seen.add(key)
        result.effects.append((sign, cat, item))

    parts = [_describe(*e) for e in result.effects]
    if result.noted and not parts:
        names = ", ".join(f"**{i}**" for _, i in result.noted)
        parts.append(f"I noted {names}, but that does not change my theory yet.")
    if not parts:
        parts.append("That hint did not change my theory.")
    result.summary = " ".join(parts)
    return result
