#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

HOST=${PG_HOST:="local-postgres"}
DBNAME=${PG_DATABSE:="chemister"}
USER=${PG_USER:="che"}
PASSWORD=${PG_PASSWORD:="guevara"}
TEST=${TEST:=true}

echo "::running base sql"
psql -U postgres -h "${HOST}" -f "${DIR}/sql/000_drop_everything.sql"
psql -U postgres -h "${HOST}" -f "${DIR}/sql/001_init_database.sql"

# PGPASSWORD should be exported to the environment
export PGPASSWORD="${PASSWORD}"
echo "::running additional sql"

psql -U "${USER}" -h "${HOST}" -d "${DBNAME}" -f "${DIR}/sql/002_create_tables.sql"


if [ -z "${TEST}" ]; then
  echo "::production env, do nothing"
else
  echo "::inserting test data"
  psql -U "${USER}" -h "${HOST}" -d "${DBNAME}" -f "${DIR}/sql/003_insert_base_data.sql"
fi
