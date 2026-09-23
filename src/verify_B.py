#!/usr/bin/env python3
"""Certificate for the interval formula (Theorem B): for every tau of length <= L,
 j(tau) = sum over intervals I of tau (|I|>=2) of [U(std I) + D(std I)],
 where U(pi)=1 iff some permutation of length |pi|+2 contains exactly two occurrences of pi whose
 complements are disjoint and the second is up-right of the first (role-wise), D(pi) = U(pi^r).
Equivalently w(pi) := j(pi) - sum_{proper intervals} w = U(pi)+D(pi).  Uses ./clusters."""
import sys, itertools, os
from pure_returns import j_of, P_of, intervals
L=int(sys.argv[1]); L0=int(sys.argv[2]) if len(sys.argv)>2 else 2; w={}; U={}
for l in range(2,L+1):
    bad=0; cnt=0
    for t in itertools.permutations(range(1,l+1)):
        w[t]=j_of(t)-sum(w[I] for I in intervals(t))
        if l<L0: continue
        ur,dr,other=P_of(t); U[t]=(ur,dr)
        if w[t]!=ur+dr: bad+=1; print("MISMATCH",''.join(map(str,t)),w[t],ur,dr)
        cnt+=1
    nU=sum(1 for t in U if len(t)==l and U[t][0]==1)
    print(f"length {l}: {cnt} patterns checked, mismatches {bad}; #patterns with U=1: {nU}; sum w = {sum(w[t] for t in w if len(t)==l)}", flush=True)
import sys
sys.exit(1 if bad else 0)
