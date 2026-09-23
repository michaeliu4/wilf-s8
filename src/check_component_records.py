#!/usr/bin/env python3
"""Validate the full stated finite-range component logs; no fresh enumeration."""
from __future__ import annotations
import argparse,itertools,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def require(ok: bool, message: str) -> None:
    if not ok:raise ValueError(message)

def inflation_numbers(a: int,k: int) -> list[int]:
    co=[1]+[0]*k
    for _ in range(a):
        co=[sum(co[d-e]*math.factorial(e+1) for e in range(d+1)) for d in range(k+1)]
    return co

def check_file(path: Path,k: int,amax: int) -> int:
    expected={''.join(map(str,t)) for a in range(2,amax+1) for t in itertools.permutations(range(1,a+1))}
    seen=set()
    for line in path.read_text().splitlines():
        m=re.fullmatch(r'tau=(\d+) k=(\d+) n=(\d+)  rho containing tau: (\d+)  classes total: (\d+)  rho with a class of chi!=1: (\d+)  rho with chi!=beta0: (\d+)  cells:(.*)',line)
        require(m is not None,f'malformed component row: {line!r}')
        tau=m[1];a=len(tau);n=a+k
        require(tau in expected and tau not in seen,'component-log coverage error')
        require(int(m[2])==k and int(m[3])==n,'wrong component-log scope')
        require(m[6]=='0' and m[7]=='0','nontrivial Euler-characteristic defect in claimed range')
        nd=inflation_numbers(a,k)
        cells={int(d):int(v) for d,v in re.findall(r'f(\d+)=(\d+)',m[8])}
        expected_cells={d:math.comb(n,a+d)**2*math.factorial(k-d)*nd[d] for d in range(k+1)}
        require(cells==expected_cells,'cell totals differ from universal inflation counts')
        ck=sum((-1)**d*v for d,v in cells.items())
        require(int(m[5])==ck,'component total differs from C_k')
        seen.add(tau)
    require(seen==expected,f'incomplete component coverage: {len(seen)}/{len(expected)}')
    return len(seen)

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory',type=Path,default=ROOT/'checks');args=ap.parse_args()
    for k,amax in ((3,6),(4,5)):
        n=check_file(args.directory/f'chi_components_k{k}.txt',k,amax)
        print(f'PASS: {n} retained component rows, k={k}, 2<=a<={amax}; all scopes, defects and cell totals checked')
    print('The a=1 case is a simplex and is treated directly in the manuscript.')
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:
        print(f'ERROR: {e}',file=sys.stderr);sys.exit(1)
