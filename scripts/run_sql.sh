#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}/common.sh"
source "${DIR}/_db_env.sh"


# PGPASSWORD should be exported to the environment
export PGPASSWORD="${POSTGRES_USER_PASS}"
_info "running base sql"
psql -U postgres -h "${HOST}" \
-f "${DIR}/sql/000_drop_everything.sql" -v ON_ERROR_STOP=1
psql -U postgres -h "${HOST}" \
-f "${DIR}/sql/001_init_database.sql" -v ON_ERROR_STOP=1

# Update password to correspond with the new user
export PGPASSWORD="${PASSWORD}"
_info "running additional sql"
run_sql "002_create_tables.sql"

_info "inserting base data"
run_sql "003_insert_base_data.sql"

if [ -z "${TEST}" ]; then
  _info "production env, do nothing"
else
  _info "inserting test data"
  run_sql "004_insert_test_data.sql"
fi

_warn "running migrations"
source "${DIR}/migrate.sh"

_note "done!"
