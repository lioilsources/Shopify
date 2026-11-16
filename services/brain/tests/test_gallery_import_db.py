"""Gallery import against a fake export (contract: docs/GALLERY_EXPORT.md)."""

import hashlib
import json

import httpx
import pytest

from brain.gallery_client import GalleryExport
from brain.gallery_import import run_import
from brain.models import Category, FilterSchema, Product
from brain.storage import LocalStorage

pytestmark = pytest.mark.db

ADMIN = {"X-Admin-Token": "test-admin-token"}

def _png_bytes(color):
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (300, 200), color).save(buf, "PNG")
    return buf.getvalue()


IMG_OK = _png_bytes((200, 120, 40))
IMG_DEV = b"\x89PNG fake flux dev"
SHA_OK = hashlib.sha256(IMG_OK).hexdigest()
SHA_DEV = hashlib.sha256(IMG_DEV).hexdigest()


def _item(**kw):
    base = {
        "imageId": "img-fox",
        "sha256": SHA_OK,
        "theme": "animals",
        "caption": "akvarelová liška v lese",
        "prompt": "watercolor fox in a forest",
        "params": {"model": "qwen-image"},
        "style": "akvarel",
        "subject": "liška",
        "tags": ["fox", "forest"],
        "rootNodeId": "node-1",
        "width": 1536,
        "height": 1024,
        "band": "safe",
        "addedAt": "2026-11-16T08:00:00Z",
        "revoked": False,
    }
    return {**base, **kw}


class FakeGallery:
    """Serves pages per `since` cursor and originals by sha."""

    def __init__(self):
        self.pages: dict[str | None, list[dict]] = {}
        self.blobs = {SHA_OK: IMG_OK, SHA_DEV: IMG_DEV}
        self.down_blobs: set[str] = set()
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path
        if path.startswith("/api/export/img/"):
            sha = path.rsplit("/", 1)[1]
            if sha in self.down_blobs or sha not in self.blobs:
                return httpx.Response(404)
            return httpx.Response(200, content=self.blobs[sha])
        since = request.url.params.get("since")
        page = int(request.url.params.get("cursor") or 0)
        pages = self.pages.get(since, [[]])
        nxt = str(page + 1) if page + 1 < len(pages) else None
        until = f"c{len(self.pages)}" if since is None else f"{since}+"
        return httpx.Response(
            200, text=json.dumps({"items": pages[page], "next": nxt, "until": until})
        )

    def client(self) -> GalleryExport:
        return GalleryExport(transport=httpx.MockTransport(self.handler), base_url="http://gallery.test")


@pytest.fixture
def fake():
    return FakeGallery()


@pytest.fixture
def storage(tmp_path):
    return LocalStorage(tmp_path)


def test_import_creates_drafts_with_gate_reasons(db, fake, storage):
    fake.pages[None] = [
        [_item()],
        [_item(imageId="img-dev", sha256=SHA_DEV, params={"model": "flux1-dev"}, tags=["signature"])],
        [_item(imageId="img-x", theme="robots")],
    ]
    stats = run_import(db, fake.client(), storage)
    assert stats["created"] == 2 and stats["skipped"] == 1
    assert stats["cursor"] == "c1"

    fox = db.query(Product).filter_by(source_key="gallery:img-fox").one()
    assert fox.status == "draft" and fox.price_czk is None
    assert fox.name == "Akvarelová liška v lese"
    assert fox.category.slug == "zvirata"
    assert fox.gate_reasons == []
    assert fox.attributes["pomer_stran"] == "3:2"
    assert "model" not in fox.attributes and fox.source_meta["model"] == "qwen-image"
    assert storage.get(SHA_OK) == IMG_OK

    dev = db.query(Product).filter_by(source_key="gallery:img-dev").one()
    codes = {r["code"] for r in dev.gate_reasons}
    assert codes == {"licence", "review"}

    # every request carries the export token
    assert all(r.headers.get("authorization", "").startswith("Bearer") for r in fake.requests)
    # all six themes exist with base filters
    assert db.query(Category).count() == 6
    assert db.query(FilterSchema).filter_by(attr_key="styl").count() == 6


def test_import_is_incremental_and_idempotent(db, fake, storage):
    fake.pages[None] = [[_item()]]
    run_import(db, fake.client(), storage)
    fake.pages["c1"] = [[_item(caption="liška v zimě")]]
    stats = run_import(db, fake.client(), storage)
    assert stats["created"] == 0 and stats["updated"] == 1
    assert db.query(Product).count() == 1
    assert db.query(Product).one().name == "Liška v zimě"


def test_blocking_reason_prevents_listing(client, db, fake, storage):
    fake.pages[None] = [[_item(imageId="img-dev", sha256=SHA_DEV, params={"model": "flux1-dev"})]]
    run_import(db, fake.client(), storage)
    pid = db.query(Product).one().id
    res = client.post("/admin/products/status", json={"ids": [pid], "status": "listed"}, headers=ADMIN)
    assert res.status_code == 409
    listed = client.get("/admin/products?status=draft", headers=ADMIN).json()
    assert listed["items"][0]["gate_reasons"][0]["code"] == "licence"


def test_revocation_hides_listed_product_but_removal_does_not(client, db, fake, storage):
    fake.pages[None] = [[_item()]]
    run_import(db, fake.client(), storage)
    pid = db.query(Product).one().id
    assert client.post("/admin/products/status", json={"ids": [pid], "status": "listed"}, headers=ADMIN).status_code == 200

    # Removal from the collection never shows up in the export: nothing changes (K4).
    fake.pages["c1"] = [[]]
    run_import(db, fake.client(), storage)
    db.expire_all()
    assert db.get(Product, pid).status == "listed"

    # A safety revocation hides it.
    fake.pages["c1+"] = [[_item(revoked=True)]]
    stats = run_import(db, fake.client(), storage)
    db.expire_all()
    assert stats["hidden"] == 1
    assert db.get(Product, pid).status == "hidden"
    assert {r["code"] for r in db.get(Product, pid).gate_reasons} >= {"revoked"}


def test_missing_original_blocks_until_recovered(client, db, fake, storage):
    fake.down_blobs.add(SHA_OK)
    fake.pages[None] = [[_item()]]
    stats = run_import(db, fake.client(), storage)
    assert stats["missing_original"] == 1
    product = db.query(Product).one()
    assert [r["code"] for r in product.gate_reasons] == ["original"]

    fake.down_blobs.clear()
    fake.pages["c1"] = [[]]
    stats = run_import(db, fake.client(), storage)
    db.expire_all()
    assert stats["originals_recovered"] == 1
    assert db.get(Product, product.id).gate_reasons == []


def test_failed_page_keeps_cursor(db, fake, storage):
    fake.pages[None] = [[_item()]]
    run_import(db, fake.client(), storage)

    def broken(request):
        return httpx.Response(500)

    with pytest.raises(httpx.HTTPStatusError):
        run_import(db, GalleryExport(transport=httpx.MockTransport(broken), base_url="http://g.test"), storage)
    from brain.models import ImportState

    db.expire_all()
    assert db.get(ImportState, "gallery:shop").cursor == "c1"


def test_admin_import_needs_configuration(client, db):
    assert client.post("/admin/import/gallery", headers=ADMIN).status_code == 503


def test_admin_media_serves_original(client, db, monkeypatch, tmp_path):
    from brain import admin

    store = LocalStorage(tmp_path)
    store.put(SHA_OK, IMG_OK)
    monkeypatch.setattr(admin, "LocalStorage", lambda: store)
    res = client.get(f"/admin/media/{SHA_OK}", headers=ADMIN)
    assert res.status_code == 200 and res.headers["content-type"] == "image/png"
    assert client.get(f"/admin/media/{SHA_OK}").status_code == 401
    assert client.get("/admin/media/" + "0" * 64, headers=ADMIN).status_code == 404


def test_import_grades_fitness_and_feeds_suits_filter(client, db, fake, storage):
    from brain.models import FilterSchema, ProductFitness

    fake.pages[None] = [[_item()]]
    run_import(db, fake.client(), storage)
    product = db.query(Product).one()
    grades = {f.profile_id: f.grade for f in db.query(ProductFitness).filter_by(product_id=product.id)}
    assert grades["poster"] == "upscale" and grades["mug"] == "caveat"  # 28 % crop
    assert "Plakát" in product.attributes["hodi_se_na"]
    assert "Hrnek" not in product.attributes["hodi_se_na"]

    # Not public before listing
    assert client.get(f"/products/{product.id}/fitness").status_code == 404
    client.post("/admin/products/status", json={"ids": [product.id], "status": "listed"}, headers=ADMIN)
    body = client.get(f"/products/{product.id}/fitness").json()
    assert body["items"][0]["grade"] in {"ok", "upscale"}
    suits = db.query(FilterSchema).filter_by(category_id=product.category_id, attr_key="hodi_se_na").one()
    db.refresh(suits)
    assert "Plakát" in suits.config["values"]
    assert any(p["id"] == "poster" for p in client.get("/profiles").json())


def test_public_preview_only_for_listed(client, db, fake, storage, monkeypatch):
    from brain import public

    monkeypatch.setattr(public, "LocalStorage", lambda: storage)
    fake.pages[None] = [[_item()]]
    run_import(db, fake.client(), storage)
    product = db.query(Product).one()
    assert product.image_url == f"/media/preview/{SHA_OK}.jpg"
    assert client.get(product.image_url).status_code == 404  # draft
    client.post("/admin/products/status", json={"ids": [product.id], "status": "listed"}, headers=ADMIN)
    res = client.get(product.image_url)
    assert res.status_code == 200 and res.headers["content-type"] == "image/jpeg"
    assert res.content[:2] == b"\xff\xd8"
    assert client.get("/media/preview/" + "0" * 64 + ".jpg").status_code == 404
