#!/usr/bin/env bash
# Recompute actual values, retain each raw output, and fail on any mismatch.
# JOBS defaults to 1. At n=14 each worker needs approximately 0.78 GB.
# Optional arguments (e.g. --output PATH or --resume) are passed to the runner.
set -euo pipefail
cd "$(dirname "$0")"
: "${CXX:=g++}"
"$CXX" -O3 -std=c++17 -o bruteforce_contain bruteforce_contain.cpp
exec python3 recount_containment.py --scope all --n 11 12 \
  --jobs "${JOBS:-1}" --output ../checks/bruteforce_all_n12.csv "$@"
