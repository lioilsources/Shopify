"""Publication gate for gallery images (plan 02 §6, docs/CONTENT_POLICY.md).

The gate only sorts: it never lists anything by itself. Blocking reasons
(unlicensed model, safety revocation by the gallery) keep a product out of
the catalogue; non-blocking ones flag it for a closer look during review.
"""

import re
from typing import Any

# Generation models whose outputs may be sold and which may run in a paid
# service (docs/LICENCES.md, "Závěr pro R7"). Compared on normalised names.
ALLOWED_MODELS = ("flux1schnell", "qwenimage", "flux2klein4b", "zimageturbo")
# Explicitly out even though a prefix might look similar.
DENIED_MODELS = ("flux2klein9b", "flux1dev", "flux2dev", "kontextdev", "filldev")

# WD14-style tags that need a human look (third-party rights, text, people).
REVIEW_TAGS: dict[str, str] = {
    "text": "nápis",
    "english_text": "nápis",
    "signature": "podpis",
    "watermark": "vodoznak",
    "artist_name": "podpis",
    "logo": "logo",
    "brand_name": "značka",
    "copyright_name": "cizí postava",
    "character_name": "cizí postava",
    "1girl": "člověk",
    "1boy": "člověk",
    "multiple_girls": "člověk",
    "multiple_boys": "člověk",
    "human": "člověk",
    "person": "člověk",
    "face": "obličej",
    "child": "dítě",
}


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def licence_ok(model: str | None) -> bool:
    if not model:
        return False
    n = _norm(model)
    if any(d in n for d in DENIED_MODELS):
        return False
    return any(a in n for a in ALLOWED_MODELS)


def reason(code: str, detail: str, blocking: bool) -> dict[str, Any]:
    return {"code": code, "detail": detail, "blocking": blocking}


def evaluate(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Gate findings for one export item."""
    reasons: list[dict[str, Any]] = []
    if item.get("revoked"):
        reasons.append(reason("revoked", "galerie obrázek stáhla (bezpečnost)", True))
    model = (item.get("params") or {}).get("model") or item.get("model")
    if not licence_ok(model):
        reasons.append(reason("licence", f"model bez povolené licence: {model or 'neznámý'}", True))
    hits = sorted({label for tag in item.get("tags") or [] if (label := REVIEW_TAGS.get(tag))})
    if hits:
        reasons.append(reason("review", "zkontrolovat: " + ", ".join(hits), False))
    return reasons
