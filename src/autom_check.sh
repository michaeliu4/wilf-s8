#!/bin/bash
# Cross-check of the cluster counter against the stage-15 automaton counter (autom.cpp) at n = 10 for the patterns listed
# in data/unsep13.txt (the hardest ones) and a few others; prints both values.  Usage: autom_check.sh
cd "$(dirname "$0")"
for t in $(cat ../data/unsep13.txt) 12345678 12436758 23157846 25876413; do
  a=$(./autom $t 10 10 10 10 10 10 10 10 10 10 | tail -1)
  c=$(grep "^$t " ../data/reps8_K4.txt ../data/unsep12_K5.txt | head -1 | sed 's/.*| //' | awk '{print $3}')
  echo "$t autom_Av10=$a cluster_Av10=$c $([ "$a" = "$c" ] && echo OK || echo MISMATCH)"
done
