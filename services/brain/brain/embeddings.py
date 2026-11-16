"""Klient pro embeddingy: OpenAI-compatible /v1/embeddings (vLLM za AiStack
gatewayí na DGX Sparku), nebo deterministický mock.

Mock skládá vektor z hash-seedovaných pseudonáhodných vektorů jednotlivých
slov — překrývající se slova dávají podobné vektory, takže similarity search
funguje i bez GPU (jen hůř).
"""

import hashlib
import logging
import math
import re

import httpx

from brain.config import settings

log = logging.getLogger(__name__)


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


def _remote_embed(text: str) -> list[float]:
    api_key = settings.embeddings_api_key or settings.llm_api_key
    headers = {"Authorization": f"Bearer {api_key}"} if api_key and api_key != "not-needed" else {}
    resp = httpx.post(
        f"{settings.embeddings_base_url.rstrip('/')}/embeddings",
        # encoding_format explicitly: LiteLLM otherwise sends None and vLLM rejects it
        json={"model": settings.embeddings_model, "input": text, "encoding_format": "float"},
        headers=headers,
        timeout=settings.embeddings_timeout,
    )
    resp.raise_for_status()
    return resp.json()["data"][0]["embedding"]


def embed(text: str) -> list[float]:
    """Embedding with the configured model; raises when the gateway is down."""
    if not settings.embeddings_enabled:
        return mock_embed(text, settings.embedding_dim)
    return _remote_embed(text)


def try_embed(text: str) -> list[float] | None:
    """Like embed(), but returns None when the gateway is unavailable.

    The shop must work without GPU (plan 02, invariant 5): callers fall back
    to fulltext search, and ingest stores the product without a vector
    (fill later with `python -m brain.seed --reembed`).
    """
    try:
        return embed(text)
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        log.warning("embeddings unavailable, falling back to fulltext: %s", exc)
        return None
