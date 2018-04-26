#!/usr/bin/env bash
set -e

if [ $# -ne 4 ]; then
  echo "Usage: $0 <server> <user> <password> <sql_file>"
  exit 1
fi;

server=$1; shift
user=$1; shift
password=$1; shift
file=$1; shift
dbname="kpidata"

export PGPASSWORD=$password

echo -e "::running sql file $file on $dbname"
psql --username $user --host $server --file $file --dbname $dbname

echo "::running additional sql"
for file in $files; do
  echo -e "\n--- $file"
  psql --username $user --host $server --file $file --dbname $dbname
done;
