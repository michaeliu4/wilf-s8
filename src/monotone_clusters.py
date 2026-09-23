#!/usr/bin/env python3
"""Cluster numbers of the monotone pattern iota_a from the hook-length formula (RSK), via the inverse cluster
transform c_r = sum_t (-1)^{r-t} C(r,t)^2 (r-t)! g_{t-a}; tests the binomial law c_{a+k} = (-1)^k C(2a+2k-2,k)
and prints the deviations from it.  Usage: monotone_clusters.py AMAX KMAX"""
import sys
BAD=False
from math import comb, factorial
def partitions(n, maxpart):
    if n==0: yield (); return
    for p in range(min(n,maxpart),0,-1):
        for rest in partitions(n-p,p): yield (p,)+rest
def flam(lam):
    n=sum(lam)
    if n==0: return 1
    conj=[sum(1 for l in lam if l>j) for j in range(lam[0])]
    h=1
    for i,l in enumerate(lam):
        for j in range(l): h*=(l-j-1)+(conj[j]-i-1)+1
    return factorial(n)//h
def Av(n,a): return sum(flam(l)**2 for l in partitions(n,a-1))
def g(k,a): return factorial(a+k)-Av(a+k,a)
def c(r,a): return sum((-1)**(r-t)*comb(r,t)**2*factorial(r-t)*g(t-a,a) for t in range(a,r+1))
def cat(n): return comb(2*n,n)//(n+1)
AMAX=int(sys.argv[1]); KMAX=int(sys.argv[2])
for a in range(1,AMAX+1):
    first_fail=None; devs=[]
    for k in range(0,KMAX+1):
        cv=c(a+k,a); b=(-1)**k*comb(2*a+2*k-2,k)
        if cv!=b and first_fail is None: first_fail=k
        if k<=a+1 and cv!=b: BAD=True
        if k==a+2 and cv-b!=-cat(a+1)**2: BAD=True
        if k==a+3 and cv-b!=(a+1)*cat(a+2)**2: BAD=True
        devs.append(cv-b)
    print(f"a={a}: binomial law holds for k<= {first_fail-1 if first_fail is not None else KMAX}; deviations at k=a+2,a+3,a+4:",
          [devs[k] if k<=KMAX else None for k in (a+2,a+3,a+4)],
          " Cat(a+1)^2=",cat(a+1)**2," (a+1)Cat(a+2)^2=",(a+1)*cat(a+2)**2)

import sys
sys.exit(1 if BAD else 0)
