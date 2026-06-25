SET search_path TO :"schema", public;

ALTER TABLE job_descriptions
  ADD COLUMN IF NOT EXISTS source_name VARCHAR(30),
  ADD COLUMN IF NOT EXISTS source_url TEXT,
  ADD COLUMN IF NOT EXISTS source_external_id VARCHAR(255),
  ADD COLUMN IF NOT EXISTS source_company TEXT,
  ADD COLUMN IF NOT EXISTS source_published_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS source_fetched_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS source_hash VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS uq_job_desc_source
  ON job_descriptions(source_name, source_external_id)
  WHERE source_name IS NOT NULL AND source_external_id IS NOT NULL;
