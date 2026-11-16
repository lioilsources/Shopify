from brain.search import build_tsquery, rrf_fuse, strip_accents


def test_strip_accents_czech():
    assert strip_accents("Žluťoučký kůň tričko") == "Zlutoucky kun tricko"


def test_build_tsquery_or_prefix_and_exact_short_tokens():
    q = build_tsquery("Chci tričko velikosti M")
    terms = q.split(" | ")
    assert "tric:*" in terms  # "tricko" -> also matches "tricka"
    assert "m" in terms  # sizes match exactly, no prefix
    assert "velikos:*" in terms


def test_build_tsquery_drops_prepositions_keeps_sizes():
    terms = build_tsquery("tričko s liškou na výlet XL 42").split(" | ")
    assert "s" not in terms and "na" not in terms
    assert {"xl", "42", "lisk:*"} <= set(terms)


def test_build_tsquery_empty_and_dedup():
    assert build_tsquery("  !!! ") is None
    assert build_tsquery("boty boty") == "boty:*"


def test_rrf_fuse_prefers_items_in_both_rankings():
    fused = rrf_fuse([([1, 2, 3], 1.0), ([3, 4], 1.0)], limit=4)
    assert fused[0] == 3
    assert set(fused) == {1, 2, 3, 4}


def test_rrf_fuse_empty_leg_is_harmless():
    assert rrf_fuse([([5, 6], 1.0), ([], 1.0)], limit=5) == [5, 6]
