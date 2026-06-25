#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-$ROOT/.venv/Scripts/python.exe}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
fi

docker compose up -d
until docker exec pg_jd_demo pg_isready -U jd_user -d jd_library >/dev/null 2>&1; do
  sleep 2
done

{
  for file in infra/migrations/{000,010,020,030,040,050,060,070,080,090,100,110,120,900,999}_*.sql; do
    cat "$file"
    printf '\n'
  done
} | docker exec -i pg_jd_demo psql -v ON_ERROR_STOP=1 -v schema=smarthire -U jd_user -d jd_library

"$PYTHON" scripts/seed_users.py

if [[ "${RUN_ETL:-0}" == "1" ]]; then
  "$PYTHON" etl/jd_etl.py --dir "${JD_ETL_DIR:-data/real_jd}"
fi
if [[ "${RUN_INDEX:-0}" == "1" ]]; then
  "$PYTHON" embeddings/jd_chunk_embed.py
fi

"$PYTHON" -m uvicorn src.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
(cd frontend && npm ci && npm run dev -- --host 0.0.0.0) &
FRONTEND_PID=$!

trap 'kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true' EXIT INT TERM
wait -n "$BACKEND_PID" "$FRONTEND_PID"
