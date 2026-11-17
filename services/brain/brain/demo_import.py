"""Import a generated demo batch into the catalogue, flagged `demo`.

Input: the batch spec (demo/batch-01.yaml: id, theme, style, subject, name,
prompt, size, seed) and the generator output dir with <id>.png and
manifest.json ([{id, file, model, seed, width, height, steps}]).

Each image goes through the same path as a gallery item (original copy,
licence gate, fitness, "Hodí se na") with source_key demo:<batch>:<id>.
Items without a blocking gate reason are listed right away: the owner asked
for the demo batch, it is labelled "Demo" on the web and purged in one go.

    python -m brain.demo_import demo/batch-01.yaml run/demo/batch-01 [--hide-legacy]
    python -m brain.demo_import --purge
"""

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml
from PIL import Image
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from brain.catalog import set_status
from brain.fitness import sync_profiles
from brain.gallery_import import ImportStats, import_item
from brain.models import STATUS_HIDDEN, STATUS_LISTED, Product, ProductEmbedding, ProductFitness
from brain.storage import LocalStorage
from brain.themes import ensure_themes

log = logging.getLogger(__name__)


class _LocalFiles:
    """Stands in for the gallery client: originals come from the output dir."""

    def __init__(self, by_sha: dict[str, Path]):
        self.by_sha = by_sha

    def image(self, sha: str) -> bytes:
        return self.by_sha[sha].read_bytes()


def build_items(spec: dict[str, Any], out_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    batch = spec["batch"]
    manifest = {m["id"]: m for m in json.loads((out_dir / "manifest.json").read_text())}
    items, files = [], {}
    for entry in spec["items"]:
        gen = manifest.get(entry["id"])
        if gen is None:
            log.warning("%s: not generated, skipped", entry["id"])
            continue
        path = out_dir / gen.get("file", f"{entry['id']}.png")
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        with Image.open(path) as img:  # trust the pixels, not the manifest
            width, height = img.size
        files[sha] = path
        items.append(
            {
                "sourceKey": f"demo:{batch}:{entry['id']}",
                "imageId": f"{batch}/{entry['id']}",
                "sha256": sha,
                "theme": entry["theme"],
                "caption": entry["name"],
                "prompt": entry["prompt"],
                "style": entry.get("style"),
                "subject": entry.get("subject"),
                "width": width,
                "height": height,
                "params": {
                    "model": gen.get("model"),
                    "seed": gen.get("seed", entry.get("seed")),
                    "steps": gen.get("steps"),
                },
            }
        )
    return items, files


def run_demo_import(
    session: Session, spec: dict[str, Any], out_dir: Path, storage: LocalStorage | None = None
) -> dict[str, Any]:
    storage = storage or LocalStorage()
    items, files = build_items(spec, out_dir)
    source = _LocalFiles(files)
    stats = ImportStats()
    categories = ensure_themes(session)
    profiles = sync_profiles(session)
    listed = 0
    try:
        for item in items:
            import_item(session, source, storage, item, stats, categories, profiles)
            product = session.scalar(select(Product).where(Product.source_key == item["sourceKey"]))
            if product is None:
                continue
            product.demo = True
            product.description = f"Demo ukázka. {item['caption']}."
            blocked = any(r["blocking"] for r in product.gate_reasons or [])
            if not blocked and product.status != STATUS_LISTED:
                set_status(session, product, STATUS_LISTED)
                listed += 1
        session.commit()
    except Exception:
        session.rollback()
        raise
    return {"items": len(items), "created": stats.created, "updated": stats.updated,
            "skipped": stats.skipped, "missing_original": stats.missing_original, "listed": listed}


def purge_demo(session: Session) -> int:
    """Delete every demo product (originals stay in storage, keyed by sha)."""
    ids = list(session.scalars(select(Product.id).where(Product.demo.is_(True))))
    if ids:
        session.execute(delete(ProductFitness).where(ProductFitness.product_id.in_(ids)))
        session.execute(delete(ProductEmbedding).where(ProductEmbedding.product_id.in_(ids)))
        session.execute(delete(Product).where(Product.id.in_(ids)))
    session.commit()
    return len(ids)


def hide_legacy(session: Session) -> int:
    """Hide listed products without an image original (the ChatShop sample shoes,
    disks and shirts) so the catalogue shows only images. Reversible in /admin/review."""
    rows = session.scalars(
        select(Product).where(Product.status == STATUS_LISTED, Product.image_sha256.is_(None))
    ).all()
    for product in rows:
        set_status(session, product, STATUS_HIDDEN)
    session.commit()
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO)
    ap = argparse.ArgumentParser(prog="python -m brain.demo_import")
    ap.add_argument("spec", nargs="?", type=Path)
    ap.add_argument("out_dir", nargs="?", type=Path)
    ap.add_argument("--purge", action="store_true", help="delete all demo products")
    ap.add_argument("--hide-legacy", action="store_true",
                    help="also hide listed products without an image (ChatShop samples)")
    args = ap.parse_args(argv)
    from brain.db import SessionLocal

    with SessionLocal() as session:
        if args.purge:
            print({"purged": purge_demo(session)})
            return 0
        if not (args.spec and args.out_dir):
            ap.error("spec and out_dir are required")
        spec = yaml.safe_load(args.spec.read_text())
        print(run_demo_import(session, spec, args.out_dir))
        if args.hide_legacy:
            print({"hidden_legacy": hide_legacy(session)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
