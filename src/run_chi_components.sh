#!/usr/bin/env bash
# Regenerate each component log in the finite ranges, then verify full coverage.
set -euo pipefail
cd "$(dirname "$0")"
: "${CXX:=g++}"
"$CXX" -O3 -std=c++17 -o chi_components chi_components.cpp
for k in 3 4; do
  amax=6; [ "$k" -eq 4 ] && amax=5
  out="../checks/chi_components_k${k}.txt"
  python3 - "$k" "$amax" "$out" <<'PYRUN'
import itertools,subprocess,sys
k,amax=int(sys.argv[1]),int(sys.argv[2])
with open(sys.argv[3],'w') as out:
    for a in range(2,amax+1):
        for p in itertools.permutations(range(1,a+1)):
            tau=''.join(map(str,p))
            result=subprocess.run(['./chi_components',str(k),tau],capture_output=True,text=True,check=True)
            out.write(result.stdout);out.flush()
PYRUN
done
python3 check_component_records.py
