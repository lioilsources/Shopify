"""Demo batch import against a real Postgres."""

import io
import json

import pytest
from PIL import Image
from sqlalchemy import select

from brain.demo_import import hide_legacy, purge_demo, run_demo_import
from brain.models import Category, Product
from brain.storage import LocalStorage

pytestmark = pytest.mark.db


def _png(path, w, h, color):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), color).save(buf, format="PNG")
    path.write_bytes(buf.getvalue())


SPEC = {
    "batch": "demo-t",
    "items": [
        {"id": "plush-01", "theme": "plush", "style": "plyšák", "subject": "medvídek",
         "name": "Plyšový medvídek", "prompt": "plush bear", "width": 64, "height": 64, "seed": 1},
        {"id": "patterns-01", "theme": "patterns", "style": "art deco", "subject": "geometrie",
         "name": "Vzor: vějíře", "prompt": "fan pattern", "width": 96, "height": 64, "seed": 2},
        {"id": "animals-01", "theme": "animals", "style": "akvarel", "subject": "liška",
         "name": "Liška", "prompt": "fox", "width": 64, "height": 96, "seed": 3},
        {"id": "missing-01", "theme": "animals", "name": "Nevygenerováno", "prompt": "x"},
    ],
}


def _outputs(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    _png(out / "plush-01.png", 1024, 1024, "brown")
    _png(out / "patterns-01.png", 1536, 1024, "gold")
    _png(out / "animals-01.png", 1024, 1536, "orange")
    manifest = [
        {"id": "plush-01", "file": "plush-01.png", "model": "FLUX.1-schnell", "seed": 1},
        {"id": "patterns-01", "file": "patterns-01.png", "model": "Qwen-Image", "seed": 2},
        # Not on the licence allowlist: imported, but stays a draft.
        {"id": "animals-01", "file": "animals-01.png", "model": "FLUX.1-dev", "seed": 3},
    ]
    (out / "manifest.json").write_text(json.dumps(manifest))
    return out


def test_demo_import_lists_licensed_flags_demo_and_is_idempotent(db, tmp_path):
    out = _outputs(tmp_path)
    storage = LocalStorage(tmp_path / "media")
    stats = run_demo_import(db, SPEC, out, storage)
    assert stats["items"] == 3 and stats["created"] == 3 and stats["listed"] == 2

    rows = {p.source_key: p for p in db.scalars(select(Product))}
    plush = rows["demo:demo-t:plush-01"]
    assert plush.demo and plush.status == "listed"
    assert plush.attributes["styl"] == "plyšák" and plush.attributes["orientace"] == "čtverec"
    assert plush.attributes["hodi_se_na"]  # fitness ran
    assert storage.has(plush.image_sha256)
    assert rows["demo:demo-t:patterns-01"].category.slug == "vzory"
    fox = rows["demo:demo-t:animals-01"]
    assert fox.status == "draft" and any(r["code"] == "licence" for r in fox.gate_reasons)

    again = run_demo_import(db, SPEC, out, storage)
    assert again["created"] == 0 and again["updated"] == 3 and again["listed"] == 0


def test_hide_legacy_and_purge(db, tmp_path):
    cat = Category(slug="boty", name="Boty")
    db.add(cat)
    db.flush()
    db.add(Product(category_id=cat.id, name="Boty", description="", price_czk=1, image_url="",
                   attributes={}, status="listed"))
    db.commit()
    run_demo_import(db, SPEC, _outputs(tmp_path), LocalStorage(tmp_path / "media"))

    assert hide_legacy(db) == 1
    assert db.scalar(select(Product).where(Product.name == "Boty")).status == "hidden"
    assert purge_demo(db) == 3
    assert [p.name for p in db.scalars(select(Product))] == ["Boty"]
