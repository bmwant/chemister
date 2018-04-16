#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

HOST="local-postgres"
DBNAME="chemister"
USER="che"
PASSWORD="guevara"

echo "::running base sql"
psql -U postgres -h "${HOST}" -f "${DIR}/sql/000_drop_everything.sql"
psql -U postgres -h "${HOST}" -f "${DIR}/sql/001_init_database.sql"

# PGPASSWORD should be exported to the environment
export PGPASSWORD="${PASSWORD}"
echo "::running additional sql"

psql -U "${USER}" -h "${HOST}" -d "${DBNAME}" -f "${DIR}/sql/002_create_tables.sql"

# todo: fail on errors
