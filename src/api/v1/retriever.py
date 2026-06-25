from fastapi import APIRouter, Depends, HTTPException

from typing import List

from src.api.dependencies import require_roles

from src.services.retriever_service import (
    RetrieveSimilarReq,
    RetrieveReq,
    ChunkResult,
    retrieve_dense,
    retrieve_hybrid,
)

from embeddings.utils.gemini_embed import embed_query

router = APIRouter(prefix="/v1/retrieve", tags=["Retriever"])


@router.post("/similar", response_model=List[ChunkResult])
def retrieve_similar_endpoint(
    req: RetrieveSimilarReq,
    _: str = Depends(require_roles("recruiter", "manager", "admin")),
):

    try:

        qvec = embed_query(req.query)

        return retrieve_dense(
            qvec,
            req.top_k,
            company=req.company,
            department=req.department,
            max_chunks_per_jd=req.max_chunks_per_jd,
        )

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")


@router.post("", response_model=List[ChunkResult])
def retrieve_endpoint(
    req: RetrieveReq, _: str = Depends(require_roles("recruiter", "manager", "admin"))
):

    try:

        effective_mode = req.mode

        qvec = None

        if req.mode != "lexical":

            try:

                qvec = embed_query(req.query)

            except Exception:

                if req.mode == "dense":

                    raise

                effective_mode = "lexical"

        return retrieve_hybrid(
            req.query,
            qvec,
            req.top_k,
            mode=effective_mode,
            company=req.company,
            department=req.department,
            max_chunks_per_jd=req.max_chunks_per_jd,
            snippet_chars=req.snippet_chars,
        )

    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")
