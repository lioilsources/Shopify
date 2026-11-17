"""Import the curated shop collection from FineTuneGallery (plan 05, part B).

Each export item becomes a `draft` product keyed by `gallery:<imageId>`;
the owner publishes it in /admin/review. Runs are incremental (cursor in
`import_state`) and idempotent, so re-running after a crash is safe.

Removing an image from the collection changes nothing in the shop (K4);
only a safety revocation by the gallery hides the product.

Run: python -m brain.gallery_import
"""

import logging
import sys
from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from brain.catalog import set_status, upsert_product
from brain.config import settings
from brain.gallery_client import GalleryExport
from brain.fitness import SUITS_ATTR, Profile, grade_all, store_fitness, suits_labels, sync_profiles
from brain.gate import evaluate, reason
from brain.previews import preview_url
from brain.models import STATUS_HIDDEN, STATUS_LISTED, ImportState, Product
from brain.storage import LocalStorage
from brain.themes import THEMES, ensure_themes

log = logging.getLogger(__name__)

NAME_MAX = 80


@dataclass
class ImportStats:
    created: int = 0
    updated: int = 0
    hidden: int = 0
    skipped: int = 0
    missing_original: int = 0


def source_key(item: dict[str, Any]) -> str:
    # Other sources (demo batches) bring their own key.
    return item.get("sourceKey") or f"gallery:{item['imageId']}"


def _orientation(w: int, h: int) -> str:
    if abs(w - h) <= max(w, h) * 0.02:
        return "čtverec"
    return "na šířku" if w > h else "na výšku"


def _ratio(w: int, h: int) -> str:
    # Snap to the formats print profiles use (03-USE-CASES.md).
    known = {"1:1": 1.0, "4:3": 4 / 3, "3:2": 1.5, "16:9": 16 / 9, "2:1": 2.0,
             "3:4": 3 / 4, "2:3": 2 / 3, "9:16": 9 / 16, "1:2": 0.5}
    r = w / h
    label, value = min(known.items(), key=lambda kv: abs(kv[1] - r))
    return label if abs(value - r) / value < 0.04 else f"{w}:{h}"


def attributes_for(item: dict[str, Any]) -> dict[str, Any]:
    """Public filter attributes. Model, prompt and lineage stay in source_meta."""
    params = item.get("params") or {}
    attrs: dict[str, Any] = {}
    if style := (item.get("style") or params.get("style")):
        attrs["styl"] = str(style)
    if subject := (item.get("subject") or params.get("subject")):
        attrs["namet"] = str(subject)
    w, h = item.get("width"), item.get("height")
    if isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0:
        attrs["orientace"] = _orientation(w, h)
        attrs["pomer_stran"] = _ratio(w, h)
        attrs["megapixely"] = round(w * h / 1_000_000, 1)
    return attrs


def name_for(item: dict[str, Any], theme_name: str) -> str:
    caption = (item.get("caption") or "").strip()
    if caption:
        first = caption.split(". ")[0].strip().rstrip(".")
        if len(first) > NAME_MAX:
            first = first[: NAME_MAX - 1].rsplit(" ", 1)[0] + "…"
        return first[:1].upper() + first[1:]
    return f"{theme_name} {str(item['imageId'])[:8]}"


def _source_meta(item: dict[str, Any]) -> dict[str, Any]:
    keys = ("imageId", "rootNodeId", "prompt", "params", "tags", "width", "height",
            "band", "addedAt", "theme", "caption")
    meta = {k: item.get(k) for k in keys if item.get(k) is not None}
    model = (item.get("params") or {}).get("model") or item.get("model")
    if model:
        meta["model"] = model
    return meta


def _get_state(session: Session, source: str) -> ImportState:
    state = session.get(ImportState, source)
    if state is None:
        state = ImportState(source=source, cursor=None)
        session.add(state)
        session.flush()
    return state


def _fetch_original(gallery: GalleryExport, storage: LocalStorage, sha: str) -> bool:
    if storage.has(sha):
        return True
    try:
        storage.put(sha, gallery.image(sha))
        return True
    except Exception as exc:  # network, 404, checksum: retried on the next run
        log.warning("original %s not copied: %s", sha, exc)
        return False


def import_item(
    session: Session,
    gallery: GalleryExport,
    storage: LocalStorage,
    item: dict[str, Any],
    stats: ImportStats,
    categories: dict[str, Any] | None = None,
    profiles: list[Profile] | None = None,
) -> None:
    theme = THEMES.get(item.get("theme") or "")
    sha = (item.get("sha256") or "").lower()
    if theme is None or not item.get("imageId") or len(sha) != 64:
        log.warning("skipping export item %r: unknown theme or missing ids", item.get("imageId"))
        stats.skipped += 1
        return

    key = source_key(item)
    product = session.scalar(select(Product).where(Product.source_key == key))
    reasons = evaluate(item)

    if item.get("revoked"):
        if product is not None:
            product.gate_reasons = reasons
            if product.status != STATUS_HIDDEN:
                set_status(session, product, STATUS_HIDDEN)
                stats.hidden += 1
        else:
            stats.skipped += 1
        return

    if not _fetch_original(gallery, storage, sha):
        reasons.append(reason("original", "originál se nepodařilo zkopírovat", True))
        stats.missing_original += 1

    category = (categories or ensure_themes(session))[item["theme"]]
    attributes = attributes_for(item)
    grades = None
    w, h = item.get("width"), item.get("height")
    if isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0:
        profiles = profiles if profiles is not None else sync_profiles(session)
        grades = grade_all(w, h, profiles)
        attributes[SUITS_ATTR] = suits_labels(grades, profiles)
    product, created = upsert_product(
        session,
        category_id=category.id,
        name=name_for(item, theme[1]),
        description=(item.get("caption") or "").strip(),
        price_czk=None,
        image_url=preview_url(sha),
        attributes=attributes,
        source_key=key,
    )
    if grades is not None:
        store_fitness(session, product, grades)
    product.gate_reasons = reasons
    product.source_meta = _source_meta(item)
    product.image_sha256 = sha
    if product.status == STATUS_LISTED and any(r["blocking"] for r in reasons):
        set_status(session, product, STATUS_HIDDEN)
        stats.hidden += 1
    if created:
        stats.created += 1
    else:
        stats.updated += 1


def retry_missing_originals(session: Session, gallery: GalleryExport, storage: LocalStorage) -> int:
    fixed = 0
    for product in session.scalars(select(Product).where(Product.image_sha256.is_not(None))):
        if not any(r.get("code") == "original" for r in product.gate_reasons or []):
            continue
        if _fetch_original(gallery, storage, product.image_sha256):
            product.gate_reasons = [r for r in product.gate_reasons if r.get("code") != "original"]
            fixed += 1
    return fixed


def run_import(
    session: Session,
    gallery: GalleryExport | None = None,
    storage: LocalStorage | None = None,
    collection: str | None = None,
) -> dict[str, Any]:
    collection = collection or settings.gallery_collection
    own_client = gallery is None
    gallery = gallery or GalleryExport()
    storage = storage or LocalStorage()
    stats = ImportStats()
    try:
        state = _get_state(session, f"gallery:{collection}")
        categories = ensure_themes(session)
        profiles = sync_profiles(session)
        until = state.cursor
        for items, page_until in gallery.changes(collection, state.cursor):
            for item in items:
                import_item(session, gallery, storage, item, stats, categories, profiles)
            session.flush()
            until = page_until or until
        fixed = retry_missing_originals(session, gallery, storage)
        # The cursor moves only after every page succeeded; a failed run re-reads.
        state.cursor = until
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if own_client:
            gallery.close()
    return {**asdict(stats), "originals_recovered": fixed, "cursor": until}


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    if not settings.gallery_enabled:
        print("GALLERY_URL a GALLERY_EXPORT_TOKEN nejsou nastavené.", file=sys.stderr)
        return 2
    from brain.db import SessionLocal

    with SessionLocal() as session:
        print(run_import(session))
    return 0


if __name__ == "__main__":
    sys.exit(main())
