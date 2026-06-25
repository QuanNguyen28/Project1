#!/usr/bin/env bash
set -euo pipefail

: "${DB_HOST:?set DB_HOST}"
: "${DB_PORT:=5432}"
: "${DB_NAME:?set DB_NAME}"
: "${DB_USER:?set DB_USER}"
: "${PGPASSWORD:?set PGPASSWORD}"
: "${DB_SCHEMA:=public}"

MIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

readarray -t SQL_FILES < <(ls -1 "$MIG_DIR"/*.sql | sort)

TMP_SQL="$(mktemp)"
{
  echo "\\set schema ${DB_SCHEMA}"
  echo "CREATE SCHEMA IF NOT EXISTS :\"schema\";"
  echo "SET search_path TO :\"schema\", public;"
  echo "\\cd '${MIG_DIR}'"
  for f in "${SQL_FILES[@]}"; do
    b="$(basename "$f")"
    echo "\\i '${b}'"
  done
} > "$TMP_SQL"

echo "==> Running migrations on $DB_HOST:$DB_PORT/$DB_NAME as $DB_USER (schema=$DB_SCHEMA)"
psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER sslmode=prefer" \
     -v ON_ERROR_STOP=1 \
     -f "$TMP_SQL"

rm -f "$TMP_SQL"
echo "==> All done."
