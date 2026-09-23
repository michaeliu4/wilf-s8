#!/usr/bin/env python3
"""Assemble data/S8_classes.csv from the class list and the cluster-number sweeps, and print the
refinement numbers (classes distinguished by |Av_t|, t <= n) and the separation certificate.
Inputs (in data/): known_classes8.txt (one class per line), reps8_K4.txt (c_8..c_12 for every representative),
unsep12_K5.txt (c_8..c_13 for the representatives not separated at n<=12), unsep13_K6.txt (c_8..c_14 for
those not separated at n<=13).  Output columns: class_id, size, representative, c8..c14, Av8..Av14, cutoff."""
import os, sys, hashlib
from collections import defaultdict
from math import factorial, comb
here=os.path.dirname(os.path.abspath(__file__)); data=os.path.join(here,'..','data')
def load(fn):
    d={}
    p=os.path.join(data,fn)
    if not os.path.exists(p): raise FileNotFoundError(p)
    for line in open(p):
        parts=line.split()
        if not parts: continue
        bar=parts.index('|')
        if parts[0] in d: raise ValueError('duplicate sweep representative: '+parts[0])
        d[parts[0]]=[int(x) for x in parts[1:bar]]
    return d
K4=load('reps8_K4.txt'); K5=load('unsep12_K5.txt'); K6=load('unsep13_K6.txt')
classes=[l.split() for l in open(os.path.join(data,'known_classes8.txt'))]
if (len(K4),len(K5),len(K6),len(classes)) != (4755,1035,8,4755):
    raise ValueError('incomplete input coverage')
rows=[]
for cid,c in enumerate(classes,1):
    rep=c[0]
    cs=K6.get(rep) or K5.get(rep) or K4.get(rep)
    rows.append([cid,len(c),rep,cs])
def av(cs,n):  # |Av_n| from cluster numbers c_8..c_{n}
    a=8; k=n-a; g=sum(comb(n,r)**2*factorial(n-r)*cs[r-a] for r in range(a,n+1)); return factorial(n)-g
# refinement numbers and cutoff per class
maxn=14
keys={}
for n in range(9,maxn+1):
    groups=defaultdict(list)
    for r in rows:
        cs=r[3]
        if cs is None or len(cs)<n-8+1: key=('NA',)+tuple(r[3][:min(len(r[3]),n-7)]) if r[3] else ('NA',)
        else: key=tuple(cs[:n-7])
        groups[key].append(r[0])
    keys[n]=groups
    print(f"n<={n}: {len(groups)} groups")
cutoff={}
for r in rows:
    cid=r[0]; cutoff[cid]=None
    for n in range(9,maxn+1):
        g=[g for g in keys[n].values() if cid in g][0]
        if len(g)==1: cutoff[cid]=n; break
missing=[r[2] for r in rows if cutoff[r[0]] is None]
print("classes not yet separated:",len(missing), missing[:20])
if missing or [len(keys[n]) for n in range(9,15)] != [1,8,256,4210,4751,4755]:
    raise ValueError('certificate refinement or separation failed; refusing to overwrite')
out=os.path.join(data,'S8_classes.csv')
with open(out,'w') as f:
    f.write('class_id,size,representative,'+','.join(f'c{r}' for r in range(8,15))+','+','.join(f'Av{n}' for n in range(8,15))+',cutoff\n')
    for r in rows:
        cs=r[3] or []
        cvals=[str(cs[i]) if i<len(cs) else '' for i in range(7)]
        avs=[str(av(cs,n)) if n-8<len(cs) else '' for n in range(8,15)]
        f.write(f"{r[0]},{r[1]},{r[2]},"+','.join(cvals)+','+','.join(avs)+f",{cutoff[r[0]] or ''}\n")
h=hashlib.sha256(open(out,'rb').read()).hexdigest()
print("wrote",out,"sha256",h)
