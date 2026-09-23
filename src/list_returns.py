#!/usr/bin/env python3
"""List all patterns of length l with a pure up-right return, with the return rho and the role shifts."""
import sys, itertools, subprocess, os
here=os.path.dirname(os.path.abspath(__file__))
def run(t,K,extra=()):
    s=''.join(map(str,t))
    return subprocess.run([os.path.join(here,'clusters'),str(K),s]+list(extra),capture_output=True,text=True).stdout
l=int(sys.argv[1])
for t in itertools.permutations(range(1,l+1)):
    a=l
    for line in run(t,2,('-list',)).splitlines():
        parts=line.split(); rho=[int(c) for c in parts[0].split('.')]; m=int(parts[1])
        if m!=2: continue
        o1=[int(x) for x in parts[2].rstrip(',').split(',')]; o2=[int(x) for x in parts[3].rstrip(',').split(',')]
        if len(set(o1)|set(o2))!=a+2: continue
        up=all(rho[o2[i]]>rho[o1[i]] for i in range(a)); right=all(o2[i]>o1[i] for i in range(a))
        if not (up and right): continue
        Q=sorted(set(o1)&set(o2))
        r1={p:i+1 for i,p in enumerate(o1)}; r2={p:i+1 for i,p in enumerate(o2)}
        v1={p:sorted(rho[q] for q in o1).index(rho[p])+1 for p in o1}; v2={p:sorted(rho[q] for q in o2).index(rho[p])+1 for p in o2}
        s=''.join(str(r2[q]-r1[q]) for q in Q); tt=''.join(str(v2[q]-v1[q]) for q in Q)
        U=[p for p in o1 if p not in Q]; Up=[p for p in o2 if p not in Q]
        print(''.join(map(str,t)),"rho",''.join(map(str,rho)),"posshift",s,"valshift",tt,"privroles O:",[r1[p] for p in U],"O':",[r2[p] for p in Up],"privvalroles O:",[v1[p] for p in U],"O':",[v2[p] for p in Up])
