#!/usr/bin/env python3
"""Brute-force verification of the intermediate identities in Appendix A of the manuscript (Lemmas A.4-A.6, the intersection
table, the recurrence (43) and the layered formula) for all layered alpha of length a <= AMAX.  Needs the compiled
`clusters` binary next to this file.  Usage: check_layered.py AMAX"""
import sys, itertools, os
from math import factorial
from functools import lru_cache
def std(seq):
    s=sorted(seq); return tuple(s.index(x)+1 for x in seq)
def contains(pi,tau):
    a=len(tau); n=len(pi)
    for S in itertools.combinations(range(n),a):
        if std([pi[i] for i in S])==tau: return True
    return False
def layered(comp):
    p=[]; base=0
    for b in comp:
        p+= [base+b-i for i in range(b)]; base+=b
    return tuple(p)
def compositions(a):
    if a==0: yield (); return
    for first in range(1,a+1):
        for rest in compositions(a-first): yield (first,)+rest
def inv(p):
    q=[0]*len(p)
    for i,x in enumerate(p): q[x-1]=i+1
    return tuple(q)
def M3(a): return (a**6+6*a**5+10*a**4+4*a**3+19*a**2+62*a+66)//6
AMAX=int(sys.argv[1])
FAILED=False
allperms={n:list(itertools.permutations(range(1,n+1))) for n in range(1,max(AMAX+4,8))}
import subprocess
def g(k,tau):
    out=subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)),'clusters'),str(k),''.join(map(str,tau))],capture_output=True,text=True).stdout
    av=[int(l.split()[3].split('=')[1]) for l in out.splitlines() if l.startswith('r=')][-1]
    return factorial(len(tau)+k)-av
for a in range(2,AMAX+1):
    for comp in compositions(a):
        alpha=layered(comp); beta=alpha+(a+1,)   # beta = alpha (+) 1
        n=a+2
        # sets in S_n
        A=[set() for _ in range(3)]; E=set()
        for rho in allperms[n]:
            for i in range(3):
                if contains(std([x for x in rho if x<=a+i]),alpha): A[i].add(rho)   # alpha among the a+i smallest values
            if contains(rho,beta): E.add(rho)
        K=E&A[0]
        Ainv=[set(inv(r) for r in X) for X in A]
        L=len(E&A[0]&Ainv[0])
        eps=1 if (len(comp)>=2 and comp[-1]>=2) else 0
        table={'A0':(len(A[0]),(a+2)*(a+1)),'A1':(len(A[1]),(a+2)*(a*a+1)),'A2':(len(A[2]),g(2,alpha)),
               'E':(len(E),(a+1)**2+1),'K':(len(K),2*a+3),'A0A0*':(len(A[0]&Ainv[0]),7),'A0A1*':(len(A[0]&Ainv[1]),4*a+3),
               'A1A1*':(len(A[1]&Ainv[1]),3*a*a+2*a+2+eps),'L':(L,5)}
        ok=all(v[0]==v[1] for v in table.values())
        # f'(rho) = number of hosts tau in S_{a+3} containing beta whose prefix of length n standardizes to rho (Lemma A.4)
        f={}
        for rho in allperms[n]:
            f[rho]=(rho in A[0])+(rho in A[1])+(rho in A[2])+(a+1)*(rho in E)-(rho in K)
        fdirect={rho:0 for rho in allperms[n]}
        for tau in allperms[a+3]:
            if contains(tau,beta): fdirect[std(tau[:n])]+=1
        ok_f = all(f[r]==fdirect[r] for r in allperms[n])
        J=sum(f[r]*f[inv(r)] for r in allperms[n])
        Jformula=(3*a**4+22*a**3+57*a**2+66*a+38)//2+eps
        # J directly: pi in S_{a+4}, pi(a+4)!=a+4, prefix of length a+3 contains beta, pi minus max contains beta
        Jdirect=None; hh=a+3
        for pi in (allperms[a+4] if a<=3 else []):
            Jdirect = Jdirect or 0
            if pi[-1]==a+4: continue
            pre=std(pi[:hh]); nomax=std([x for x in pi if x!=a+4])
            if contains(pre,beta) and contains(nomax,beta): Jdirect+=1
        # recurrence g3(alpha+1) = g3(alpha) + 2(a+3) g2(beta) - J
        g3b=g(3,beta); g3a=g(3,alpha); g2b=g(2,beta)
        rec = (g3b == g3a + 2*(a+3)*g2b - J)
        formula = (g3b == M3(a+1) - sum(1 for i in range(1,len(comp+(1,))-1) if (comp+(1,))[i]>=2))
        print(comp, "table ok" if ok else ("TABLE MISMATCH",table), "f' ok" if ok_f else "F' MISMATCH", "J", J, Jdirect, Jformula, "rec" if rec else "REC FAIL", "formula" if formula else "FORMULA FAIL")
        if not (ok and ok_f and rec and formula and (Jdirect is None or Jdirect==J) and Jformula==J): FAILED=True

sys.exit(1 if FAILED else 0)
