#!/usr/bin/env python3
"""Exact bounded regressions for the catalogue dictionary, cubic comparison,
projection-preserving elimination, and the return figure. These tests supplement
but do not replace the all-parameter proofs in the manuscript.
"""
from __future__ import annotations
import itertools
import json
import random
from math import factorial
from pathlib import Path
import sympy as sp
from return_catalogue import catalogue, return_word, primitive_parameters


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def polynomial_checks() -> dict:
    a = sp.Symbol('a')
    C3 = (a**6+6*a**5+10*a**4+10*a**3+37*a**2+44*a+36)/6
    M3 = (a**6+6*a**5+10*a**4+4*a**3+19*a**2+62*a+66)/6
    require(sp.expand(C3-M3-(a+1)*(a*a+2*a-5)) == 0, 'cubic difference')
    # N_d(a) = [t^d](1+sum_(i>=1) (i+1)! t^i)^a,
    # computed by its binomial expansion in a.
    K = 6
    f = [sp.Integer(0)] + [sp.Integer(factorial(i+1)) for i in range(1,K+1)]
    powers = [[sp.Integer(1)]+[sp.Integer(0)]*K]
    for j in range(1,K+1):
        powers.append([sum(powers[-1][d-i]*f[i] for i in range(1,d+1)) for d in range(K+1)])
    choose = lambda x,j: sp.prod(x-i for i in range(j))*sp.Rational(1,factorial(j))
    N = [sp.expand(sum(choose(a,j)*powers[j][d] for j in range(d+1))) for d in range(K+1)]
    for k in range(1,K+1):
        C = sp.Poly(sp.expand(sum((-1)**d*N[d]*choose(a+k,k-d)**2*factorial(k-d) for d in range(k+1))),a)
        require(C.degree()==2*k, f'degree C_{k}')
        require(C.nth(2*k)==sp.Rational(1,factorial(k)), f'leading C_{k}')
        require(C.nth(2*k-1)==sp.Rational(k*(k-1),factorial(k)), f'next C_{k}')
    checked = 0
    for n in range(17,202,2):
        p = [1+(4*i % n) for i in range(n)]
        require(sorted(p)==list(range(1,n+1)), 'modular permutation')
        require(all(abs(p[i]-p[i+d])>=4 for d in (1,2,3) for i in range(n-d)), 'separation')
        checked += 1
    return {'cubic_identity':'exact symbolic equality','leading_coefficients_k':list(range(1,K+1)),
            'separated_modular_patterns':checked,'odd_lengths':[17,201]}


def dictionary_checks() -> dict:
    count = 0
    for l in range(2,26):
        for (a,b,t,s), w in catalogue(l):
            q,v = b-1+2*t,a-1+2*s
            h1,h2,h3 = a-2,2*(s+1),l-a-2*s
            w1,w2,w3 = b-2,2*(t+1),l-b-2*t
            require(min(h1,h3,w1,w3)>=0 and h2>=2 and w2>=2, 'block dimensions')
            require(h1+h2+h3==l==w1+w2+w3, 'square support')
            require(h1-w2//2==w3-h2//2, 'Ray-West compatibility')
            require((h1,h2,h3)==((a-1)-1,(v+2)-(a-1),(l+1)-(v+2)), 'row gaps')
            require((w1,w2,w3)==((b-1)-1,(q+2)-(b-1),(l+1)-(q+2)), 'column gaps')
            require(primitive_parameters(w)==(a,b,t,s), 'recovered parameters')
            count += 1
    require(return_word(6,2,1,1)==(6,1,8,2,3,4,5,7), 'Example 8.4')
    rho=(2,4,1,6,3,5)
    def std(xs):
        return tuple(sorted(xs).index(v)+1 for v in xs)
    O=(2,4,5,6); Op=(1,2,3,5)
    require(std([rho[i-1] for i in O])==std([rho[i-1] for i in Op])==(2,4,1,3),'figure occurrences')
    require(set(range(1,7))-set(O)=={1,3} and set(range(1,7))-set(Op)=={4,6},'figure deletions')
    return {'primitive_support_dictionaries':count,'lengths':[2,25],
            'Ray_West_example_8_4':'61823457 = Z(6,2;1,1)', 'return_figure':'passed'}


def elimination_checks(instances: int=400) -> dict:
    rng=random.Random(20260921)
    steps=0; assignments=0
    for trial in range(instances):
        n=rng.randrange(2,8)
        bases=list(zip(rng.sample(range(60),n),rng.sample(range(60),n)))
        domains=[]
        for base in bases:
            d=[base]
            while len(d)<3:
                point=(rng.randrange(60),rng.randrange(60))
                if point not in d: d.append(point)
            domains.append(d)
        constraints=[]; used=1
        while used<n:
            articulation=rng.randrange(used)
            take=rng.randrange(1,min(3,n-used)+1)
            axis=rng.randrange(2)
            variables=[articulation]+list(range(used,used+take))
            variables.sort(key=lambda i:bases[i][axis])
            constraints.append((variables,axis)); used+=take
        # This construction adds only new vertices to one existing variable:
        # its incidence graph is a tree.
        def feasible(x):
            return all(all(domains[u][x[u]][axis]<domains[v][x[v]][axis]
                           for u,v in zip(variables,variables[1:]))
                       for variables,axis in constraints)
        F={x for x in itertools.product(range(3),repeat=n) if feasible(x)}
        require(bool(F),'constructed nonempty instance')
        assignments += len(F)
        active=set(range(n)); current=[(list(vs),ax) for vs,ax in constraints]
        while active:
            nonunary=[(vs,ax) for vs,ax in current if len(vs)>1]
            degree={i:sum(i in vs for vs,_ in nonunary) for i in active}
            if nonunary:
                choices=[(vs,ax) for vs,ax in nonunary if sum(degree[i]>1 for i in vs)<=1]
                require(bool(choices),'pendant constraint must exist')
                vs,axis=choices[0]
                # Left endpoint is private unless it is the articulation.
                left=degree[vs[0]]==1
                i=vs[0] if left else vs[-1]
                require(degree[i]==1,'selected role private')
                candidates={x[i] for x in F}
                d=(min if left else max)(candidates,key=lambda c:domains[i][c][axis])
            else:
                i=min(active);d=min(x[i] for x in F)
            before={tuple(x[j] for j in sorted(active-{i})) for x in F}
            for x in F:
                y=x[:i]+(d,)+x[i+1:]
                require(y in F,'replacement must preserve every feasible assignment')
            F={x for x in F if x[i]==d}
            after={tuple(x[j] for j in sorted(active-{i})) for x in F}
            require(before==after,'full projection invariant')
            active.remove(i);steps+=1
            reduced=[]
            for vs,axis in current:
                if i not in vs: reduced.append((vs,axis));continue
                j=vs.index(i)
                for part in (vs[:j],vs[j+1:]):
                    if part:reduced.append((part,axis))
            current=reduced
        require(len(F)==1,'terminal point')
    return {'seed':20260921,'finite_forest_instances':instances,
            'initial_feasible_assignments':assignments,'projection_preserving_steps':steps}


def main() -> None:
    result={'polynomials':polynomial_checks(),'catalogue_dictionary':dictionary_checks(),
            'elimination':elimination_checks(),
            'scope':'Exact symbolic identities and bounded regression cases; not exhaustive proof verification.'}
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
