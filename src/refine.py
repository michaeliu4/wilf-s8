#!/usr/bin/env python3
"""Refinement numbers from a cluster-number sweep.
Usage: refine.py sweepfile [sweepfile2 ...]
Each line of a sweep file: tau c_a ... c_{a+K} | Av_a ... Av_{a+K}  (output of run_reps.py).
Later files override earlier ones for the same tau (use them for deeper runs on subsets).
Prints, for every n, the number W(n) of groups of representatives with identical (c_a..c_n) — i.e. identical
|Av_t| for t <= n — and finally the groups still unseparated at the largest common depth."""
import sys
from collections import defaultdict
cs={}
for fn in sys.argv[1:]:
    for line in open(fn):
        p=line.split()
        if not p or '|' not in p: continue
        cs[p[0]]=[int(x) for x in p[1:p.index('|')]]
a=len(next(iter(cs)))
depth=min(len(v) for v in cs.values())
print(f"{len(cs)} representatives of length {a}; common depth n <= {a+depth-1}")
for d in range(1,depth+1):
    g=defaultdict(list)
    for t,v in cs.items(): g[tuple(v[:d])].append(t)
    print(f"n<={a+d-1}: W={len(g)}")
uns=[grp for grp in g.values() if len(grp)>1]
print(f"unseparated groups at n<={a+depth-1}: {len(uns)} groups, {sum(len(x) for x in uns)} representatives")
for grp in uns: print("  ",' '.join(grp))
