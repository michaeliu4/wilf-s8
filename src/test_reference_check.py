#!/usr/bin/env python3
"""Negative regression tests for the shared-counter/appendix reference defect.
Build the manuscript first. All malformed aux copies must be rejected.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

R = Path(__file__).resolve().parents[1]
checker = R/'src/check_latex_references.py'
original = (R/'manuscript/main.aux').read_text()

def run(aux):
    return subprocess.run([sys.executable, str(checker), '--aux', str(aux)], capture_output=True, text=True)

if run(R/'manuscript/main.aux').returncode:
    raise SystemExit('FAIL: baseline references must pass before negative tests')
tests = {'lem:run': 'lemma', 'def:return': 'definition', 'prop:k5': 'proposition',
         'cor:LIS': 'corollary', 'app:layered': 'appendix'}
with tempfile.TemporaryDirectory() as name:
    aux = Path(name)/'main.aux'
    for label, kind in tests.items():
        before = '\\newlabel{'+label+'@cref}{{['+kind+']'
        after = '\\newlabel{'+label+'@cref}{{['+('section' if kind=='appendix' else 'theorem')+']'
        if original.count(before) != 1:
            raise SystemExit(f'FAIL: cannot identify unique test label {label}')
        aux.write_text(original.replace(before, after))
        result = run(aux)
        if result.returncode == 0 or label not in result.stderr:
            raise SystemExit(f'FAIL: erroneous reference type accepted for {label}')
    aux.write_text('\n'.join(line for line in original.splitlines() if not line.startswith('\\newlabel{lem:run@cref}')))
    if run(aux).returncode == 0:
        raise SystemExit('FAIL: missing reference record accepted')
    duplicate = next(line for line in original.splitlines() if line.startswith('\\newlabel{lem:run@cref}'))
    aux.write_text(original+'\n'+duplicate+'\n')
    if run(aux).returncode == 0:
        raise SystemExit('FAIL: duplicate reference record accepted')
print('PASS: 7 negative reference regressions rejected (5 wrong types, missing, duplicate).')
