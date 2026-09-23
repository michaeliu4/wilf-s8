"""Intrinsic deletion-overlap formula for g_k, specialized evaluator for k=3.
No containing permutation is built or tested by this module.
"""
from itertools import combinations, combinations_with_replacement, permutations
from math import comb

def standardize(values):
    values=tuple(values)
    ranks={v:i+1 for i,v in enumerate(sorted(values))}
    return tuple(ranks[v] for v in values)

def validate(beta):
    beta=tuple(beta)
    if not beta or sorted(beta)!=list(range(1,len(beta)+1)):
        raise ValueError('beta must be a nonempty permutation of 1,...,m')
    return beta

def deletion_data(beta):
    m=len(beta); deck={}
    for d in range(1,min(3,m)+1):
        for P in combinations(range(1,m+1),d):
            ps=set(P)
            kept=[beta[i-1] for i in range(1,m+1) if i not in ps]
            deck[P]=(standardize(kept), (0,*sorted(kept),m+1))
    return deck

def boxes(beta, c, sigma, deck=None):
    """All forbidden row-gap boxes for fixed three column gaps and new ranks."""
    beta=validate(beta);m=len(beta)
    if deck is None:deck=deletion_data(beta)
    answer=set()
    for d in range(1,min(3,m)+1):
        for X in combinations(range(3),d):
            for P in combinations(range(1,m+1),d):
                if c[X[0]]>=P[0]:continue
                Q=tuple(c[j]-sum(p<=c[j] for p in P)+r+1 for r,j in enumerate(X))
                if deck[P][0]!=deck[Q][0]:continue
                qvalues=tuple(beta[q-1] for q in Q)
                if standardize(sigma[j] for j in X)!=standardize(qvalues):continue
                V=deck[P][1]
                L=[0]*3; U=[m]*3
                for j,v in zip(X,qvalues):
                    t=v-1-sum(w<v for w in qvalues)
                    axis=sigma[j]-1
                    L[axis]=V[t];U[axis]=V[t+1]-1
                answer.add((tuple(L),tuple(U)))
    return sorted(answer)

def interval_union_length(intervals):
    """Number of integers in an exact union of inclusive intervals."""
    last=-1;size=0
    for lo,hi in sorted(intervals):
        if lo<=hi:
            size+=max(0,hi-max(lo-1,last))
            last=max(last,hi)
    return size

def box_union_on_simplex(B,m):
    total=0
    for a in range(m+1):
        for b in range(a,m+1):
            intervals=[(max(b,L[2]),U[2]) for L,U in B
                       if L[0]<=a<=U[0] and L[1]<=b<=U[1] and U[2]>=b]
            total+=interval_union_length(intervals)
    return total

def g3(beta):
    beta=validate(beta);m=len(beta);deck=deletion_data(beta)
    correction=0
    for c in combinations_with_replacement(range(m+1),3):
        for sigma in permutations((1,2,3)):
            correction+=box_union_on_simplex(boxes(beta,c,sigma,deck),m)
    return 6*comb(m+3,3)**2-correction

if __name__=='__main__':
    import argparse,json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pattern',help='semicolon-separated permutation, e.g. 2;4;1;3')
    args=parser.parse_args();p=tuple(map(int,args.pattern.split(';')))
    print(json.dumps({'pattern':p,'g3':g3(p)}))
