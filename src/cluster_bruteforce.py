BAD=False
# cluster expansion for the number g_k(tau) of permutations of length m+k containing tau:
#   g_k(tau) = sum_{r=m}^{m+k} C(m+k,r)^2 (m+k-r)! c_r(tau),   c_r(tau) = sum_{rho in S_r} sum_{S covering rho} (-1)^{|S|+1}
# where S ranges over nonempty sets of occurrences of tau in rho whose union of positions is all of [r].
import itertools, sys
from math import comb, factorial
def red(s):
    r=sorted(s); return tuple(r.index(x)+1 for x in s)
def occs(rho,tau):
    m=len(tau); return [idx for idx in itertools.combinations(range(len(rho)),m) if red([rho[i] for i in idx])==tau]
def c_r(tau,r):
    tot=0
    for rho in itertools.permutations(range(1,r+1)):
        oc=occs(rho,tau)
        if not oc: continue
        # sum over nonempty subsets covering all positions: inclusion-exclusion over uncovered positions
        # sum_{S covering} (-1)^{|S|+1} = sum_{T subset [r]} (-1)^{|T|} * sum_{S subset occ avoiding T, S nonempty} (-1)^{|S|+1}
        #  = sum_T (-1)^{|T|} [n_T>=1] where n_T = number of occurrences disjoint from T  (since sum_{S nonempty subset of N} (-1)^{|S|+1} = 1 if N nonempty)
        s=0
        for tsize in range(r+1):
            for T in itertools.combinations(range(r),tsize):
                Tset=set(T); nT=sum(1 for o in oc if not (set(o)&Tset))
                if nT>=1: s+=(-1)**tsize
        tot+=s
    return tot
def g(tau,k):
    m=len(tau); n=m+k
    return sum(1 for pi in itertools.permutations(range(1,n+1)) if occs(pi,tau))
for tau in [(1,2),(2,1),(1,3,2),(2,3,1),(1,2,3),(2,4,1,3),(1,3,4,2),(2,1,4,3)]:
    m=len(tau)
    for k in [1,2,3]:
        if m+k>7: continue
        cs=[c_r(tau,r) for r in range(m,m+k+1)]
        pred=sum(comb(m+k,r)**2*factorial(m+k-r)*cs[r-m] for r in range(m,m+k+1))
        print(tau,'k=%d'%k,'c_r =',cs,'cluster formula',pred,'direct',g(tau,k))
        if pred!=g(tau,k): BAD=True

import sys
sys.exit(1 if BAD else 0)
