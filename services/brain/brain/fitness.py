"""Print profiles and image fitness ("Co si můžu dovolit", 03-USE-CASES.md).

Every image gets one grade per profile:
  ok       ✅ native resolution is enough at the profile's minimum DPI
  upscale  ⬆ needs upscaling within the cap of the image's class
  caveat   ⚠ crop of 15–35 %, outpainting a panorama, or upscaling above the cap
  no       ✖ do not offer
Until the print bench has run, every image uses the cautious 4× cap and an
upscale grade carries the note "orientačně".

Run `python -m brain.fitness` to resync profiles and recompute all products.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from brain.models import PrintProfile, Product, ProductFitness

PROFILES_FILE = Path(__file__).parent / "data" / "print_profiles.yaml"
UPSCALE_CAP = 4.0
CROP_OK = 0.15
CROP_MAX = 0.35
SUITS_ATTR = "hodi_se_na"
OFFERED = ("ok", "upscale")


@dataclass(frozen=True)
class Profile:
    id: str
    label_cs: str
    short_cm: float
    long_cm: float
    max_short_cm: float
    max_long_cm: float
    aspect: str
    dpi_min: float
    spec: dict[str, Any]

    @property
    def ratio(self) -> float:
        return self.long_cm / self.short_cm


@dataclass(frozen=True)
class Fitness:
    grade: str
    max_long_cm: float | None
    max_short_cm: float | None
    upscale: float | None
    crop: float | None
    note: str


def load_profiles(path: Path = PROFILES_FILE) -> list[Profile]:
    out = []
    for row in yaml.safe_load(path.read_text(encoding="utf-8")):
        short, long_ = sorted(row["area_cm"])
        max_short, max_long = sorted(row.get("max_area_cm") or row["area_cm"])
        out.append(
            Profile(
                id=row["id"],
                label_cs=row["label"]["cs"],
                short_cm=short,
                long_cm=long_,
                max_short_cm=max_short,
                max_long_cm=max_long,
                aspect=row.get("aspect", "fixed"),
                dpi_min=float(row["dpi"]["min"]),
                spec=row,
            )
        )
    return out


def _px(cm: float, dpi: float) -> float:
    return cm / 2.54 * dpi


def _cm(px: float, dpi: float) -> float:
    return px / dpi * 2.54


def grade_image(width: int, height: int, profile: Profile, cap: float = UPSCALE_CAP) -> Fitness:
    """Grade one image for one profile. Orientation is free (a poster can be portrait)."""
    il, is_ = max(width, height), min(width, height)
    r = il / is_
    notes: list[str] = []
    crop = 0.0
    outpaint = False

    if profile.aspect == "free":
        # The whole image fits into the print area, keeping its ratio.
        scale = min(profile.long_cm / il, profile.short_cm / is_)
        need_long = _px(il * scale, profile.dpi_min)
        avail_long = il
        out_ratio = r
    else:
        pr = profile.ratio
        if r > pr:
            avail_long, avail_short = is_ * pr, is_
        else:
            avail_long, avail_short = il, il / pr
        crop = 1 - (avail_long * avail_short) / (il * is_)
        out_ratio = pr
        if profile.aspect == "panorama" and crop > CROP_MAX:
            # Extend the image sideways instead of cutting most of it away.
            outpaint = True
            crop = 0.0
            avail_long = is_ * pr
        need_long = _px(profile.long_cm, profile.dpi_min)

    if outpaint:
        # Native pixels only cover the short side; that side sets the resolution.
        upscale = _px(profile.short_cm, profile.dpi_min) / is_
    else:
        upscale = need_long / avail_long

    if upscale <= 1:
        grade = "ok"
    elif upscale <= cap:
        grade = "upscale"
        notes.append("orientačně, tiskový bench ještě neproběhl")
    else:
        grade = "caveat"
        notes.append(f"zvětšení {upscale:.1f}× nad strop {cap:.0f}×")

    if outpaint:
        grade = "caveat" if grade in OFFERED else grade
        notes.append("dopočet okrajů na panorama")
    elif crop > CROP_MAX:
        grade = "no"
        notes = [f"ořez {crop:.0%} je příliš velký"]
    elif crop > CROP_OK:
        grade = "caveat" if grade in OFFERED else grade
        notes.append(f"ořez {crop:.0%}")

    # Largest size within the cap, never beyond what the profile offers.
    if outpaint:
        max_short = min(_cm(is_ * cap, profile.dpi_min), profile.max_short_cm)
        max_long = max_short * out_ratio
    else:
        max_long = min(_cm(avail_long * cap, profile.dpi_min), profile.max_long_cm)
        max_short = max_long / out_ratio
        if max_short > profile.max_short_cm:
            max_short = profile.max_short_cm
            max_long = max_short * out_ratio
    if grade == "no":
        max_long = max_short = None

    return Fitness(
        grade=grade,
        max_long_cm=round(max_long, 1) if max_long else None,
        max_short_cm=round(max_short, 1) if max_short else None,
        upscale=round(upscale, 2),
        crop=round(crop, 3),
        note="; ".join(notes),
    )


def sync_profiles(session: Session, profiles: list[Profile] | None = None) -> list[Profile]:
    """Upsert the seed into print_profiles. Profiles missing from the seed get inactive."""
    profiles = profiles or load_profiles()
    seen = set()
    for p in profiles:
        row = session.get(PrintProfile, p.id) or PrintProfile(id=p.id)
        row.group_key = p.spec.get("group", "")
        row.label_cs = p.label_cs
        row.label_en = p.spec["label"].get("en", p.label_cs)
        row.spec = p.spec
        row.phase = int(p.spec.get("phase", 0))
        row.active = True
        session.add(row)
        seen.add(p.id)
    for row in session.scalars(select(PrintProfile).where(PrintProfile.id.not_in(seen))):
        row.active = False
    session.flush()
    return profiles


def grade_all(width: int, height: int, profiles: list[Profile]) -> dict[str, Fitness]:
    return {p.id: grade_image(width, height, p) for p in profiles}


def suits_labels(grades: dict[str, Fitness], profiles: list[Profile]) -> list[str]:
    """Values of the public "Hodí se na" filter: profiles graded ✅ or ⬆."""
    return [p.label_cs for p in profiles if grades[p.id].grade in OFFERED]


def store_fitness(session: Session, product: Product, grades: dict[str, Fitness]) -> None:
    session.execute(delete(ProductFitness).where(ProductFitness.product_id == product.id))
    for profile_id, f in grades.items():
        session.add(
            ProductFitness(
                product_id=product.id,
                profile_id=profile_id,
                grade=f.grade,
                max_long_cm=f.max_long_cm,
                max_short_cm=f.max_short_cm,
                upscale=f.upscale,
                crop=f.crop,
                note=f.note,
            )
        )


def recompute_all(session: Session) -> int:
    """Recompute fitness and the "Hodí se na" attribute for every image product."""
    from brain.filters import merge_attributes
    from brain.models import STATUS_LISTED

    profiles = sync_profiles(session)
    count = 0
    for product in session.scalars(select(Product).where(Product.image_sha256.is_not(None))):
        meta = product.source_meta or {}
        w, h = meta.get("width"), meta.get("height")
        if not (isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0):
            continue
        grades = grade_all(w, h, profiles)
        store_fitness(session, product, grades)
        product.attributes = {**(product.attributes or {}), SUITS_ATTR: suits_labels(grades, profiles)}
        if product.status == STATUS_LISTED:
            merge_attributes(session, product.category_id, {SUITS_ATTR: product.attributes[SUITS_ATTR]})
        count += 1
    session.commit()
    return count


def main() -> int:
    from brain.db import SessionLocal

    with SessionLocal() as session:
        print(f"přepočítáno {recompute_all(session)} obrázků")
    return 0


if __name__ == "__main__":
    sys.exit(main())
