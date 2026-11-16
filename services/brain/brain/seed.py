"""Seed demo dat: trička, boty, HDD — včetně filter schémat a embeddingů.

Spuštění: python -m brain.seed             # naplní prázdnou DB
          python -m brain.seed --reembed   # přepočítá embeddingy všech produktů
                                           # (nutné po přechodu mock -> reálný model)
"""

import sys

from sqlalchemy import select

from brain.catalog import refresh_embedding
from brain.db import SessionLocal
from brain.filters import merge_attributes
from brain.models import STATUS_LISTED, Category, Product

CATEGORIES = [
    {"slug": "tricka", "name": "Trička"},
    {"slug": "boty", "name": "Boty"},
    {"slug": "hdd", "name": "Disky"},
]

PRODUCTS = [
    # Trička
    {
        "category": "tricka",
        "name": "Bavlněné tričko Basic černé",
        "description": "Jednobarevné tričko ze 100% organické bavlny, střih unisex.",
        "price_czk": 349,
        "image_url": "https://picsum.photos/seed/tricko1/600/600",
        "attributes": {"size": ["S", "M", "L", "XL"], "color": "černá", "material": "bavlna"},
    },
    {
        "category": "tricka",
        "name": "Tričko s potiskem Retro Wave",
        "description": "Modré tričko s neonovým synthwave potiskem.",
        "price_czk": 499,
        "image_url": "https://picsum.photos/seed/tricko2/600/600",
        "attributes": {"size": ["M", "L"], "color": "modrá", "material": "bavlna"},
    },
    {
        "category": "tricka",
        "name": "Sportovní funkční tričko",
        "description": "Prodyšné funkční tričko na běhání, rychleschnoucí.",
        "price_czk": 599,
        "image_url": "https://picsum.photos/seed/tricko3/600/600",
        "attributes": {"size": ["S", "M", "L", "XL"], "color": "červená", "material": "polyester"},
    },
    # Boty
    {
        "category": "boty",
        "name": "Běžecké boty CloudRun",
        "description": "Lehké běžecké boty s pěnovou mezipodešví na silnici.",
        "price_czk": 2790,
        "image_url": "https://picsum.photos/seed/boty1/600/600",
        "attributes": {"size": ["40", "41", "42", "43", "44"], "color": "bílá"},
    },
    {
        "category": "boty",
        "name": "Kožené městské tenisky",
        "description": "Elegantní kožené tenisky do města, ručně šité.",
        "price_czk": 3490,
        "image_url": "https://picsum.photos/seed/boty2/600/600",
        "attributes": {"size": ["41", "42", "43"], "color": "hnědá"},
    },
    {
        "category": "boty",
        "name": "Dětské sandály LedFlash",
        "description": "Dětské sandály s blikající podrážkou.",
        "price_czk": 890,
        "image_url": "https://picsum.photos/seed/boty3/600/600",
        "attributes": {"size": ["29", "30", "31", "32"], "color": "růžová"},
    },
    # Disky
    {
        "category": "hdd",
        "name": "HDD Seagate IronWolf 4TB",
        "description": "3.5\" NAS disk, 5400 ot/min, určený pro provoz 24/7.",
        "price_czk": 2990,
        "image_url": "https://picsum.photos/seed/hdd1/600/600",
        "attributes": {"capacity_tb": 4, "form_factor": "3.5\"", "nas_ready": True},
    },
    {
        "category": "hdd",
        "name": "HDD WD Red Plus 8TB",
        "description": "3.5\" NAS disk s CMR záznamem pro RAID pole.",
        "price_czk": 5490,
        "image_url": "https://picsum.photos/seed/hdd2/600/600",
        "attributes": {"capacity_tb": 8, "form_factor": "3.5\"", "nas_ready": True},
    },
    {
        "category": "hdd",
        "name": "SSD Samsung 990 Pro 2TB",
        "description": "NVMe M.2 SSD, čtení až 7450 MB/s, pro hry i práci.",
        "price_czk": 4290,
        "image_url": "https://picsum.photos/seed/hdd3/600/600",
        "attributes": {"capacity_tb": 2, "form_factor": "M.2", "nas_ready": False},
    },
]


def reembed() -> None:
    """Recompute vectors of all products with the configured model."""
    with SessionLocal() as session:
        products = list(session.scalars(select(Product)))
        done = sum(refresh_embedding(session, p) for p in products)
        session.commit()
        print(f"Re-embed hotov: {done}/{len(products)} produktů.")
        if done < len(products):
            sys.exit("Embeddingy nejsou dostupné, zbytek zůstal bez vektoru.")


def run() -> None:
    with SessionLocal() as session:
        if session.scalar(select(Product).limit(1)) is not None:
            print("Seed přeskočen — databáze už obsahuje produkty.")
            return

        categories: dict[str, Category] = {}
        for c in CATEGORIES:
            cat = session.scalar(select(Category).where(Category.slug == c["slug"]))
            if cat is None:
                cat = Category(**c)
                session.add(cat)
                session.flush()
            categories[c["slug"]] = cat

        for p in PRODUCTS:
            cat = categories[p["category"]]
            product = Product(
                category_id=cat.id,
                name=p["name"],
                description=p["description"],
                price_czk=p["price_czk"],
                image_url=p["image_url"],
                attributes=p["attributes"],
                status=STATUS_LISTED,  # demo data is approved
            )
            session.add(product)
            session.flush()
            merge_attributes(session, cat.id, p["attributes"], price_czk=p["price_czk"])
            refresh_embedding(session, product)

        session.commit()
        print(f"Seed hotov: {len(CATEGORIES)} kategorie, {len(PRODUCTS)} produktů.")


if __name__ == "__main__":
    if "--reembed" in sys.argv:
        reembed()
    else:
        run()
