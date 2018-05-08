#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${DIR}/common.sh"
source "${DIR}/_db_env.sh"

# Update password to correspond with the new user
export PGPASSWORD="${PASSWORD}"

_info "applying migrations"
run_sql "005_add_events_table.sql"

_note "migrations has been successfully applied!"
