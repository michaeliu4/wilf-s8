#!/usr/bin/env python3
"""P(tau) := number of rho in S_{a+2} containing exactly two occurrences of tau, with disjoint
complements, the second occurrence up-right of the first (role-wise larger positions and values).
Checks w(tau) = P(tau) + P(tau^r) for all tau of length <= L, where w is the recursive interval weight."""
import sys, itertools, subprocess, os
from collections import Counter
here=os.path.dirname(os.path.abspath(__file__))
def std(seq):
    s=sorted(seq); return tuple(s.index(x)+1 for x in seq)
def intervals(t):
    n=len(t); out=[]
    for i in range(n):
        for l in range(2,n):
            if i+l>n: break
            seg=t[i:i+l]
            if max(seg)-min(seg)==l-1: out.append(std(seg))
    return out
def run(t,K,extra=()):
    s=''.join(map(str,t))
    r=subprocess.run([os.path.join(here,'clusters'),str(K),s]+list(extra),capture_output=True,text=True)
    return r.stdout
def j_of(t):
    a=len(t); c=[int(line.split()[1].split('=')[1]) for line in run(t,2).splitlines()]
    return 2*a*(a+2)-c[2]
def P_of(t):
    a=len(t); cnt=0; ur=0; dr=0
    for line in run(t,2,('-list',)).splitlines():
        parts=line.split(); rho=[int(c) for c in parts[0].split('.')]; m=int(parts[1])
        if m!=2: continue
        o1=[int(x) for x in parts[2].rstrip(',').split(',')]; o2=[int(x) for x in parts[3].rstrip(',').split(',')]
        if set(o1)&set(o2) and len(set(o1)&set(o2))!=a-2: continue
        if len(set(o1)|set(o2))!=a+2: continue
        # o1 is lexicographically first (leftmost start). second up-right?
        up=all(rho[o2[i]]>rho[o1[i]] for i in range(a)); right=all(o2[i]>o1[i] for i in range(a))
        down=all(rho[o2[i]]<rho[o1[i]] for i in range(a))
        if right and up: ur+=1
        elif right and down: dr+=1
        else: cnt+=1
    return ur,dr,cnt
if __name__=="__main__":
    L=int(sys.argv[1])
    w={}
    bad=0; tot=0
    for l in range(2,L+1):
        stats=Counter()
        for t in itertools.permutations(range(1,l+1)):
            w[t]=j_of(t)-sum(w[I] for I in intervals(t))
        for t in itertools.permutations(range(1,l+1)):
            ur,dr,other=P_of(t); tr=tuple(reversed(t))
            stats[(w[t],ur,dr,other)]+=1
            tot+=1
            if w[t]!=ur+dr: bad+=1; print("MISMATCH",''.join(map(str,t)),"w=",w[t],"ur,dr,other=",ur,dr,other)
        print(f"l={l}: (w, #up-right pure returns, #down-right, #other) distribution: {dict(stats)}")
    print("checked",tot,"patterns; mismatches:",bad)
