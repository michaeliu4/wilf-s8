#!/usr/bin/env python3
"""Partition S_m by explicit, proved Wilf-equivalence generators.

Entries use 0-based values internally, one-line 1-based strings in output.
The generators are D4 symmetries; iota_k (+) gamma <-> delta_k (+) gamma;
and 231 (+) gamma <-> 312 (+) gamma.  At m=4 only, include 1342 <-> 2413.
"""
import itertools, collections, json, csv, pathlib, sys

class DSU:
    def __init__(self,n): self.p=list(range(n))
    def find(self,a):
        while self.p[a]!=a:
            self.p[a]=self.p[self.p[a]];a=self.p[a]
        return a
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b:self.p[max(a,b)]=min(a,b)

def inverse(p):
    q=[0]*len(p)
    for i,x in enumerate(p):q[x]=i
    return tuple(q)

def classify(n, out=None):
    perms=list(itertools.permutations(range(n)));ids={p:i for i,p in enumerate(perms)}
    sym=DSU(len(perms));eq=DSU(len(perms));edges=[]
    def join(a,b,rule):
        eq.union(a,b)
        if a<b:edges.append((a,b,rule))
    for a,p in enumerate(perms):
        for q,r in [(p[::-1],'reverse'),(tuple(n-1-x for x in p),'complement'),(inverse(p),'inverse')]:
            b=ids[q];sym.union(a,b);join(a,b,r)
        for k in range(2,n+1):
            if p[:k]==tuple(range(k)):
                q=tuple(range(k-1,-1,-1))+p[k:];join(a,ids[q],f'BWX_{k}')
        if p[:3]==(1,2,0):join(a,ids[(2,0,1)+p[3:]],'SW_231_312')
    if n==4:join(ids[(0,2,3,1)],ids[(1,3,0,2)],'Stankova_sporadic')
    sc=collections.defaultdict(list);ec=collections.defaultdict(list)
    for a,p in enumerate(perms):sc[sym.find(a)].append(a);ec[eq.find(a)].append(a)
    text=lambda p:''.join(str(x+1) for x in p)
    result={'m':n,'symmetry_classes':len(sc),'proved_components':len(ec),'component_size_distribution':dict(sorted(collections.Counter(map(len,ec.values())).items()))}
    print(json.dumps(result),flush=True)
    if out:
        out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
        with open(out/f'classes_{n}.csv','w') as f:
            w=csv.writer(f);w.writerow(['rank','pattern','symmetry_representative_rank','symmetry_orbit_size','proved_component_representative_rank'])
            for a,p in enumerate(perms):w.writerow([a,text(p),sym.find(a),len(sc[sym.find(a)]),eq.find(a)])
        with open(out/f'equivalence_edges_{n}.csv','w') as f:
            w=csv.writer(f);w.writerow(['rank_a','rank_b','theorem_or_symmetry']);w.writerows(edges)
        (out/f'classes_summary_{n}.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else None
    for n in range(3,9):classify(n,out)
