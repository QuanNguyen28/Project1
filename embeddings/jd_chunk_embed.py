from __future__ import annotations

import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import Collection
from sqlalchemy.orm import Session

from embeddings.chunk_utils import embed_chunks, prepare_chunk_metadata, prepare_chunk_records
from embeddings.schema import COLLECTION_NAME, FIELD_JD_ID, connect, ensure_collection
from embeddings.utils.gemini_embed import embedding_provider_name
from src.core.config import (
    CHUNKER_VERSION,
    EMBEDDING_MODEL,
    GEMINI_EMBED_MODEL,
    MILVUS_COLLECTION,
    VECTOR_DIM,
)
from src.db.models import JDChunk, JobDescription, RAGIndexMetadata
from src.db.session import SessionLocal


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _delete_existing_jd(collection: Collection, jd_id: int) -> None:
    collection.delete(expr=f"{FIELD_JD_ID} == {int(jd_id)}")


def _extract_heading(text: str) -> str | None:
    match = re.search(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip()[:500] if match else None


def _sync_catalog(
    db: Session,
    chunk_ids: List[str],
    jd_ids: List[int],
    indexes: List[int],
    paths: List[str],
    texts: List[str],
    document_count: int,
) -> None:
    now = _utcnow()
    db.query(JDChunk).delete(synchronize_session=False)
    db.add_all([
        JDChunk(
            chunk_id=chunk_id,
            jd_id=jd_id,
            chunk_index=index,
            heading=_extract_heading(text),
            content=text,
            content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            object_path=path,
            char_count=len(text),
            token_estimate=max(1, (len(text) + 3) // 4),
            created_at=now,
            updated_at=now,
        )
        for chunk_id, jd_id, index, path, text in zip(
            chunk_ids, jd_ids, indexes, paths, texts
        )
    ])
    provider = embedding_provider_name()
    model = GEMINI_EMBED_MODEL if provider == "gemini" else EMBEDDING_MODEL
    manifest = db.get(RAGIndexMetadata, MILVUS_COLLECTION)
    if manifest is None:
        manifest = RAGIndexMetadata(index_name=MILVUS_COLLECTION)
        db.add(manifest)
    manifest.collection_name = MILVUS_COLLECTION
    manifest.embedding_provider = provider
    manifest.embedding_model = model
    manifest.vector_dim = VECTOR_DIM
    manifest.chunker_version = CHUNKER_VERSION
    manifest.document_count = document_count
    manifest.chunk_count = len(chunk_ids)
    manifest.indexed_at = now
    db.commit()


def _collect_metadata(db: Session, *, save_to_local: bool):
    rows = db.query(JobDescription.jd_id, JobDescription.content_md).all()
    all_chunk_ids: List[str] = []
    all_jd_ids: List[int] = []
    all_indexes: List[int] = []
    all_paths: List[str] = []
    all_texts: List[str] = []
    for jd_id, markdown in rows:
        if not markdown or not markdown.strip():
            continue
        ids, jd_ids, indexes, paths, texts = prepare_chunk_metadata(
            jd_id, markdown, save_to_local=save_to_local
        )
        all_chunk_ids.extend(ids)
        all_jd_ids.extend(jd_ids)
        all_indexes.extend(indexes)
        all_paths.extend(paths)
        all_texts.extend(texts)
    return rows, all_chunk_ids, all_jd_ids, all_indexes, all_paths, all_texts


def sync_chunk_catalog(*, save_to_local: bool = True) -> int:
    db = SessionLocal()
    try:
        rows, ids, jd_ids, indexes, paths, texts = _collect_metadata(
            db, save_to_local=save_to_local
        )
        _sync_catalog(db, ids, jd_ids, indexes, paths, texts, len(rows))
        return len(ids)
    finally:
        db.close()


def reindex_jd(jd_id: int, *, save_to_local: bool = True) -> int:
    connect()
    collection = ensure_collection()
    db = SessionLocal()
    try:
        row = db.get(JobDescription, jd_id)
        if not row or not row.content_md.strip():
            return 0
        ids, jd_ids, indexes, paths, vectors = prepare_chunk_records(
            jd_id=row.jd_id, md=row.content_md, save_to_local=save_to_local
        )
        _delete_existing_jd(collection, jd_id)
        if ids:
            collection.insert([ids, jd_ids, indexes, paths, vectors])
        collection.flush()
        collection.load()
        # Keep the hybrid catalog consistent; the corpus is small enough that
        # a full metadata refresh is safer than bespoke stale-row handling.
        sync_chunk_catalog(save_to_local=save_to_local)
        return len(ids)
    finally:
        db.close()


def reindex_all(*, save_to_local: bool = True) -> int:
    connect()
    collection = ensure_collection()
    db = SessionLocal()
    try:
        rows, ids, jd_ids, indexes, paths, texts = _collect_metadata(
            db, save_to_local=save_to_local
        )

        # Embed before mutating either store, avoiding a partial rebuild when
        # an external embedding provider is unavailable.
        vectors = embed_chunks(texts)
        for jd_id, _ in rows:
            _delete_existing_jd(collection, jd_id)
        if ids:
            collection.insert([ids, jd_ids, indexes, paths, vectors])
        collection.flush()
        try:
            collection.compact(timeout=120)
            collection.wait_for_compaction_completed(timeout=120)
        except Exception:
            pass
        collection.load()
        _sync_catalog(db, ids, jd_ids, indexes, paths, texts, len(rows))
        print(f"[Milvus] Inserted {len(ids)} chunks into '{COLLECTION_NAME}'")
        return len(ids)
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index JD content for dense and hybrid retrieval")
    parser.add_argument("--only", type=int, help="Reindex only this jd_id")
    parser.add_argument("--no-save", action="store_true", help="Do not write local chunk files")
    parser.add_argument(
        "--catalog-only",
        action="store_true",
        help="Sync PostgreSQL chunk catalog without re-embedding",
    )
    args = parser.parse_args()

    if args.catalog_only:
        total = sync_chunk_catalog(save_to_local=not args.no_save)
        print(f"Synced chunk catalog: {total} chunks")
    elif args.only:
        total = reindex_jd(args.only, save_to_local=not args.no_save)
        print(f"Reindexed JD {args.only}: {total} chunks")
    else:
        total = reindex_all(save_to_local=not args.no_save)
        print(f"Reindexed all: {total} chunks")
