"""Klient pro vLLM (OpenAI-compatible) na DGX Sparku."""

from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from brain.config import settings


def client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=settings.llm_base_url.rstrip("/"),
        api_key=settings.llm_api_key or "not-needed",
    )


async def stream_chat(messages: list[dict]) -> AsyncIterator[str]:
    stream = await client().chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield delta


async def complete(messages: list[dict]) -> str:
    resp = await client().chat.completions.create(
        model=settings.llm_model,
        messages=messages,
    )
    return resp.choices[0].message.content or ""
