#!/usr/bin/env python3
"""Cluster numbers of the monotone pattern iota_a from the discrete Bessel kernel.
Poissonized Plancherel measure with parameter theta: P(lambda) = e^{-theta} theta^{|lambda|} (f^lambda/|lambda|!)^2.
Schensted: |Av_n(iota_a)| = #{pi in S_n : LIS(pi) < a} = sum_{lambda |- n, lambda_1 <= a-1} (f^lambda)^2, hence
   e^{-theta} sum_n |Av_n(iota_a)| theta^n/n!^2 = P_theta(lambda_1 <= a-1),
and the cluster expansion gives sum_r c_r(iota_a) theta^r/r!^2 = 1 - e^{-theta} sum_n |Av_n| theta^n/n!^2 = P_theta(lambda_1 >= a).
Borodin-Okounkov-Olshanski / Johansson: {lambda_i - i} is determinantal with the discrete Bessel kernel
   K(x,y) = sum_{s>=1} J_{x+s}(2 sqrt theta) J_{y+s}(2 sqrt theta),
so P_theta(lambda_1 <= a-1) = det(I - K) on l^2({a-1, a, a+1, ...}) and
   sum_r c_r theta^r / r!^2 = 1 - det(I-K) = sum_{p>=1} (-1)^{p+1} sum_{x_1<...<x_p, x_i>=a-1} det[K(x_i,x_j)].
This script expands the right-hand side as a power series in theta (exactly, with rationals) and compares
with the cluster numbers computed by the inverse cluster transform from the hook-length formula; it also
prints the contribution of each Fredholm order p.  The p = 1 term equals (-1)^{r-a} C(2r-2, r-a) exactly
(a binomial identity), so the binomial law holds as long as the p >= 2 terms vanish, i.e. for r <= 2a+1.
Usage: bessel_clusters.py a RMAX"""
import sys
from fractions import Fraction
from math import factorial, comb
from itertools import combinations
a=int(sys.argv[1]); R=int(sys.argv[2])     # cluster sizes r <= R
D=2*R+2                                     # work with series in u = sqrt(theta) up to u^D
def J(m):
    """J_m(2u) as list of coefficients in u, degree <= D."""
    c=[Fraction(0)]*(D+1)
    k=0
    while m+2*k<=D:
        c[m+2*k]=Fraction((-1)**k, factorial(k)*factorial(k+m)); k+=1
    return c
def mul(p,q):
    r=[Fraction(0)]*(D+1)
    for i,x in enumerate(p):
        if x==0: continue
        for j,y in enumerate(q):
            if i+j>D: break
            if y: r[i+j]+=x*y
    return r
def add(p,q): return [x+y for x,y in zip(p,q)]
def sub(p,q): return [x-y for x,y in zip(p,q)]
Js={m:J(m) for m in range(0,D+2)}
X=list(range(a-1, R+1))          # only x <= R-? matter: K(x,y) = O(u^{x+y+2}); with x,y>=a-1 and degree <= 2R
K={}
for x in X:
    for y in X:
        if x+y+2>D: K[(x,y)]=[Fraction(0)]*(D+1); continue
        s=[Fraction(0)]*(D+1); t=1
        while x+t+y+t<=D:
            s=add(s,mul(Js[x+t],Js[y+t])); t+=1
        K[(x,y)]=s
def det(rows):
    # Laplace expansion (small p)
    if len(rows)==1: return K[(rows[0],rows[0])]
    x=rows[0]; res=[Fraction(0)]*(D+1)
    for j,y in enumerate(rows):
        minor=[r for r in rows[1:]]
        # expand along first row: entry K(x,y) times det of submatrix with column y removed
        sub_rows=rows[1:]; sub_cols=[c for c in rows if c!=y]
        res=add(res, [((-1)**j)*v for v in mul(K[(x,y)], det_gen(sub_rows,sub_cols))])
    return res
def det_gen(rows,cols):
    if len(rows)==1: return K[(rows[0],cols[0])]
    x=rows[0]; res=[Fraction(0)]*(D+1)
    for j,y in enumerate(cols):
        res=add(res,[((-1)**j)*v for v in mul(K[(x,y)], det_gen(rows[1:],[c for c in cols if c!=y]))])
    return res
# hook-length reference
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
def cref(r,a): return sum((-1)**(r-t)*comb(r,t)**2*factorial(r-t)*(factorial(t)-Av(t,a)) for t in range(a,r+1))
total=[Fraction(0)]*(D+1); byp={}
pmax=4
for p in range(1,pmax+1):
    term=[Fraction(0)]*(D+1)
    for rows in combinations(X,p):
        if sum(rows)*2+2*p>D: continue   # det is O(u^{2 sum x + 2p})
        term=add(term, det_gen(list(rows),list(rows)))
    byp[p]=term
    total=add(total,[((-1)**(p+1))*v for v in term])
print(f"a={a}: c_r(iota_a) for r={a}..{R}; columns: r, hook-length value, Fredholm value, p=1 term (binomial), p=2, p=3, p=4 terms (each times r!^2)")
for r in range(a,R+1):
    f=factorial(r)**2
    vals=[byp[p][2*r]*f*((-1)**(p+1)) for p in range(1,pmax+1)]
    tot=total[2*r]*f
    print(r, cref(r,a), tot, 'OK' if tot==cref(r,a) else 'XX', [int(v) for v in vals], "binomial", (-1)**(r-a)*comb(2*r-2,r-a))
