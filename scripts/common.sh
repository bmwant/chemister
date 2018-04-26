#!/usr/bin/env bash
set -e


function _note {
  echo -e "\033[0;32m========================"
  echo $1
  echo -e "========================\033[0m"
}

function _info {
  echo -e "\033[0;33m========================"
  echo $1
  echo -e "========================\033[0m"
}

function _warn {
  echo -e "\033[0;31m========================"
  echo $1
  echo -e "========================\033[0m"
}
