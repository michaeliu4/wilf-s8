#!/usr/bin/env python3
"""Reject malformed cluster CLI inputs and check unchanged valid-input behavior."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import tempfile
import re
import math


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='cluster-cli-') as tmp:
        exe = args.executable.resolve() if args.executable else Path(tmp) / 'clusters'
        if args.executable is None:
            subprocess.run(['g++', '-std=c++17', '-O2', str(Path(__file__).with_name('clusters.cpp')), '-o', str(exe)], check=True)
        invalid = [[], ['0'], ['0','12','-list','extra'], ['0','12','--unknown'],
                   ['nonsense','12'], ['1junk','12'], ['','12'], ['-1','12'], ['+1','12'],
                   [' 1','12'], ['1 ','12'], ['1.0','12'], ['9'*200,'12'],
                   ['15','1'], ['14','1'], ['7','12345678'],
                   ['0',''], ['0','0'], ['0','11'], ['0','13'], ['0','01'], ['0','ab'],
                   ['0','123456788'], ['0','1234567890'], ['0','1'*10000], ['0','１２']]
        for case in invalid:
            run = subprocess.run([str(exe), *case], text=True, capture_output=True, timeout=10)
            if run.returncode == 0 or run.returncode < 0 or run.stdout or not run.stderr:
                raise RuntimeError(f'Bad invalid-input behavior: {case!r}: {run.returncode}, {run.stdout!r}, {run.stderr!r}')
        # Output rows: size, signed cluster count, cluster count, avoidance count.
        for pattern in ['1','12','21','13426758','123456789']:
            run = subprocess.run([str(exe), '0', pattern], text=True, capture_output=True, timeout=10, check=True)
            match = re.fullmatch(r'r=(\d+) c_r=(-?\d+) clusters=(\d+) Av_(\d+)=(\d+)\n', run.stdout)
            expected = [len(pattern),1,1,len(pattern),math.factorial(len(pattern))-1]
            if match is None or [int(x) for x in match.groups()] != expected:
                raise RuntimeError(f'Unexpected K=0 output for {pattern}: {run.stdout!r}')
        listed = subprocess.run([str(exe), '0', '21', '-list'], text=True, capture_output=True, timeout=10, check=True)
        if listed.stdout.strip() != '2.1 1 0,1,':
            raise RuntimeError(f'Legacy -list output changed: {listed.stdout!r}')
        print(f'Cluster CLI: {len(invalid)} invalid inputs rejected; 6 valid-input cases passed.')

if __name__ == '__main__':
    main()
