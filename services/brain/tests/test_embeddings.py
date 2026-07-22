import math

from brain.embeddings import mock_embed


def _cos(a, b):
    return sum(x * y for x, y in zip(a, b))


def test_mock_embed_is_deterministic_and_normalized():
    a = mock_embed("běžecké boty bílá", 128)
    b = mock_embed("běžecké boty bílá", 128)
    assert a == b
    assert math.isclose(math.sqrt(sum(v * v for v in a)), 1.0, rel_tol=1e-6)


def test_mock_embed_similarity_reflects_word_overlap():
    shoes = mock_embed("běžecké boty na silnici", 256)
    similar = mock_embed("boty na běhání běžecké", 256)
    unrelated = mock_embed("NAS disk 8TB CMR", 256)
    assert _cos(shoes, similar) > _cos(shoes, unrelated)
