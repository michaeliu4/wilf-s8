#!/usr/bin/env python3
"""Check compiled reference types against environments in this manuscript.

This deliberately supports the single main.tex source, not arbitrary TeX macro
expansion. It checks every source label, all reference/citation keys, and refuses
missing, duplicate, or mistyped aux records. Run after a converged LaTeX build.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

TYPES = {'theorem','lemma','proposition','corollary','definition','remark',
         'conjecture','question','example'}
EQUATIONS = {'equation','align','gather','multline'}
EVENT = re.compile(r'\\(begin|end)\{([^}]+)\}|\\label(?:\[([^]]+)\])?\{([^}]+)\}|\\(section|subsection|subsubsection)(?![A-Za-z])')


def check(source: Path, auxiliary: Path) -> dict[str, int]:
    text = re.sub(r'(?<!\\)%[^\n]*', '', source.read_text())
    if re.search(r'\\(?:input|include)\s*\{', text):
        raise ValueError('external TeX source requires extending this checker')
    stack: list[str] = []
    section = 'section'
    expected: dict[str,str] = {}
    for event in EVENT.finditer(text):
        operation, env, explicit, label, sec = event.groups()
        if operation == 'begin':
            stack.append(env)
        elif operation == 'end':
            if not stack or stack.pop() != env:
                raise ValueError(f'unbalanced environment {env}')
        elif sec:
            section = sec
        elif label:
            kind = explicit
            if kind is None:
                for enclosing in reversed(stack):
                    if enclosing in TYPES:
                        kind = enclosing; break
                    if enclosing.rstrip('*') in EQUATIONS:
                        kind = 'equation'; break
                    if enclosing in {'table','figure'}:
                        kind = enclosing; break
                else:
                    kind = section
            if label in expected:
                raise ValueError(f'duplicate source label {label}')
            expected[label] = kind
    aux = auxiliary.read_text()
    records = re.findall(r'\\newlabel\{([^}]+)@cref\}\{\{\[([^]]+)\]', aux)
    actual: dict[str,str] = {}
    for label, kind in records:
        if label in actual:
            raise ValueError(f'duplicate compiled label {label}')
        actual[label] = kind
    if set(actual) != set(expected):
        raise ValueError(f'aux/source mismatch: missing {set(expected)-set(actual)}, extra {set(actual)-set(expected)}')
    for key, kind in expected.items():
        if actual[key] != kind:
            raise ValueError(f'{key}: expected {kind}, compiled as {actual[key]}')
    refs = re.findall(r'\\(?:[Cc]ref|eqref|ref)\*?\{([^}]+)\}', text)
    for group in refs:
        for key in group.split(','):
            if key.strip() not in expected:
                raise ValueError(f'undefined reference {key}')
    bibkeys = re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}', text)
    if len(bibkeys) != len(set(bibkeys)):
        raise ValueError('duplicate bibliography key')
    citations = re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}', text)
    for group in citations:
        for key in group.split(','):
            if key.strip() not in bibkeys:
                raise ValueError(f'undefined citation {key}')
    return dict(Counter(expected.values()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parents[1]/'manuscript'
    parser.add_argument('--source', type=Path, default=base/'main.tex')
    parser.add_argument('--aux', type=Path, default=base/'main.aux')
    args = parser.parse_args()
    try:
        result = check(args.source, args.aux)
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
    print('PASS: all', sum(result.values()), 'compiled reference types agree with source environments.')
    print('Types:', dict(sorted(result.items())))
    print('All internal reference keys and bibliography citation keys resolve.')


if __name__ == '__main__':
    main()
