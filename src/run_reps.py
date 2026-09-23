#!/usr/bin/env python3
"""Run ./clusters K tau for every pattern in a list, in parallel, resumably.
Usage: run_reps.py K listfile outfile [workers]
Output lines: tau  c_a ... c_{a+K}  |  Av_a ... Av_{a+K}
"""
import sys, subprocess, os
from concurrent.futures import ThreadPoolExecutor
K=int(sys.argv[1]); lst=sys.argv[2]; out=sys.argv[3]; W=int(sys.argv[4]) if len(sys.argv)>4 else 2
here=os.path.dirname(os.path.abspath(__file__))
done=set()
if os.path.exists(out):
    for line in open(out):
        if line.strip(): done.add(line.split()[0])
todo=[l.split()[0] for l in open(lst) if l.strip() and l.split()[0] not in done]
def work(tau):
    r=subprocess.run([os.path.join(here,'clusters'),str(K),tau],capture_output=True,text=True,check=True)
    cs=[];avs=[]
    for line in r.stdout.splitlines():
        parts=dict(p.split('=') for p in line.split())
        cs.append(parts['c_r']); avs.append([v for k,v in parts.items() if k.startswith('Av_')][0])
    if len(cs) != K+1: raise ValueError('incomplete cluster output for '+tau)
    return tau, cs, avs
with ThreadPoolExecutor(max_workers=W) as ex, open(out,'a') as f:
    for tau,cs,avs in ex.map(work,todo):
        f.write(tau+' '+' '.join(cs)+' | '+' '.join(avs)+'\n'); f.flush()
