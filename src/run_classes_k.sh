#!/bin/bash
# usage: run_classes_k.sh k a outfile  -- runs classes_k for every pattern of length a
k=$1; a=$2; out=$3
python3 -c "
import itertools
for t in itertools.permutations(range(1,$a+1)): print(''.join(map(str,t)))" | while read t; do ./classes_k $k $t; done > $out
