#!/usr/bin/env bash
set -e
#********************************************************************
# Setup environment variables to reuse in scripts that use database
#********************************************************************


# Fallback to local values when not defined
export HOST=${PG_HOST:="local-postgres"}
export DBNAME=${PG_DATABASE:="chemister"}
export USER=${PG_USER:="che"}
export PASSWORD=${PG_PASSWORD:="guevara"}
export POSTGRES_USER=${POSTGRES_USER:="postgres"}
export POSTGRES_USER_PASS=${POSTGRES_USER_PASS:="postgres"}
if [ -z ${TEST+x} ]; then
 export TEST=true
fi
