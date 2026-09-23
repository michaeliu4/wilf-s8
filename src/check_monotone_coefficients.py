#!/usr/bin/env python3
"""Exact checks of Section 10, independent of the package's hook-length code.

Tableau dimensions are computed by corner removal. Three small Fredholm
cases are also expanded directly from the Bessel series in Fraction arithmetic.
This is bounded computational evidence, not a substitute for the general proofs.
Usage: python3 src/check_monotone_coefficients.py [--amax 12]
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, permutations
from math import comb, factorial
import json


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@lru_cache(None)
def partitions(n: int, upper: int) -> tuple[tuple[int, ...], ...]:
    if not n:
        return ((),)
    return tuple((v,) + q for v in range(min(n, upper), 0, -1)
                 for q in partitions(n-v, v))


@lru_cache(None)
def tableaux(shape: tuple[int, ...]) -> int:
    if not shape:
        return 1
    total = 0
    for i, v in enumerate(shape):
        if i+1 == len(shape) or v > shape[i+1]:
            q = list(shape)
            q[i] -= 1
            if not q[-1]:
                q.pop()
            total += tableaux(tuple(q))
    return total


def cat(n: int) -> int:
    return comb(2*n, n)//(n+1)


def product(p: dict[int, Q], q: dict[int, Q], limit: int) -> dict[int, Q]:
    out: dict[int, Q] = {}
    for i, a in p.items():
        for j, b in q.items():
            if i+j <= limit:
                out[i+j] = out.get(i+j, Q(0)) + a*b
    return {i: c for i, c in out.items() if c}


def add(p: dict[int, Q], q: dict[int, Q], sign: int = 1) -> None:
    for i, a in q.items():
        p[i] = p.get(i, Q(0)) + sign*a
        if not p[i]:
            del p[i]


def fredholm_case(a: int, p: int) -> dict:
    L = p*(a+p-1)
    limit = 2*(L+1)

    @lru_cache(None)
    def J(m: int) -> dict[int, Q]:
        return {m+2*j: Q((-1)**j, factorial(j)*factorial(m+j))
                for j in range((limit-m)//2+1)}

    @lru_cache(None)
    def kernel(x: int, y: int) -> dict[int, Q]:
        out: dict[int, Q] = {}
        for s in range(1, (limit-x-y)//2+1):
            add(out, product(J(x+s), J(y+s), limit))
        return out

    total: dict[int, Q] = {}
    # A row tuple cannot contribute by degree theta^(L+1) unless sum(x)+p<=L+1.
    for xs in combinations(range(a-1, L+2), p):
        if sum(xs)+p > L+1:
            continue
        for perm in permutations(range(p)):
            inv = sum(perm[i] > perm[j] for i in range(p) for j in range(i+1, p))
            term = {0: Q(1)}
            for i in range(p):
                term = product(term, kernel(xs[i], xs[perm[i]]), limit)
            add(total, term, (-1)**inv)
    expected = Q(tableaux((a+p-1,)*p)**2, factorial(L)**2)
    require(total and min(total) == 2*L, f"wrong first power for {(a,p)}")
    require(total[2*L] == expected, f"wrong rectangle coefficient for {(a,p)}")
    return {"a": a, "p": p, "first_theta_power": L,
            "coefficient": str(expected), "tableau_square": tableaux((a+p-1,)*p)**2}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--amax', type=int, default=12)
    args = parser.parse_args()
    require(1 <= args.amax <= 16, 'supported amax range is 1..16')
    values = []
    comparisons = 0
    for a in range(1, args.amax+1):
        g = {r: sum(tableaux(lam)**2 for lam in partitions(r, r) if lam[0] >= a)
             for r in range(a, 2*a+4)}
        c = {r: sum((-1)**(r-t)*comb(r,t)**2*factorial(r-t)*g[t]
                    for t in range(a, r+1)) for r in g}
        for k in range(a+2):
            require(c[a+k] == (-1)**k*comb(2*a+2*k-2,k), f'binomial law a={a}, k={k}')
            comparisons += 1
        first = (-1)**a*comb(4*a+2,a+2) - cat(a+1)**2
        nxt = (-1)**(a+1)*comb(4*a+4,a+3) + (a+1)*cat(a+2)**2
        require(c[2*a+2] == first, f'first correction a={a}')
        require(c[2*a+3] == nxt, f'next correction a={a}')
        comparisons += 2
        b = a+1
        require(tableaux((b+1,b)) == cat(b+1), f'two-row dimension b={b}')
        require(2*tableaux((b,b,1)) == b*cat(b+1), f'three-row dimension b={b}')
        require(4*(2*b+1)**2*cat(b)**2 - (4+b*b)*cat(b+1)**2 == 4*b*cat(b+1)**2,
                f'hook-length simplification b={b}')
        values.append({'a': a, 'c_2a_plus_2': first, 'c_2a_plus_3': nxt})
    print(json.dumps({'status': 'PASS', 'amax': args.amax,
                      'cluster_coefficient_comparisons': comparisons,
                      'dimensions': 'corner-removal recurrence', 'values': values,
                      'direct_fredholm_cases': [fredholm_case(a,p) for a,p in ((1,2),(2,2),(1,3))]}, indent=2))


if __name__ == '__main__':
    main()
