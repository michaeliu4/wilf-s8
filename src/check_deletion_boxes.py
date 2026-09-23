#!/usr/bin/env python3
"""Check the deletion-overlap formula (deletion_boxes.py, the deletion-overlap theorem of the manuscript) against the cluster values
of g_3: all patterns of length 4 and 5 (data/clusters_len*.txt) and all class representatives of lengths 6, 7
(data/reps6_K5.txt, data/reps7_K5.txt).  For the 4,755 representatives of length 8 use the C++ evaluator:
   g++ -O2 -std=c++17 -o dbox deletion_boxes.cpp && ./dbox reps8_semicolon.txt out.csv   (11 s)
Usage: check_deletion_boxes.py"""
import os, sys
from math import factorial
here=os.path.dirname(os.path.abspath(__file__)); data=os.path.join(here,'..','data')
sys.path.insert(0,here)
import deletion_boxes as db
tests=[]
for a in (4,5):
    for line in open(os.path.join(data,f'clusters_len{a}.txt')):
        if line.startswith('#') or not line.strip(): continue
        p=line.split(); vals=[int(x) for x in p[1:]]
        tests.append((p[0], factorial(a+3)-vals[1+4+2]))
for a,fn in ((6,'reps6_K5.txt'),(7,'reps7_K5.txt')):
    for line in open(os.path.join(data,fn)):
        p=line.split()
        if '|' not in p: continue
        avs=[int(x) for x in p[p.index('|')+1:]]
        tests.append((p[0], factorial(a+3)-avs[3]))
bad=0
for tau,g3 in tests:
    v=db.g3([int(c) for c in tau])
    if v!=g3: bad+=1; print("MISMATCH",tau,v,g3)
print("patterns compared:",len(tests),"mismatches:",bad)
sys.exit(1 if bad else 0)
