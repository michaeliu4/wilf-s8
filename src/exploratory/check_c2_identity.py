#!/usr/bin/env python3
"""Exhaustive check of the codimension-two identity c(sigma) = I_tau(sigma) - (beta_0(Gamma_tau(sigma)) - 1)
(Proposition on cluster weights vs inflation weights) for all tau of length <= 5 and all sigma in S_{a+2} containing tau."""
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
def beta0(sigma,tau):
    occ=occurrences(sigma,tau); parent=list(range(len(occ)))
    def f(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    for i in range(len(occ)):
        for j in range(i+1,len(occ)):
            if len(set(occ[i])&set(occ[j]))==len(tau)-1:
                a,b=f(i),f(j)
                if a!=b: parent[a]=b
    return len(set(f(i) for i in range(len(occ))))
bad=0; n=0
for a in range(2,6):
    for tau in itertools.permutations(range(1,a+1)):
        for sigma in itertools.permutations(range(1,a+3)):
            if not contains(sigma,tau): continue
            n+=1
            if cw(sigma,tau)!=I(sigma,tau)-(beta0(sigma,tau)-1): bad+=1; print("BAD",tau,sigma)
print("hosts checked:",n,"violations of c = I - (beta0-1):",bad)
