"""Integration tests against a real Postgres (see conftest)."""

import pytest

from brain.models import Category, FilterSchema, Product

pytestmark = pytest.mark.db

ADMIN = {"X-Admin-Token": "test-admin-token"}


def _category(db, slug="tricka", name="Trička"):
    cat = Category(slug=slug, name=name)
    db.add(cat)
    db.commit()
    return cat


def _ingest(client, **overrides):
    body = {
        "category_slug": "tricka",
        "name": "Bavlněné tričko Basic",
        "price_czk": 349,
        "attributes": {"size": ["S", "M"], "color": "černá"},
        **overrides,
    }
    res = client.post("/ingest", json=body, headers=ADMIN)
    assert res.status_code == 200, res.text
    return res.json()


def test_ingest_requires_admin_token(client, db):
    _category(db)
    res = client.post("/ingest", json={"category_slug": "tricka", "name": "x"})
    assert res.status_code == 401


def test_ingest_creates_draft_and_is_idempotent_by_source_key(client, db):
    _category(db)
    first = _ingest(client, source_key="sha256:abc")
    second = _ingest(client, source_key="sha256:abc", name="Tričko Basic v2")
    assert first["status"] == "draft" and first["created"] is True
    assert second["id"] == first["id"] and second["created"] is False
    assert db.query(Product).count() == 1


def test_ingest_without_price(client, db):
    _category(db)
    assert _ingest(client, price_czk=None)["status"] == "draft"


def test_drafts_are_invisible_to_search_and_filters(client, db):
    _category(db)
    _ingest(client)
    res = client.post("/chat", json={"messages": [{"role": "user", "content": "tričko"}]})
    assert "Bavlněné" not in res.text.split("event: token")[0]
    assert db.query(FilterSchema).count() == 0


def test_listing_publishes_to_search_and_grows_filters(client, db):
    _category(db)
    pid = _ingest(client)["id"]
    drafts = client.get("/admin/products?status=draft", headers=ADMIN).json()
    assert drafts["total"] == 1 and drafts["counts"]["draft"] == 1

    res = client.post("/admin/products/status", json={"ids": [pid], "status": "listed"}, headers=ADMIN)
    assert res.status_code == 200
    keys = {f.attr_key for f in db.query(FilterSchema).all()}
    assert {"size", "color", "price_czk"} <= keys

    chat = client.post("/chat", json={"messages": [{"role": "user", "content": "chci tricko M"}]})
    products_block = chat.text.split("event: token")[0]
    assert "Bavlněné tričko Basic" in products_block


def test_fulltext_ignores_accents_and_respects_category(client, db):
    _category(db)
    _category(db, slug="boty", name="Boty")
    a = _ingest(client, name="Běžecké boty CloudRun", category_slug="boty")["id"]
    b = _ingest(client, name="Tričko na běhání")["id"]
    client.post("/admin/products/status", json={"ids": [a, b], "status": "listed"}, headers=ADMIN)

    from brain.search import search_products

    hits = search_products(db, "bezecke boty")
    assert hits and hits[0].id == a
    scoped = search_products(db, "behani", category_slug="tricka")
    assert [p.id for p in scoped] == [b]


def test_status_change_rejects_unknown_ids(client, db):
    res = client.post("/admin/products/status", json={"ids": [999], "status": "listed"}, headers=ADMIN)
    assert res.status_code == 404


def _sse_events(body: str) -> dict:
    import json

    out = {}
    for block in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        out.setdefault(lines["event"], []).append(json.loads(lines["data"]))
    return out


def test_chat_maps_words_to_filters_without_llm(client, db):
    _category(db, slug="zvirata", name="Zvířata")
    a = _ingest(client, category_slug="zvirata", name="Liška v lese", price_czk=None,
                attributes={"styl": "watercolor", "hodi_se_na": ["Hrnek", "Plakát"]})["id"]
    b = _ingest(client, category_slug="zvirata", name="Liška ve sněhu", price_czk=None,
                attributes={"styl": "anime", "hodi_se_na": ["Plakát"]})["id"]
    c = _ingest(client, category_slug="zvirata", name="Sova", price_czk=None,
                attributes={"styl": "watercolor", "hodi_se_na": ["Hrnek"]})["id"]
    client.post("/admin/products/status", json={"ids": [a, b, c], "status": "listed"}, headers=ADMIN)

    ev = _sse_events(client.post("/chat", json={
        "messages": [{"role": "user", "content": "liška akvarel na hrnek"}]}).text)
    assert ev["filters"][0]["filters"] == {"styl": ["watercolor"], "hodi_se_na": ["Hrnek"]}
    assert ev["filters"][0]["only"] is False
    assert [p["id"] for p in ev["products"][0]] == [a]
    answer = "".join(t["text"] for t in ev["token"])
    assert "Hledám bez asistenta" in answer and "Hrnek" in answer

    ev = _sse_events(client.post("/chat", json={
        "messages": [{"role": "user", "content": "na hrnek"}], "category": "zvirata"}).text)
    assert ev["filters"][0]["only"] is True and ev["filters"][0]["total"] == 2
    assert {p["id"] for p in ev["products"][0]} == {a, c}

    ev = _sse_events(client.post("/chat", json={
        "messages": [{"role": "user", "content": "sova"}]}).text)
    assert "filters" not in ev and [p["id"] for p in ev["products"][0]] == [c]
