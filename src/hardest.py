#!/usr/bin/env python3
"""Print the groups of S_8 classes that are not separated by |Av_n| for n <= 13, with their full class lists,
cluster numbers c_8..c_14 and |Av_n| for n = 13, 14 (from data/S8_classes.csv)."""
import csv, os
here=os.path.dirname(os.path.abspath(__file__)); data=os.path.join(here,'..','data')
classes={l.split()[0]: l.split() for l in open(os.path.join(data,'known_classes8.txt'))}
rows=list(csv.DictReader(open(os.path.join(data,'S8_classes.csv'))))
from collections import defaultdict
g=defaultdict(list)
for r in rows:
    key=tuple(r[f'c{i}'] for i in range(8,14))
    g[key].append(r)
groups=[v for v in g.values() if len(v)>1]
print(f"{len(groups)} groups not separated at n<=13")
for grp in groups:
    print("group: shared c_8..c_13 =", ' '.join(grp[0][f'c{i}'] for i in range(8,14)))
    for r in grp:
        print(f"  class {r['class_id']} (size {r['size']}): rep {r['representative']}  c14={r['c14']}  Av13={r['Av13']}  Av14={r['Av14']}  cutoff={r['cutoff']}")
        print("     members:", ' '.join(classes[r['representative']]))
