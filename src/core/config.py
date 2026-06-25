from dotenv import load_dotenv

import os

from urllib.parse import quote_plus

load_dotenv()

ALGORITHM = "HS256"

DB_HOST = os.getenv("DB_HOST")

DB_PORT = int(os.getenv("DB_PORT", "5432"))

DB_NAME = os.getenv("DB_NAME", "hcm")

DB_USER = os.getenv("DB_USER")

DB_PASS = os.getenv("DB_PASS")

DB_SCHEMA = os.getenv("DB_SCHEMA", "smarthire")

DATABASE_URL = (
    f"postgresql://{quote_plus(DB_USER or '')}:{quote_plus(DB_PASS or '')}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash-lite")

GEMINI_FALLBACK_CHAT_MODELS = [
    item.strip()
    for item in os.getenv("GEMINI_FALLBACK_CHAT_MODELS", "").split(",")
    if item.strip()
]

GEMINI_LLM_MAX_RETRIES = int(os.getenv("GEMINI_LLM_MAX_RETRIES", "3"))

GEMINI_LLM_RETRY_BASE_SECONDS = float(
    os.getenv("GEMINI_LLM_RETRY_BASE_SECONDS", "1.25")
)

GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "lexical-hashing")

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "auto").strip().lower()

EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "90"))

EMBEDDING_BATCH_DELAY_SECONDS = float(os.getenv("EMBEDDING_BATCH_DELAY_SECONDS", "65"))

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")

MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))

MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "jdchunks")

VECTOR_DIM = int(os.getenv("VECTOR_DIM", "768"))

CHUNKER_VERSION = os.getenv("CHUNKER_VERSION", "markdown-char-v2")

RAG_DENSE_CANDIDATES = int(os.getenv("RAG_DENSE_CANDIDATES", "40"))

RAG_LEXICAL_CANDIDATES = int(os.getenv("RAG_LEXICAL_CANDIDATES", "40"))

RAG_RRF_K = int(os.getenv("RAG_RRF_K", "60"))

RAG_MAX_CHUNKS_PER_JD = int(os.getenv("RAG_MAX_CHUNKS_PER_JD", "2"))

CHUNK_LOCAL_DIR = os.getenv("CHUNK_LOCAL_DIR", "data/chunks")

CORS_ORIGINS = [
    item.strip()
    for item in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if item.strip()
]
