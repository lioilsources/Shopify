from brain.filters import infer_kind, _initial_config, _widen
from brain.models import FilterSchema


def test_infer_kind():
    assert infer_kind(True) == "bool"
    assert infer_kind(4) == "range"
    assert infer_kind(4.5) == "range"
    assert infer_kind(["S", "M"]) == "set"
    assert infer_kind("černá") == "set"
    assert infer_kind("x" * 100) == "text"


def test_initial_config_range():
    assert _initial_config("range", 4) == {"min": 4, "max": 4}


def test_initial_config_set_sorts_numerically():
    config = _initial_config("set", ["30", "29", "31"])
    assert config["values"] == ["29", "30", "31"]


def test_widen_range():
    schema = FilterSchema(kind="range", config={"min": 4, "max": 4})
    _widen(schema, 8)
    assert schema.config == {"min": 4, "max": 8}
    _widen(schema, 2)
    assert schema.config == {"min": 2, "max": 8}


def test_widen_set_unions_values():
    schema = FilterSchema(kind="set", config={"values": ["S", "M"]})
    _widen(schema, ["M", "XL"])
    assert set(schema.config["values"]) == {"S", "M", "XL"}
