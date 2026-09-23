#!/usr/bin/env python3
"""Read-only validation of the sparse S8 classification certificate and coverage."""
from __future__ import annotations
from collections import Counter, defaultdict
import csv, math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]

def require(ok: bool, message: str) -> None:
    if not ok: raise ValueError(message)

def main() -> None:
    classes=[line.split() for line in (ROOT/'data/known_classes8.txt').read_text().splitlines() if line.strip()]
    require(len(classes)==4755,'wrong number of theorem-generated classes')
    members=[t for group in classes for t in group]
    require(len(members)==len(set(members))==math.factorial(8),'class list does not partition S8')
    require(all(sorted(t)==list('12345678') for t in members),'invalid member of S8')
    require(all(group==sorted(group) for group in classes),'class members must be sorted')
    expected_sizes={2:29,4:260,8:4094,12:10,16:309,18:1,20:1,24:39,32:9,40:1,48:1,56:1}
    require(Counter(map(len,classes))==expected_sizes,'class-size distribution differs')
    with (ROOT/'data/S8_classes.csv').open(newline='') as f: rows=list(csv.DictReader(f))
    require(len(rows)==4755,'wrong certificate row count')
    identities=0
    for cid,(row,group) in enumerate(zip(rows,classes),1):
        require((int(row['class_id']),int(row['size']),row['representative'])==(cid,len(group),group[0]),'certificate/class mismatch')
        require(row['c8']=='1' and row['c9']=='-16','wrong universal initial cluster value')
        c={}; ended=False
        for n in range(8,15):
            x,y=row[f'c{n}'],row[f'Av{n}']
            require(bool(x)==bool(y),'cluster and avoidance coverage differs')
            if not x: ended=True; continue
            require(not ended,'non-prefix sparse row')
            c[n]=int(x); av=int(y)
            require(0<=av<=math.factorial(n),'avoidance count out of range')
            calculated=math.factorial(n)-sum(math.comb(n,r)**2*math.factorial(n-r)*c[r] for r in range(8,n+1))
            require(av==calculated,f'cluster transform failed at {group[0]}, n={n}')
            identities+=1
        require(12 in c,'all representatives need values through n=12')
    groups=[rows]; cutoffs={}; refinements=[]
    for n,expected in zip(range(9,15),(1,8,256,4210,4751,4755)):
        new=[]
        for group in groups:
            if len(group)==1:new.append(group);continue
            bins=defaultdict(list)
            for row in group:
                require(bool(row[f'c{n}']),f'missing value in unresolved group at n={n}')
                bins[int(row[f'c{n}'])].append(row)
            new.extend(bins.values())
        groups=new; refinements.append(len(groups))
        require(len(groups)==expected,f'wrong refinement at n={n}')
        for group in groups:
            if len(group)==1: cutoffs.setdefault(group[0]['representative'],n)
        if n==12:
            require(sum(len(g)==1 for g in groups)==3720,'wrong number of n12 singleton groups')
    require(len(cutoffs)==4755,'not all classes separated')
    require(all(cutoffs[r['representative']]==int(r['cutoff']) for r in rows),'incorrect separating cutoff')
    print(f'PASS: {len(members)} permutations partitioned into {len(classes)} classes')
    print(f'PASS: {identities} exact cluster/avoidance identities')
    print('PASS: refinement '+', '.join(map(str,refinements))+'; all cutoffs and class sizes checked')
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError) as e:
        print(f'ERROR: {e}',file=sys.stderr);sys.exit(1)
