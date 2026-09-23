#!/usr/bin/env python3
"""Cross-check of the S_8 sweep: for N classes (all classes that contain a Backelin-West-Xin or Stankova-West move
in the provenance tree, plus random others), compute the cluster numbers c_8..c_12 of a SECOND member of the class
with src/clusters and compare with the representative's numbers in data/reps8_K4.txt.  Usage: second_member.py N"""
import sys, os, random, subprocess
here=os.path.dirname(os.path.abspath(__file__)); data=os.path.join(here,'..','data')
N=int(sys.argv[1]) if len(sys.argv)>1 else 40
rep={}
for line in open(os.path.join(data,'reps8_K4.txt')):
    p=line.split(); rep[p[0]]=p[1:p.index('|')]
# parse provenance: classes with a BWX or SW move, and the member reached by that move
cls=None; cand=[]; allc={}
for line in open(os.path.join(data,'provenance8.txt')):
    p=line.split()
    if p[0]=='class': cls=p[5]; allc[cls]=[]
    else:
        allc[cls].append(p[0])
        if p[4].startswith('BWX') or p[4]=='SW': cand.append((cls,p[0],p[4]))
random.seed(1)
random.shuffle(cand)
chosen=cand[:N*3//4]
others=[c for c in allc if allc[c]]
random.shuffle(others)
for c in others:
    if len(chosen)>=N: break
    if all(c!=x[0] for x in chosen): chosen.append((c,random.choice(allc[c]),'SYM'))
bad=0
for cls,member,move in chosen:
    r=subprocess.run([os.path.join(here,'clusters'),'4',member],capture_output=True,text=True)
    cs=[l.split()[1].split('=')[1] for l in r.stdout.splitlines() if l.startswith('r=')]
    ok = cs==rep[cls]
    bad+= (not ok)
    print(f"class rep {cls}  member {member} ({move}): c_8..c_12 = {' '.join(cs)}  {'OK' if ok else 'MISMATCH'}")
print(f"{len(chosen)} classes checked, {bad} mismatches")
