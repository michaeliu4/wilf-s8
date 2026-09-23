#!/usr/bin/env python3
"""Check malformed chi_components arguments and small exact valid cases."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import tempfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='chi-components-cli-') as tmp:
        exe = args.executable.resolve() if args.executable else Path(tmp) / 'chi_components'
        if args.executable is None:
            subprocess.run(['g++', '-std=c++17', '-O2', str(Path(__file__).with_name('chi_components.cpp')), '-o', str(exe)], check=True)
        invalid = [[], ['0'], ['0', '12', 'extra'], ['', '12'], ['junk', '12'],
                   ['1junk', '12'], ['-1', '12'], ['+1', '12'], [' 1', '12'],
                   ['1 ', '12'], ['1.0', '12'], ['9' * 200, '12'], ['13', '1'],
                   ['12', '1'], ['5', '12345678'], ['0', ''], ['0', '0'],
                   ['0', '11'], ['0', '13'], ['0', '01'], ['0', 'ab'],
                   ['0', '123456788'], ['0', '1234567890'], ['0', '1' * 10000], ['0', '１２']]
        for case in invalid:
            run = subprocess.run([str(exe), *case], text=True, capture_output=True, timeout=10)
            if run.returncode <= 0 or run.stdout or not run.stderr:
                raise RuntimeError(f'Invalid-input failure: {case!r}: {run.returncode}, {run.stdout!r}, {run.stderr!r}')
        # For k=0 the sole containing permutation is tau, giving one vertex.
        cases = [('0', '1', 1, 1, ' f0=1'), ('0', '21', 1, 1, ' f0=1'),
                 ('0', '231', 1, 1, ' f0=1'), ('0', '2413', 1, 1, ' f0=1'),
                 # Each S2 permutation has two vertices and one edge for tau=1.
                 ('1', '1', 2, 2, ' f0=4 f1=2'),
                 # The five S3 permutations containing 12 have nine occurrences
                 # and four one-dimensional cells in total.
                 ('1', '12', 5, 5, ' f0=9 f1=4')]
        for k, pattern, containing, classes, cells in cases:
            run = subprocess.run([str(exe), k, pattern], text=True, capture_output=True, timeout=10, check=True)
            expected = (f'tau={pattern} k={k} n={len(pattern) + int(k)}  rho containing tau: {containing}  '
                        f'classes total: {classes}  rho with a class of chi!=1: 0  '
                        f'rho with chi!=beta0: 0  cells:{cells}\n')
            if run.stdout != expected or run.stderr:
                raise RuntimeError(f'Unexpected valid output: {run.stdout!r}; expected {expected!r}')
        print(f'chi_components CLI: {len(invalid)} invalid inputs rejected; {len(cases)} exact valid-input cases passed.')


if __name__ == '__main__':
    main()
