"""Rule-based mapping of a chat query onto the category's set filters.

Works without any LLM: "liška akvarel na hrnek" -> Styl: akvarel,
Hodí se na: Hrnek, and "liška" stays for fulltext. Only values that exist
in the filter schemas (grown from listed products) can be matched, so the
web never gets a filter the catalogue does not offer.
"""

import re
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from brain.models import Category, FilterSchema
from brain.search import strip_accents

_TOKEN = re.compile(r"\d+:\d+|\w+", re.UNICODE)
_RATIO = re.compile(r"^\d+:\d+$")

# Query phrase (normalised, no accents) -> candidate filter values; the first
# candidate that exists in the schema wins. Covers words the stemmer cannot
# connect ("triko" vs "Tričko") and Czech names of styles stored in English.
SYNONYMS: dict[str, list[str]] = {
    "triko": ["Tričko"],
    "tricko": ["Tričko"],
    "taska": ["Plátěná taška"],
    "tapeta": ["Fototapeta"],
    "tapetu": ["Fototapeta"],
    "tapety": ["Fototapeta"],
    "mobil": ["Obal na mobil"],
    "kryt": ["Obal na mobil"],
    "plakat": ["Plakát"],
    "platno": ["Plátno na rámu"],
    "cedule": ["Plechová cedule"],
    "podlozka": ["Podložka pod myš"],
    "na vysku": ["na výšku"],
    "vertikalni": ["na výšku"],
    "nastojato": ["na výšku"],
    "na sirku": ["na šířku"],
    "horizontalni": ["na šířku"],
    "nalezato": ["na šířku"],
    "ctvercovy": ["čtverec"],
    "akvarel": ["akvarel", "watercolor", "watercolour"],
    "olejomalba": ["olejomalba", "oil painting"],
    "kresba": ["kresba", "drawing", "sketch"],
    "fotka": ["fotografie", "photo", "photograph", "photorealistic"],
    "fotografie": ["fotografie", "photo", "photograph", "photorealistic"],
    "realisticky": ["fotorealistický", "photorealistic", "realistic"],
    "anime": ["anime"],
    "komiks": ["komiks", "comic"],
    "pixel": ["pixel art"],
}


@dataclass
class Match:
    key: str
    label: str
    value: str


@dataclass
class Extraction:
    filters: dict[str, list[str]] = field(default_factory=dict)
    matches: list[Match] = field(default_factory=list)
    rest: str = ""
    # Category named in the query ("krajina na plakát"), when none is selected.
    category: str | None = None


def _norm(value: str) -> str:
    return strip_accents(value).lower()


def _tokens(value: str) -> list[str]:
    return _TOKEN.findall(_norm(value))


def _stem(word: str) -> str:
    # Same crude stemming as fulltext: drop the inflected ending.
    if len(word) >= 6:
        return word[:-2]
    if len(word) == 5:
        return word[:-1]
    return word


def _stems(word: str) -> set[str]:
    stems = {_stem(word)}
    # Czech mobile e: "hrnek" -> "hrnky", "hrnku"; "ctverec" -> "ctverce".
    if len(word) >= 5 and word[-2] == "e" and word[-1] in "kcl":
        stems.add(word[:-2] + word[-1])
    return stems


def _same_word(query_tok: str, value_tok: str) -> bool:
    if len(value_tok) <= 3 or len(query_tok) <= 3 or _RATIO.match(value_tok):
        return query_tok == value_tok
    return any(query_tok.startswith(s) for s in _stems(value_tok)) or any(
        value_tok.startswith(s) for s in _stems(query_tok)
    )


def _find(tokens: list[str], used: set[int], phrase: list[str]) -> list[int] | None:
    """Positions of a contiguous phrase in the query, skipping used tokens."""
    n = len(phrase)
    for start in range(len(tokens) - n + 1):
        span = range(start, start + n)
        if any(i in used for i in span):
            continue
        if all(_same_word(tokens[i], phrase[j]) for j, i in enumerate(span)):
            return list(span)
    return None


def _schemas(session: Session, category_slug: str | None) -> list[FilterSchema]:
    stmt = select(FilterSchema).where(FilterSchema.kind == "set")
    if category_slug:
        stmt = stmt.join(Category).where(Category.slug == category_slug)
    return list(session.scalars(stmt))


def extract(
    query: str,
    schemas: list[tuple[str, str, list[str]]],
    categories: list[tuple[str, str]] | None = None,
) -> Extraction:
    """Match query words to schema values; schemas = [(attr_key, label, values)].

    Longer values are tried first so "Obal na mobil" beats a shorter value.
    Matched words are removed from the rest that goes to fulltext.
    """
    # Original case is kept for the fulltext rest: "M" or "XL" must stay sizes.
    original = _TOKEN.findall(strip_accents(query))
    tokens = [t.lower() for t in original]
    used: set[int] = set()
    out = Extraction()
    owner: dict[str, tuple[str, str]] = {}  # normalised value -> (key, original value)
    labels: dict[str, str] = {}
    candidates: list[tuple[list[str], str, str]] = []  # (value tokens, key, value)
    for key, label, values in schemas:
        labels[key] = label
        for value in values:
            toks = _tokens(value)
            if toks:
                candidates.append((toks, key, value))
                owner.setdefault(_norm(value), (key, value))
    candidates.sort(key=lambda c: -len(c[0]))

    def add(key: str, value: str, positions: list[int]) -> None:
        used.update(positions)
        bucket = out.filters.setdefault(key, [])
        if value not in bucket:
            bucket.append(value)
            out.matches.append(Match(key=key, label=labels[key], value=value))

    # Synonyms first: they encode intent the generic matcher would miss
    # ("na výšku" must not fall back to a looser match).
    for phrase in sorted(SYNONYMS, key=lambda p: -len(p.split())):
        hit = next((owner[_norm(v)] for v in SYNONYMS[phrase] if _norm(v) in owner), None)
        if hit is None:
            continue
        positions = _find(tokens, used, phrase.split())
        if positions is not None:
            add(hit[0], hit[1], positions)

    for toks, key, value in candidates:
        # Words of two letters ("na", "s") never match alone.
        if len(toks) == 1 and len(toks[0]) <= 2 and not _RATIO.match(toks[0]):
            continue
        positions = _find(tokens, used, toks)
        if positions is not None:
            add(key, value, positions)

    # A word naming a category ("krajina" -> Krajiny a příroda) scopes the search.
    # Only the first word of the name counts: "a příroda" or "a hračky" are not intent.
    for slug, name in categories or []:
        words = [w for w in _tokens(name) if len(w) > 3]
        if words:
            positions = _find(tokens, used, words[:1])
            if positions is not None:
                used.update(positions)
                # The rest of the name ("tapety" in "vzory a tapety") is not a search term.
                for word in words[1:]:
                    more = _find(tokens, used, [word])
                    if more is not None:
                        used.update(more)
                out.category = slug
                out.matches.append(Match(key="category", label="Kategorie", value=name))
                break

    out.rest = " ".join(t for i, t in enumerate(original) if i not in used)
    return out


def extract_filters(session: Session, query: str, category_slug: str | None) -> Extraction:
    """Extraction against the set filters of one category (or all categories)."""
    merged: dict[str, tuple[str, set[str]]] = {}
    for schema in _schemas(session, category_slug):
        label, values = merged.setdefault(schema.attr_key, (schema.label, set()))
        values.update(str(v) for v in (schema.config or {}).get("values", []))
    categories = None
    if not category_slug:
        categories = [(c.slug, c.name) for c in session.scalars(select(Category))]
    return extract(
        query, [(k, label, sorted(vals)) for k, (label, vals) in merged.items()], categories
    )
