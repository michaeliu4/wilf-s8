#!/usr/bin/env python3
"""Compare the present S_8 certificate (data/S8_classes.csv, data/known_classes8.txt) with the earlier certificate
of the same research programme (reference/archive_stage1_S8/), computed by two different algorithms
(D4-weighted distinct-subpattern counts for n <= 12; prefix/tail bitmap unions for n = 13, 14).
Checks: same representatives, identical class membership, identical counts for every certificate entry present on both
sides, and identical counts for all 40,320 patterns at n = 9..12 (class representative value vs archived per-pattern value)."""
import csv, os, sys
from math import factorial
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.join(here,'..')
arch=os.path.join(root,'reference','archive_stage1_S8')
mine={r['representative']:r for r in csv.DictReader(open(os.path.join(root,'data','S8_classes.csv')))}
myclasses={}; rep_of={}
for line in open(os.path.join(root,'data','known_classes8.txt')):
    p=line.split(); myclasses[p[0]]=frozenset(p)
    for t in p: rep_of[t]=p[0]
A=list(csv.DictReader(open(os.path.join(arch,'class_representatives.csv'))))
memb={}
for r in csv.DictReader(open(os.path.join(arch,'class_membership.csv'))):
    memb.setdefault(r['representative'],set()).add(r['pattern'])
nrep=sum(1 for r in A if r['representative'] in mine)
nsame=sum(1 for r in A if frozenset(memb[r['representative']])==myclasses.get(r['representative']))
print("archived classes:",len(A),"present classes:",len(mine))
print("archived representatives that are present representatives:",nrep)
print("classes with identical membership:",nsame)
bad0 = 0 if (len(A)==len(mine)==nrep==nsame) else 1
cmp=0; bad=0
for r in A:
    m=mine[r['representative']]
    for n in range(9,15):
        a=r[f'avoid_{n}']; b=m[f'Av{n}']
        if a=='' or b=='': continue
        cmp+=1
        if int(a)!=int(b): bad+=1; print("MISMATCH",r['representative'],n,a,b)
print("certificate entries compared:",cmp,"mismatches:",bad)
tot=0; bad2=0
for n in range(9,13):
    for r in csv.DictReader(open(os.path.join(arch,f'counts_{n}.csv'))):
        tot+=1
        if int(r[f'avoids_{n}'])!=int(mine[rep_of[r['pattern']]][f'Av{n}']): bad2+=1
print("per-pattern counts compared (all 40320 patterns, n=9..12):",tot,"mismatches:",bad2)

fails = [v for k,v in globals().items() if k.startswith("bad") and isinstance(v,int)]
sys.exit(1 if any(fails) else 0)
