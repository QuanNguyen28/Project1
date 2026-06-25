SET search_path TO :"schema", public;

CREATE TABLE IF NOT EXISTS jd_chunks (
  chunk_id        VARCHAR(64) PRIMARY KEY,
  jd_id           INTEGER NOT NULL REFERENCES job_descriptions(jd_id) ON DELETE CASCADE,
  chunk_index     INTEGER NOT NULL,
  heading         TEXT,
  content         TEXT NOT NULL,
  content_hash    VARCHAR(64) NOT NULL,
  object_path     TEXT,
  char_count      INTEGER NOT NULL,
  token_estimate  INTEGER NOT NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (jd_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_jd_chunks_jd_id ON jd_chunks(jd_id);
CREATE INDEX IF NOT EXISTS idx_jd_chunks_fts ON jd_chunks USING GIN (
  to_tsvector('simple', COALESCE(heading, '') || ' ' || content)
);

CREATE TABLE IF NOT EXISTS rag_index_metadata (
  index_name      VARCHAR(100) PRIMARY KEY,
  collection_name VARCHAR(100) NOT NULL,
  embedding_provider VARCHAR(30) NOT NULL,
  embedding_model TEXT NOT NULL,
  vector_dim      INTEGER NOT NULL,
  chunker_version VARCHAR(30) NOT NULL,
  document_count INTEGER NOT NULL,
  chunk_count     INTEGER NOT NULL,
  indexed_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
