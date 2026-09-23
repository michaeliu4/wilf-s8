#!/usr/bin/env python3
"""Validate retained actual recount rows without claiming a fresh enumeration."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from pathlib import Path
from recount_containment import HARD, parse_counter
ROOT=Path(__file__).resolve().parents[1]

def require(ok: bool, message: str) -> None:
    if not ok: raise ValueError(message)

def check_csv(path: Path, certificate: Path) -> int:
    with certificate.open(newline='') as f: certrows=list(csv.DictReader(f))
    cert={r['representative']:r for r in certrows}
    require(len(certrows)==len(cert)==4755,'certificate coverage must be exactly 4,755 representatives')
    expected={(t,n) for t in cert for n in (11,12)}; seen=set()
    with path.open(newline='') as f:
        for r in csv.DictReader(f):
            key=(r['representative'],int(r['n']))
            require(key in expected and key not in seen,'duplicate or out-of-scope row')
            g,av=parse_counter(r['stdout'],*key)
            require(g==int(r['g']) and av==int(r['avoidance']),'stored value differs from raw stdout')
            require(av==int(r['certificate_avoidance'])==int(cert[key[0]][f'Av{key[1]}']),'recount/certificate mismatch')
            require(r['status']=='PASS','row does not report PASS')
            seen.add(key)
    require(seen==expected,f'incomplete recount: {len(seen)}/{len(expected)} rows')
    return len(seen)

def check_legacy(path: Path, certificate: Path) -> int:
    with certificate.open(newline='') as f: cert={r['representative']:r for r in csv.DictReader(f)}
    expected={(t,n) for t in HARD for n in (13,14)}; seen=set()
    for line in path.read_text().splitlines():
        if line=='brute-force counts compared with the certificate: 16 values, 0 mismatches':continue
        m=re.match(r'tau=(\d+) n=(\d+) ',line)
        require(m is not None,f'malformed legacy row: {line!r}')
        key=(m[1],int(m[2])); require(key in expected and key not in seen,'legacy coverage error')
        g,av=parse_counter(line,*key)
        require(av==int(cert[key[0]][f'Av{key[1]}']),'legacy comparison failed'); seen.add(key)
    require(seen==expected,'incomplete legacy hardest-pair log')
    return len(seen)

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--csv',type=Path,default=ROOT/'checks/bruteforce_all_n12.csv')
    ap.add_argument('--certificate',type=Path,default=ROOT/'data/S8_classes.csv')
    args=ap.parse_args()
    print(f'PASS: {check_csv(args.csv,args.certificate)} retained row-level recount values; not a fresh enumeration')
    if args.csv==ROOT/'checks/bruteforce_all_n12.csv':
        meta=json.loads(args.csv.with_suffix('.metadata.json').read_text())
        for k,p in [('certificate_sha256',args.certificate),('source_sha256',ROOT/'src/bruteforce_contain.cpp')]:
            require(meta[k]==hashlib.sha256(p.read_bytes()).hexdigest(),f'{k} differs from recorded recount input')
        print('PASS: recorded source and certificate hashes match')
    n=check_legacy(ROOT/'checks/bruteforce_hardest.txt',args.certificate)
    print(f'PASS: {n} inherited n=13,14 values; inspected/comparison-checked, not freshly recounted')
if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,OSError) as e:
        print(f'ERROR: {e}',file=sys.stderr); sys.exit(1)
