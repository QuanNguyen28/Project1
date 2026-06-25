from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pymilvus import Collection, connections, utility
from sqlalchemy import text

from src.core.config import MILVUS_COLLECTION, MILVUS_HOST, MILVUS_PORT
from src.db.session import engine
from src.db.session import SessionLocal
from src.db.models import JDChunk, RAGIndexMetadata

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def live():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    checks = {"postgres": False, "milvus": False, "index": False}
    errors = {}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["postgres"] = True
    except Exception as exc:
        errors["postgres"] = type(exc).__name__

    try:
        connections.connect(alias="health", host=MILVUS_HOST, port=str(MILVUS_PORT))
        checks["milvus"] = True
        checks["index"] = utility.has_collection(MILVUS_COLLECTION, using="health")
        if checks["index"]:
            collection = Collection(MILVUS_COLLECTION, using="health")
            collection.load()
            db = SessionLocal()
            try:
                manifest = db.get(RAGIndexMetadata, MILVUS_COLLECTION)
                catalog_count = db.query(JDChunk).count()
                checks["index"] = bool(
                    manifest
                    and manifest.chunk_count == catalog_count
                    and collection.num_entities == catalog_count
                )
            finally:
                db.close()
    except Exception as exc:
        errors["milvus"] = type(exc).__name__
    finally:
        try:
            connections.disconnect("health")
        except Exception:
            pass

    payload = {"status": "ready" if all(checks.values()) else "not_ready", "checks": checks}
    if errors:
        payload["errors"] = errors
    if not all(checks.values()):
        raise HTTPException(status_code=503, detail=payload)
    return payload
