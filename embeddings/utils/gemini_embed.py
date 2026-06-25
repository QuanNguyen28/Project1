from __future__ import annotations

import math

import hashlib

import re

import time

from functools import lru_cache

from typing import List

from google import genai

from google.genai import types

from src.core.config import (
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_DELAY_SECONDS,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_EMBED_MODEL,
    VECTOR_DIM,
)


def _unit_normalize(vector: List[float]) -> List[float]:

    norm = math.sqrt(sum(float(value) ** 2 for value in vector)) or 1.0

    return [float(value) / norm for value in vector]


def _fix_dim(vector: List[float], dim: int = VECTOR_DIM) -> List[float]:

    values = [float(value) for value in vector]

    if len(values) > dim:

        values = values[:dim]

    elif len(values) < dim:

        values.extend([0.0] * (dim - len(values)))

    return _unit_normalize(values)


def _effective_provider() -> str:

    if EMBEDDING_PROVIDER == "auto":

        return "gemini" if GEMINI_API_KEY else "local"

    return EMBEDDING_PROVIDER


def embedding_provider_name() -> str:

    return _effective_provider()


@lru_cache(maxsize=1)
def _gemini_client() -> genai.Client:

    if not GEMINI_API_KEY:

        raise RuntimeError("GEMINI_API_KEY is required for Gemini embeddings")

    return genai.Client(api_key=GEMINI_API_KEY)


def _embed_gemini(texts: List[str], task_type: str) -> List[List[float]]:

    output: List[List[float]] = []

    batch_size = max(1, min(100, EMBEDDING_BATCH_SIZE))

    for start in range(0, len(texts), batch_size):

        batch = texts[start : start + batch_size]

        response = _gemini_client().models.embed_content(
            model=GEMINI_EMBED_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=VECTOR_DIM,
            ),
        )

        embeddings = response.embeddings or []

        if len(embeddings) != len(batch):

            raise RuntimeError(
                f"Gemini returned {len(embeddings)} embeddings for {len(batch)} inputs"
            )

        output.extend(_fix_dim(item.values or []) for item in embeddings)

        if start + batch_size < len(texts) and EMBEDDING_BATCH_DELAY_SECONDS > 0:

            time.sleep(EMBEDDING_BATCH_DELAY_SECONDS)

    return output


def _embed_local(texts: List[str]) -> List[List[float]]:
    """Dependency-free lexical hashing fallback for offline development."""

    output: List[List[float]] = []

    for text in texts:

        vector = [0.0] * VECTOR_DIM

        tokens = re.findall(r"[\w+#.-]{2,}", text.lower(), flags=re.UNICODE)

        for token in tokens:

            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()

            index = int.from_bytes(digest, "big") % VECTOR_DIM

            vector[index] += 1.0

        output.append(_unit_normalize(vector))

    return output


def embed_text(
    chunks: List[str],
    model: str | None = None,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> List[List[float]]:
    """Embed documents using Gemini or the configured local fallback."""

    del model

    texts = [str(chunk or "") for chunk in chunks]

    if not texts:

        return []

    provider = _effective_provider()

    if provider == "gemini":

        return _embed_gemini(texts, task_type)

    if provider == "local":

        return _embed_local(texts)

    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


@lru_cache(maxsize=512)
def _cached_query_embedding(normalized_query: str) -> tuple[float, ...]:

    return tuple(embed_text([normalized_query], task_type="RETRIEVAL_QUERY")[0])


def embed_query(query: str) -> List[float]:
    """Embed a query with a bounded in-process cache for repeated searches."""

    normalized = " ".join((query or "").strip().split())

    if not normalized:

        raise ValueError("query must not be empty")

    return list(_cached_query_embedding(normalized))
