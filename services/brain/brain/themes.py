"""Shop themes (R13, plan 04): each theme is a catalogue category.

The gallery collection tags every item with one of these theme keys.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from brain.models import Category, FilterSchema

# key used by the gallery -> (category slug, Czech name)
THEMES: dict[str, tuple[str, str]] = {
    "animals": ("zvirata", "Zvířata"),
    "dinosaurs": ("dinosauri", "Dinosauři"),
    "machines": ("stroje", "Stroje a vozidla"),
    "plush": ("plysaci", "Plyšáci a hračky"),
    "landscapes": ("krajiny", "Krajiny a příroda"),
    "pets": ("psi-a-kocky", "Psi a kočky"),
    # Use-case themes (demo batch, plan 03): graphics for prints, seamless patterns.
    "prints": ("potisky", "Potisky na trička"),
    "patterns": ("vzory", "Vzory a tapety"),
    # R14: purely generated faces, demo only (never for sale, never from the gallery).
    "portraits": ("portrety", "Portréty"),
}

# Themes that only `brain.demo_import` may fill; the gallery import skips them.
DEMO_ONLY_THEMES = frozenset({"portraits"})

# Filters every image theme starts with; values grow from listed products.
IMAGE_FILTERS: list[tuple[str, str, str]] = [
    ("styl", "Styl", "set"),
    ("namet", "Námět", "set"),
    ("orientace", "Orientace", "set"),
    ("pomer_stran", "Poměr stran", "set"),
    ("megapixely", "Rozlišení (Mpx)", "range"),
    ("hodi_se_na", "Hodí se na", "set"),
]


def ensure_themes(session: Session) -> dict[str, Category]:
    """Create missing theme categories and their base filters. Idempotent."""
    out: dict[str, Category] = {}
    for key, (slug, name) in THEMES.items():
        category = session.scalar(select(Category).where(Category.slug == slug))
        if category is None:
            category = Category(slug=slug, name=name)
            session.add(category)
            session.flush()
        existing = set(
            session.scalars(
                select(FilterSchema.attr_key).where(FilterSchema.category_id == category.id)
            )
        )
        for attr_key, label, kind in IMAGE_FILTERS:
            if attr_key not in existing:
                session.add(
                    FilterSchema(
                        category_id=category.id, attr_key=attr_key, label=label, kind=kind, config={}
                    )
                )
        out[key] = category
    session.flush()
    return out
