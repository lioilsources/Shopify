"""Odvozování a rozšiřování filter schémat kategorie z atributů produktů.

Při vložení produktu se každý atribut promítne do `filter_schemas`:
nový atribut založí filtr (druh se odvodí z typu hodnoty), existující
set filtr rozšíří výčet hodnot, range filtr roztáhne meze.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from brain.models import FilterSchema

# Delší texty nemá smysl nabízet jako výčet — spadnou do fulltextu.
_SET_MAX_LEN = 40

PRICE_ATTR = "price_czk"
PRICE_LABEL = "Cena (Kč)"


def infer_kind(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "range"
    if isinstance(value, list):
        return "set"
    if isinstance(value, str) and len(value) <= _SET_MAX_LEN:
        return "set"
    return "text"


def _initial_config(kind: str, value: Any) -> dict[str, Any]:
    if kind == "range":
        return {"min": value, "max": value}
    if kind == "set":
        values = value if isinstance(value, list) else [value]
        return {"values": sorted({str(v) for v in values}, key=_set_sort_key)}
    return {}


def _set_sort_key(v: str):
    try:
        return (0, float(v), "")
    except ValueError:
        return (1, 0.0, v)


def _widen(schema: FilterSchema, value: Any) -> None:
    config = dict(schema.config or {})
    if schema.kind == "range" and isinstance(value, (int, float)) and not isinstance(value, bool):
        config["min"] = min(config.get("min", value), value)
        config["max"] = max(config.get("max", value), value)
    elif schema.kind == "set":
        values = value if isinstance(value, list) else [value]
        merged = set(config.get("values", [])) | {str(v) for v in values}
        config["values"] = sorted(merged, key=_set_sort_key)
    schema.config = config


def merge_attributes(
    session: Session,
    category_id: int,
    attributes: dict[str, Any],
    price_czk: float | None = None,
) -> None:
    """Promítne atributy produktu (a cenu) do filter schémat kategorie."""
    merged = dict(attributes)
    if price_czk is not None:
        merged[PRICE_ATTR] = float(price_czk)

    for attr_key, value in merged.items():
        if value is None:
            continue
        schema = session.scalar(
            select(FilterSchema).where(
                FilterSchema.category_id == category_id,
                FilterSchema.attr_key == attr_key,
            )
        )
        if schema is None:
            kind = infer_kind(value)
            label = PRICE_LABEL if attr_key == PRICE_ATTR else attr_key.replace("_", " ").capitalize()
            session.add(
                FilterSchema(
                    category_id=category_id,
                    attr_key=attr_key,
                    label=label,
                    kind=kind,
                    config=_initial_config(kind, value),
                )
            )
        else:
            _widen(schema, value)
    session.flush()
