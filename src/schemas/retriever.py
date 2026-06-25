# src/schemas/retriever.py
from __future__ import annotations
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(5, ge=1, le=100)
    with_snippet: bool = False

class ChunkHit(BaseModel):
    chunk_id: str
    jd_id: Optional[int] = None
    chunk_index: Optional[int] = None
    object_path: str
    score: float
    snippet: Optional[str] = None

class RetrieveResponse(BaseModel):
    items: List[ChunkHit]


class RetrieveSimilarReq(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    top_k: int = Field(5, ge=1, le=50)
    company: Optional[str] = None
    department: Optional[str] = None
    max_chunks_per_jd: int = Field(2, ge=1, le=5)

class RetrieveReq(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    top_k: int = Field(5, ge=1, le=50)
    mode: Literal["hybrid", "dense", "lexical"] = "hybrid"
    company: Optional[str] = None
    department: Optional[str] = None
    max_chunks_per_jd: int = Field(2, ge=1, le=5)
    snippet_chars: int = Field(700, ge=100, le=3000)

class ChunkResult(BaseModel):
    chunk_id: str
    jd_id: int
    chunk_index: int
    score: float
    object_path: Optional[str] = None
    snippet: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    source_url: Optional[str] = None
    heading: Optional[str] = None
    dense_score: Optional[float] = None
    lexical_score: Optional[float] = None
    retrieval_method: str = "dense"
