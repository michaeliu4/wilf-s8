#!/usr/bin/env python3
"""Compare the primitive-return catalogue (return_catalogue.py, the primitive-return catalogue theorem) with the pure-return indicator U
(data/returns_l.txt, computed from the clusters of size l+2), for all words of length 2..7, and check the counts r_l
and the value of j on all patterns of length <= 5 (data/clusters_len*.txt) via the all-pattern formula."""
import os, sys, itertools
here=os.path.dirname(os.path.abspath(__file__)); data=os.path.join(here,'..','data')
sys.path.insert(0,here)
from return_catalogue import primitive_parameters
def P(w): return primitive_parameters(tuple(w)) is not None
all_ok=True
for l in range(2,8):
    U=set(line.split()[0] for line in open(os.path.join(data,f'returns_{l}.txt')) if line.strip())
    Pset=set(''.join(map(str,w)) for w in itertools.permutations(range(1,l+1)) if P(w))
    print(f"l={l}: |P|={len(Pset)} |U|={len(U)} P==U: {Pset==U}")
    all_ok = all_ok and (Pset==U)
def j_formula(p):
    m=len(p); tot=0
    for i in range(m):
        for k in range(i+1,m):
            seg=p[i:k+1]
            if max(seg)-min(seg)==k-i:
                s=sorted(seg); w=tuple(s.index(x)+1 for x in seg)
                tot+=P(w)+P(w[::-1])
    return tot
bad=0; n=0
for a in (4,5):
    for line in open(os.path.join(data,f'clusters_len{a}.txt')):
        if line.startswith('#') or not line.strip(): continue
        q=line.split(); p=[int(c) for c in q[0]]; jv=int(q[1]); n+=1
        if j_formula(p)!=jv: bad+=1; print("MISMATCH",q[0],j_formula(p),jv)
print(f"j by the catalogue formula vs cluster value: {n} patterns, {bad} mismatches")
sys.exit(1 if (bad or not all_ok) else 0)
