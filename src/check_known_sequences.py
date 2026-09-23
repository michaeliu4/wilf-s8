#!/usr/bin/env python3
"""Fail-closed checks of known class totals and exact cluster/avoidance sequences."""
from __future__ import annotations
import argparse
from pathlib import Path
import re, subprocess, sys
HERE=Path(__file__).resolve().parent

def require(condition: bool, message: str) -> None:
    if not condition: raise ValueError(message)

def parse_clusters(text: str) -> dict[int,tuple[int,int]]:
    rows={}
    for line in text.splitlines():
        m=re.fullmatch(r'r=(\d+) c_r=(-?\d+) clusters=(\d+) Av_(\d+)=(\d+)',line)
        require(m is not None, f'malformed cluster output: {line!r}')
        n=int(m[1]); require(n==int(m[4]) and n not in rows,'wrong or duplicate row label')
        rows[n]=(int(m[2]),int(m[5]))
    require(bool(rows),'empty cluster output')
    return rows

def check_cluster_output(text: str, expected: dict[int,tuple[int,int]]) -> None:
    rows=parse_clusters(text)
    require(rows==expected, f'cluster/avoidance sequence mismatch: {rows} != {expected}')

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=('classes','clusters'))
    args=ap.parse_args()
    if args.mode=='classes':
        for m,count in ((4,4),(5,16),(6,91),(7,595),(8,4755)):
            out=subprocess.run([sys.executable,str(HERE/'known_classes.py'),str(m)],capture_output=True,text=True,check=True).stdout
            require(out.strip()==f'{m} {count}',f'wrong class total: {out!r}')
            print(f'S_{m}: {count} known-equivalence classes: PASS')
        out=subprocess.run([sys.executable,str(HERE/'known_classes.py'),'4','--with-1342'],capture_output=True,text=True,check=True).stdout
        require(out.strip()=='4 3','the extra length-four equivalence failed')
        print('S_4 with 1342~2413: 3 classes: PASS')
    else:
        # All rows are checked, including the initial rows; no missing-row success.
        examples={}
        # The Catalan values alone do not determine these higher cluster values;
        # compute their exact triangular inverse, independently of clusters.cpp.
        from math import comb, factorial
        catalans={n:comb(2*n,n)//(n+1) for n in range(3,10)}
        cs={}
        for n,av in catalans.items():
            cs[n]=factorial(n)-av-sum(comb(n,r)**2*factorial(n-r)*cs[r] for r in range(3,n))
        examples['123']={n:(cs[n],av) for n,av in catalans.items()}
        # Hook-length avoids transcription of small initial containment values.
        expected8={8:1,9:-16,10:153,11:-1140,12:7315,13:-42504,14:230230}
        av8={n:factorial(n)-sum(comb(n,r)**2*factorial(n-r)*expected8[r] for r in range(8,n+1)) for n in range(8,15)}
        require([av8[n] for n in (12,13,14)]==[476591309,6162155981,85494566892],'internal fixed hook-length values disagree')
        examples['12345678']={n:(expected8[n],av8[n]) for n in range(8,15)}
        for tau,expected in examples.items():
            out=subprocess.run([str(HERE/'clusters'),'6',tau],capture_output=True,text=True,check=True).stdout
            check_cluster_output(out,expected)
            print(f'{tau}: {len(expected)} complete cluster/avoidance rows: PASS')

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.SubprocessError) as e:
        print(f'ERROR: {e}',file=sys.stderr); sys.exit(1)
