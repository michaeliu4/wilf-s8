#!/usr/bin/env python3
"""For each tau of length <= 5, lists the inflation hosts sigma in S_{a+2} with cluster weight c(sigma) != I_tau(sigma)
(referee item A extended to codimension two)."""
import itertools
from functools import lru_cache
def std(seq):
    s=sorted(seq); return tuple(s.index(x)+1 for x in seq)
def contains(sigma,tau):
    a=len(tau)
    for T in itertools.combinations(range(len(sigma)),a):
        if std([sigma[i] for i in T])==tau: return True
    return False
def occurrences(sigma,tau):
    a=len(tau); return [T for T in itertools.combinations(range(len(sigma)),a) if std([sigma[i] for i in T])==tau]
def cw(sigma,tau):
    r=len(sigma); a=len(tau); tot=0
    for m in range(a,r+1):
        for T in itertools.combinations(range(r),m):
            if contains(tuple(sigma[i] for i in T),tau): tot+=(-1)**(r-m)
    return tot
def I(sigma,tau):
    # number of ways sigma = tau[pi_1..pi_a]
    r=len(sigma); a=len(tau); cnt=0
    for cuts in itertools.combinations(range(1,r),a-1):
        bounds=[0]+list(cuts)+[r]
        blocks=[sigma[bounds[i]:bounds[i+1]] for i in range(a)]
        ok=True; reps=[]
        for b in blocks:
            if max(b)-min(b)!=len(b)-1: ok=False;break
            reps.append(min(b))
        if ok and std(reps)==tau: cnt+=1
    return cnt
# codim 2: is c(sigma)=I(sigma) for every inflation host sigma in S_{a+2}?  and codim 3 (a<=4)
for a in range(2,6):
    for tau in itertools.permutations(range(1,a+1)):
        bad2=[]; 
        for sigma in itertools.permutations(range(1,a+3)):
            i=I(sigma,tau)
            if i>0:
                c=cw(sigma,tau)
                if c!=i: bad2.append((sigma,c,i))
        print("a=%d tau=%s codim2 inflation hosts with c!=I: %d"%(a,''.join(map(str,tau)),len(bad2)), bad2[:3])
