#!/usr/bin/env python3
"""Recompute exact counts and compare to the delivered certificate.

Requires Python 3.9+ and g++ with C++17/OpenMP. No Python packages are needed.
Default: recompute the primary proof, including n=13 and n=14.
--smoke: only small-degree and compiler checks.
--extra: also repeat n=13 at width 7 and n=14 at width 6.
Outputs are written to build/; delivered data are never overwritten.
"""
from __future__ import annotations
import argparse
import csv
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=ROOT, check=True)

def table(path):
    with path.open(newline='') as f:
        return {int(row['rank']): row for row in csv.DictReader(f)}

def compare(generated, delivered, allow_subset=False):
    a, b = table(generated), table(delivered)
    if not allow_subset:
        assert set(a) == set(b), (generated, delivered, 'rank sets')
    for rank, row in a.items():
        assert rank in b and row == b[rank], (generated, rank, row, b.get(rank))
    print(f'MATCH: {generated.name}: {len(a)} rows', flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--extra', action='store_true')
    parser.add_argument('--native', action='store_true', help='enable compiler tuning for the current CPU')
    args = parser.parse_args()
    if not 1 <= args.threads <= 256:
        parser.error('--threads must lie between 1 and 256')
    build = ROOT/'build'
    build.mkdir(exist_ok=True)
    compiler = os.environ.get('CXX', 'g++')
    flags = ['-O3', '-std=c++17', '-fopenmp', '-Wall', '-Wextra']
    if args.native:
        flags += ['-march=native']
    for program in ('count_all', 'count_blocks'):
        run(compiler, *flags, ROOT/'src'/f'{program}.cpp', '-o', build/program)
    for n in ((9, 10, 11) if args.smoke else (9, 10, 11, 12)):
        output = build/f'counts_{n}.csv'
        run(build/'count_all', n, output, args.threads)
        compare(output, ROOT/'data'/f'counts_{n}.csv')
    for width in (5, 6, 7):
        output = build/f'blocks11_width{width}.csv'
        run(build/'count_blocks', 11, ROOT/'data'/'needed14_controls.txt', output, args.threads, width)
        compare(output, ROOT/'data'/'counts_11.csv', allow_subset=True)
    if not args.smoke:
        jobs = [(13, 6, 'needed13.txt', ROOT/'data'/'selected13.csv'),
                (14, 7, 'needed14_controls.txt', ROOT/'checks'/'selected14_w7.csv')]
        if args.extra:
            jobs += [(13, 7, 'needed13.txt', ROOT/'checks'/'blocks13_w7.csv'),
                     (14, 6, 'needed14.txt', ROOT/'data'/'selected14.csv')]
        for n, width, targets, reference in jobs:
            output = build/f'blocks{n}_width{width}.csv'
            run(build/'count_blocks', n, ROOT/'data'/targets, output, args.threads, width)
            compare(output, reference)
    run(sys.executable, ROOT/'src'/'validate.py')
    print('ALL REQUESTED RECOMPUTATIONS AND CERTIFICATE CHECKS PASSED.', flush=True)

if __name__ == '__main__':
    main()
