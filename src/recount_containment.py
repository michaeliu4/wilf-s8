#!/usr/bin/env python3
"""Fresh containment recount with row-level evidence and fail-closed comparison.

Actual values come only from bruteforce_contain stdout. The certificate provides
comparison values, never a replacement for a computation. --resume validates
both the checkpoint and the certificate/source/executable identities.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv, hashlib, json, math
from pathlib import Path
import re, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]
HARD=('13426758','13427568','13678254','32718564','14567823','14567832','23815764','25876314')
FIELDS=('representative','n','g','avoidance','certificate_avoidance','status','seconds','stdout')
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def parse_counter(text: str, tau: str, n: int) -> tuple[int,int]:
    m=re.fullmatch(r'tau=(\d+) n=(\d+) g_(\d+)=(\d+) Av_(\d+)=(\d+)\s*',text)
    if not m or m[1]!=tau or int(m[2])!=n or int(m[3])!=n-len(tau) or int(m[5])!=n:
        raise ValueError(f'malformed or wrong-scope output for {tau}, n={n}: {text!r}')
    g,av=int(m[4]),int(m[6])
    if min(g,av)<0 or g+av!=math.factorial(n):raise ValueError('complement identity failed')
    return g,av

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate',type=Path,default=ROOT/'data/S8_classes.csv')
    ap.add_argument('--counter',type=Path,default=ROOT/'src/bruteforce_contain')
    ap.add_argument('--output',type=Path,default=ROOT/'checks/bruteforce_all_n12.csv')
    ap.add_argument('--scope',choices=('all','hardest'),default='all')
    ap.add_argument('--n',type=int,nargs='+',default=(11,12))
    ap.add_argument('--jobs',type=int,default=1)
    ap.add_argument('--resume',action='store_true')
    args=ap.parse_args()
    if args.jobs<1 or len(set(args.n))!=len(args.n) or any(not 8<=n<=14 for n in args.n):
        ap.error('jobs must be positive; n must be distinct integers in [8,14]')
    with args.certificate.open(newline='') as f:rows=list(csv.DictReader(f))
    by_tau={r['representative']:r for r in rows}
    if len(rows)!=4755 or len(by_tau)!=4755:raise ValueError('expected 4,755 distinct representatives')
    reps=sorted(by_tau) if args.scope=='all' else list(HARD)
    requested=[(t,n) for t in reps for n in sorted(args.n)]
    expected={(t,n):int(by_tau[t][f'Av{n}']) for t,n in requested}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    meta_path=args.output.with_suffix('.metadata.json')
    metadata={'schema':1,'source_sha256':sha(ROOT/'src/bruteforce_contain.cpp'),
              'executable_sha256':sha(args.counter),'certificate_sha256':sha(args.certificate),
              'scope':args.scope,'n':sorted(args.n),'rows_expected':len(requested)}
    complete={}
    if args.resume and args.output.exists():
        if not meta_path.exists() or json.loads(meta_path.read_text())!=metadata:raise ValueError('resume identity mismatch')
        with args.output.open(newline='') as f:
            for r in csv.DictReader(f):
                key=(r['representative'],int(r['n']))
                if key not in expected or key in complete:raise ValueError('duplicate/out-of-scope row')
                g,av=parse_counter(r['stdout'],*key)
                if av!=expected[key] or r['status']!='PASS' or int(r['g'])!=g or int(r['avoidance'])!=av or int(r['certificate_avoidance'])!=av:
                    raise ValueError('invalid checkpoint row')
                complete[key]=r
    elif args.output.exists():raise FileExistsError(f'{args.output} exists; use --resume or another path')
    else:meta_path.write_text(json.dumps(metadata,indent=2)+'\n')
    def run(key: tuple[str,int]) -> dict[str,str]:
        tau,n=key;t0=time.monotonic()
        proc=subprocess.run([str(args.counter.resolve()),str(n),tau],capture_output=True,text=True,check=True)
        g,av=parse_counter(proc.stdout,tau,n)
        return dict(zip(FIELDS,(tau,str(n),str(g),str(av),str(expected[key]),
                    'PASS' if av==expected[key] else 'MISMATCH',f'{time.monotonic()-t0:.6f}',proc.stdout.strip())))
    pending=[x for x in requested if x not in complete]
    mode='a' if args.output.exists() else 'w';t0=time.monotonic()
    with args.output.open(mode,newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS)
        if mode=='w':writer.writeheader();f.flush()
        with ThreadPoolExecutor(max_workers=args.jobs) as ex:
            futures={ex.submit(run,key):key for key in pending}
            for future in as_completed(futures):
                key=futures[future];row=future.result();writer.writerow(row);f.flush()
                if row['status']!='PASS':
                    for todo in futures:todo.cancel()
                    raise ValueError(f'mismatch: {row}')
                complete[key]=row
                if len(complete)%250==0:print(f'checked {len(complete)}/{len(requested)} rows',flush=True)
    if set(complete)!=set(requested):raise ValueError('incomplete coverage')
    temp=args.output.with_suffix('.tmp')
    with temp.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(complete[k] for k in requested)
    temp.replace(args.output)
    summary=f'representatives: {len(reps)}; n={sorted(args.n)}; rows: {len(complete)}; mismatches: 0; fresh rows this run: {len(pending)}; elapsed seconds: {time.monotonic()-t0:.3f}'
    args.output.with_suffix('.summary.txt').write_text(summary+'\n');print(summary)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);sys.exit(1)
