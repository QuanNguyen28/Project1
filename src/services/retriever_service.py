from __future__ import annotations

import re

from dataclasses import dataclass

from functools import lru_cache

from typing import Dict, Iterable, List, Optional

from pymilvus import Collection, connections

from sqlalchemy import func, text

from embeddings.utils.gemini_embed import embedding_provider_name

from src.core.config import (
    EMBEDDING_MODEL,
    GEMINI_EMBED_MODEL,
    MILVUS_COLLECTION,
    MILVUS_HOST,
    MILVUS_PORT,
    RAG_DENSE_CANDIDATES,
    RAG_LEXICAL_CANDIDATES,
    RAG_MAX_CHUNKS_PER_JD,
    RAG_RRF_K,
    VECTOR_DIM,
)

from src.db.models import JDChunk, JobDescription, RAGIndexMetadata

from src.db.session import SessionLocal

from src.schemas.retriever import ChunkResult, RetrieveReq, RetrieveSimilarReq

__all__ = [
    "RetrieveSimilarReq",
    "RetrieveReq",
    "ChunkResult",
    "retrieve_dense",
    "retrieve_hybrid",
]


@dataclass
class _Candidate:

    chunk_id: str

    jd_id: int

    chunk_index: int

    content: str = ""

    object_path: Optional[str] = None

    heading: Optional[str] = None

    title: Optional[str] = None

    company: Optional[str] = None

    source_url: Optional[str] = None

    dense_score: Optional[float] = None

    lexical_score: Optional[float] = None

    fused_score: float = 0.0


@lru_cache(maxsize=1)
def _collection() -> Collection:

    connections.connect(alias="default", host=MILVUS_HOST, port=str(MILVUS_PORT))

    collection = Collection(MILVUS_COLLECTION)

    collection.load()

    return collection


def clear_collection_cache() -> None:

    _collection.cache_clear()


def _safe_get(hit, key: str):

    try:

        entity = getattr(hit, "entity", None)

        return entity.get(key) if entity is not None else None

    except Exception:

        return None


def _validate_manifest() -> None:

    db = SessionLocal()

    try:

        manifest = db.get(RAGIndexMetadata, MILVUS_COLLECTION)

        if manifest is None:

            raise RuntimeError(
                "RAG index manifest is missing; run the indexing command"
            )

        provider = embedding_provider_name()

        model = GEMINI_EMBED_MODEL if provider == "gemini" else EMBEDDING_MODEL

        if (
            manifest.embedding_provider != provider
            or manifest.embedding_model != model
            or manifest.vector_dim != VECTOR_DIM
        ):

            raise RuntimeError(
                "Embedding configuration differs from the active index; reindex before querying"
            )

    finally:

        db.close()


def _eligible_jd_ids(
    company: Optional[str], department: Optional[str]
) -> Optional[List[int]]:

    if not company and not department:

        return None

    db = SessionLocal()

    try:

        query = db.query(JobDescription.jd_id)

        if company:

            query = query.filter(
                func.lower(JobDescription.source_company) == company.strip().lower()
            )

        if department:

            query = query.filter(
                JobDescription.department.ilike(f"%{department.strip()}%")
            )

        return [row[0] for row in query.all()]

    finally:

        db.close()


def _dense_candidates(
    query_vec: List[float],
    limit: int,
    company: Optional[str] = None,
    department: Optional[str] = None,
) -> List[_Candidate]:

    _validate_manifest()

    eligible = _eligible_jd_ids(company, department)

    if eligible == []:

        return []

    expression = None

    if eligible is not None:

        expression = f"jd_id in [{','.join(str(value) for value in eligible)}]"

    kwargs = {
        "data": [query_vec],
        "anns_field": "embedding",
        "param": {"metric_type": "COSINE", "params": {"ef": max(128, limit * 4)}},
        "limit": limit,
        "output_fields": ["chunk_id", "jd_id", "chunk_index", "object_url"],
    }

    if expression:

        kwargs["expr"] = expression

    hits = _collection().search(**kwargs)[0]

    return [
        _Candidate(
            chunk_id=str(_safe_get(hit, "chunk_id") or hit.id),
            jd_id=int(_safe_get(hit, "jd_id") or 0),
            chunk_index=int(_safe_get(hit, "chunk_index") or 0),
            object_path=_safe_get(hit, "object_url"),
            dense_score=float(hit.score),
        )
        for hit in hits
    ]


def _lexical_candidates(
    query: str,
    limit: int,
    company: Optional[str] = None,
    department: Optional[str] = None,
) -> List[_Candidate]:

    lexical_query = re.sub(r"[-–—]+", " ", query)

    statement = text("""
        WITH q AS (SELECT websearch_to_tsquery('simple', :query) AS query)
        SELECT c.chunk_id, c.jd_id, c.chunk_index, c.heading, c.content,
               c.object_path, j.title, j.source_company, j.source_url,
               ts_rank_cd(
                   setweight(to_tsvector('simple', COALESCE(j.title, '')), 'A') ||
                   setweight(to_tsvector('simple', COALESCE(c.heading, '') || ' ' || c.content), 'B'),
                   q.query,
                   32
               ) AS lexical_score
        FROM jd_chunks c
        JOIN job_descriptions j ON j.jd_id = c.jd_id
        CROSS JOIN q
        WHERE (
            setweight(to_tsvector('simple', COALESCE(j.title, '')), 'A') ||
            setweight(to_tsvector('simple', COALESCE(c.heading, '') || ' ' || c.content), 'B')
        ) @@ q.query
          AND (:company IS NULL OR lower(j.source_company) = lower(:company))
          AND (:department IS NULL OR j.department ILIKE '%' || :department || '%')
        ORDER BY lexical_score DESC, c.chunk_id
        LIMIT :limit
    """)

    db = SessionLocal()

    try:

        rows = (
            db.execute(
                statement,
                {
                    "query": lexical_query,
                    "company": company,
                    "department": department,
                    "limit": limit,
                },
            )
            .mappings()
            .all()
        )

        return [
            _Candidate(
                chunk_id=row["chunk_id"],
                jd_id=row["jd_id"],
                chunk_index=row["chunk_index"],
                heading=row["heading"],
                content=row["content"],
                object_path=row["object_path"],
                title=row["title"],
                company=row["source_company"],
                source_url=row["source_url"],
                lexical_score=float(row["lexical_score"]),
            )
            for row in rows
        ]

    finally:

        db.close()


def _hydrate(candidates: Iterable[_Candidate]) -> List[_Candidate]:

    items = list(candidates)

    ids = {item.chunk_id for item in items}

    if not ids:

        return items

    db = SessionLocal()

    try:

        rows = (
            db.query(JDChunk, JobDescription)
            .join(JobDescription, JobDescription.jd_id == JDChunk.jd_id)
            .filter(JDChunk.chunk_id.in_(ids))
            .all()
        )

        metadata = {chunk.chunk_id: (chunk, jd) for chunk, jd in rows}

        for item in items:

            pair = metadata.get(item.chunk_id)

            if pair:

                chunk, jd = pair

                item.content = chunk.content

                item.heading = chunk.heading

                item.object_path = chunk.object_path

                item.title = jd.title

                item.company = jd.source_company

                item.source_url = jd.source_url

        return items

    finally:

        db.close()


def _tokens(value: str) -> set[str]:

    return set(re.findall(r"[\w+#.-]{2,}", value.lower(), flags=re.UNICODE))


def _jaccard(left: str, right: str) -> float:

    a, b = _tokens(left), _tokens(right)

    return len(a & b) / len(a | b) if a and b else 0.0


def _select_diverse(
    candidates: List[_Candidate], top_k: int, max_chunks_per_jd: int
) -> List[_Candidate]:

    remaining = list(candidates)

    selected: List[_Candidate] = []

    counts: Dict[int, int] = {}

    while remaining and len(selected) < top_k:

        allowed = [
            item for item in remaining if counts.get(item.jd_id, 0) < max_chunks_per_jd
        ]

        if not allowed:

            break

        best = max(
            allowed,
            key=lambda item: item.fused_score
            - 0.08
            * max(
                (_jaccard(item.content, prev.content) for prev in selected), default=0.0
            ),
        )

        selected.append(best)

        counts[best.jd_id] = counts.get(best.jd_id, 0) + 1

        remaining.remove(best)

    return selected


def _to_results(
    candidates: List[_Candidate], method: str, snippet_chars: int = 700
) -> List[ChunkResult]:

    return [
        ChunkResult(
            chunk_id=item.chunk_id,
            jd_id=item.jd_id,
            chunk_index=item.chunk_index,
            object_path=item.object_path,
            score=float(item.fused_score),
            snippet=item.content[:snippet_chars] if item.content else None,
            title=item.title,
            company=item.company,
            source_url=item.source_url,
            heading=item.heading,
            dense_score=item.dense_score,
            lexical_score=item.lexical_score,
            retrieval_method=method,
        )
        for item in candidates
    ]


def retrieve_dense(
    query_vec: List[float],
    top_k: int,
    *,
    company: Optional[str] = None,
    department: Optional[str] = None,
    max_chunks_per_jd: int = RAG_MAX_CHUNKS_PER_JD,
    snippet_chars: int = 700,
) -> List[ChunkResult]:

    candidates = _hydrate(
        _dense_candidates(
            query_vec,
            max(top_k * 4, RAG_DENSE_CANDIDATES),
            company,
            department,
        )
    )

    for candidate in candidates:

        candidate.fused_score = candidate.dense_score or 0.0

    selected = _select_diverse(candidates, top_k, max_chunks_per_jd)

    return _to_results(selected, "dense", snippet_chars)


def retrieve_hybrid(
    query: str,
    query_vec: Optional[List[float]],
    top_k: int,
    *,
    mode: str = "hybrid",
    company: Optional[str] = None,
    department: Optional[str] = None,
    max_chunks_per_jd: int = RAG_MAX_CHUNKS_PER_JD,
    snippet_chars: int = 700,
) -> List[ChunkResult]:

    dense = (
        []
        if mode == "lexical"
        else _dense_candidates(
            query_vec or [], max(top_k * 4, RAG_DENSE_CANDIDATES), company, department
        )
    )

    lexical = (
        []
        if mode == "dense"
        else _lexical_candidates(
            query, max(top_k * 4, RAG_LEXICAL_CANDIDATES), company, department
        )
    )

    merged: Dict[str, _Candidate] = {}

    for rank, item in enumerate(dense, 1):

        target = merged.setdefault(item.chunk_id, item)

        target.dense_score = item.dense_score

        target.fused_score += 1.0 / (RAG_RRF_K + rank)

    for rank, item in enumerate(lexical, 1):

        target = merged.setdefault(item.chunk_id, item)

        target.lexical_score = item.lexical_score

        target.fused_score += 1.0 / (RAG_RRF_K + rank)

    candidates = _hydrate(merged.values())

    if mode == "dense":

        for item in candidates:

            item.fused_score = item.dense_score or 0.0

    elif mode == "lexical":

        maximum = (
            max((item.lexical_score or 0.0 for item in candidates), default=1.0) or 1.0
        )

        for item in candidates:

            item.fused_score = (item.lexical_score or 0.0) / maximum

    else:

        theoretical_max = 2.0 / (RAG_RRF_K + 1)

        for item in candidates:

            item.fused_score /= theoretical_max

    candidates.sort(key=lambda item: item.fused_score, reverse=True)

    selected = _select_diverse(candidates, top_k, max_chunks_per_jd)

    return _to_results(selected, mode, snippet_chars)
