#!/bin/bash
# Same as autom_check.sh at n = 11 for the 8 hardest patterns (about 90 s each).
cd "$(dirname "$0")"
for t in $(cat ../data/unsep13.txt); do
  a=$(./autom $t 11 11 11 11 11 11 11 11 11 11 11 | tail -1)
  c=$(grep "^$t " ../data/unsep12_K5.txt | head -1 | sed 's/.*| //' | awk '{print $4}')
  echo "$t autom_Av11=$a cluster_Av11=$c $([ "$a" = "$c" ] && echo OK || echo MISMATCH)"
done
