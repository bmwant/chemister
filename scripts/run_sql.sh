#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}/common.sh"


# Fallback to local values when not defined
HOST=${PG_HOST:="local-postgres"}
DBNAME=${PG_DATABASE:="chemister"}
USER=${PG_USER:="che"}
PASSWORD=${PG_PASSWORD:="guevara"}
POSTGRES_USER_PASS=${POSTGRES_USER_PASS:="postgres"}
if [ -z ${TEST+x} ]; then
 TEST=true
fi

# PGPASSWORD should be exported to the environment
export PGPASSWORD="${POSTGRES_USER_PASS}"
_info "|| running base sql"
psql -U postgres -h "${HOST}" -f "${DIR}/sql/000_drop_everything.sql"
psql -U postgres -h "${HOST}" -f "${DIR}/sql/001_init_database.sql"

# Update password to correspond with the new user
export PGPASSWORD="${PASSWORD}"
info "|| running additional sql"

psql -U "${USER}" -h "${HOST}" -d "${DBNAME}" -f "${DIR}/sql/002_create_tables.sql"


if [ -z "${TEST}" ]; then
  _info "|| production env, do nothing"
else
  _info "|| inserting test data"
  psql -U "${USER}" -h "${HOST}" -d "${DBNAME}" -f "${DIR}/sql/003_insert_base_data.sql"
fi

_note "|| done!"
