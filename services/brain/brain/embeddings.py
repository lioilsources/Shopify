"""Klient pro embeddingy: TEI na DGX Sparku, nebo deterministický mock.

Mock skládá vektor z hash-seedovaných pseudonáhodných vektorů jednotlivých
slov — překrývající se slova dávají podobné vektory, takže similarity search
funguje i bez GPU (jen hůř).
"""

import hashlib
import math
import re

import httpx

from brain.config import settings


def _word_vector(word: str, dim: int) -> list[float]:
    out: list[float] = []
    counter = 0
    seed = word.encode("utf-8")
    while len(out) < dim:
        digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        out.extend(b / 255.0 - 0.5 for b in digest)
        counter += 1
    return out[:dim]


def mock_embed(text: str, dim: int) -> list[float]:
    words = re.findall(r"\w+", text.lower())
    if not words:
        words = ["empty"]
    acc = [0.0] * dim
    for word in words:
        for i, v in enumerate(_word_vector(word, dim)):
            acc[i] += v
    norm = math.sqrt(sum(v * v for v in acc)) or 1.0
    return [v / norm for v in acc]


def embed(text: str) -> list[float]:
    if not settings.embeddings_enabled:
        return mock_embed(text, settings.embedding_dim)
    resp = httpx.post(
        f"{settings.embeddings_base_url.rstrip('/')}/embed",
        json={"inputs": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()[0]
