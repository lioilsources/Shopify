"""Test setup.

Unit tests need no database. Integration tests (marked `db`) run only when
TEST_DATABASE_URL points to a disposable database (e.g. chatshop_test next to
the dev DB on JODA); they migrate it and wipe all tables between tests.
"""

import os

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
# Must be set before brain.config is imported anywhere.
if TEST_DATABASE_URL:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
else:
    os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://unused@localhost:1/unused")
# Tests never call the GPU gateway.
os.environ["LLM_BASE_URL"] = ""
os.environ["EMBEDDINGS_BASE_URL"] = ""
os.environ["ADMIN_TOKEN"] = "test-admin-token"

import pytest  # noqa: E402


def pytest_collection_modifyitems(config, items):
    if TEST_DATABASE_URL:
        return
    skip = pytest.mark.skip(reason="TEST_DATABASE_URL není nastavené")
    for item in items:
        if "db" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def migrated():
    from alembic import command
    from alembic.config import Config

    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    command.upgrade(cfg, "head")


@pytest.fixture
def db(migrated):
    from sqlalchemy import text

    from brain.db import SessionLocal, engine

    with engine.begin() as conn:
        conn.execute(
            text("TRUNCATE product_embeddings, products, filter_schemas, categories RESTART IDENTITY CASCADE")
        )
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient

    from brain.main import app

    return TestClient(app)
