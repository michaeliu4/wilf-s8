#!/usr/bin/env python3
"""Read-only verification of every S8 provenance edge and rooted class tree.

This independently checks the stated local move, not a regenerated BFS order.
It checks the recorded use of the theorems; it does not prove those theorems.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HEADER = re.compile(r'class ([1-9][0-9]*) size ([1-9][0-9]*) rep ([1-8]{8})')
EDGE = re.compile(r'  ([1-8]{8}) <- ([1-8]{8}) via (SYM:[rci]|BWX:[2-7]|SW)')


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def apply_move(parent: str, label: str) -> str:
    p = tuple(map(int, parent))
    if label == 'SYM:r':
        q = p[::-1]
    elif label == 'SYM:c':
        q = tuple(9 - x for x in p)
    elif label == 'SYM:i':
        q = tuple(p.index(x) + 1 for x in range(1, 9))
    else:
        k = int(label[4:]) if label.startswith('BWX:') else 3
        lo = tuple(range(1, k + 1)) if label.startswith('BWX:') else (2, 3, 1)
        hi = lo[::-1] if label.startswith('BWX:') else (3, 1, 2)
        require(p[:k] in (lo, hi), f'{label} has no admissible direct-sum prefix in {parent}')
        # The prefix is exactly [k]; permutation validity then ensures that the
        # unchanged, nonempty suffix has values k+1,...,8 (the right extension).
        q = (hi if p[:k] == lo else lo) + p[k:]
    return ''.join(map(str, q))


def validate(provenance: Path, classes_path: Path) -> tuple[int, int]:
    groups = [line.split() for line in classes_path.read_text().splitlines() if line.strip()]
    members = [p for group in groups for p in group]
    require(len(groups) == 4755, 'expected 4755 class blocks')
    require(len(members) == len(set(members)) == math.factorial(8), 'classes do not partition S8')
    require(all(sorted(p) == list('12345678') for p in members), 'invalid S8 member')
    require(all(group == sorted(group) for group in groups), 'class members are not sorted')
    require([g[0] for g in groups] == sorted(g[0] for g in groups), 'class representatives are not sorted')
    blocks: list[tuple[int, int, str, dict[str, str]]] = []
    for lineno, line in enumerate(provenance.read_text().splitlines(), 1):
        header = HEADER.fullmatch(line)
        if header:
            cid, size, rep = header.groups()
            blocks.append((int(cid), int(size), rep, {}))
            continue
        edge = EDGE.fullmatch(line)
        require(edge is not None and bool(blocks), f'line {lineno}: malformed or unowned edge')
        child, parent, label = edge.groups()
        cid, _, rep, parents = blocks[-1]
        require(sorted(child) == sorted(parent) == list('12345678'), f'line {lineno}: invalid permutation')
        require(child != rep, f'class {cid}: root has a parent')
        require(child not in parents, f'class {cid}: duplicate parent for {child}')
        require(apply_move(parent, label) == child, f'line {lineno}: incorrect {label} edge')
        parents[child] = parent
    require(len(blocks) == len(groups), 'wrong provenance block count')
    edges = 0
    for expected_id, (block, group) in enumerate(zip(blocks, groups), 1):
        cid, size, rep, parents = block
        require((cid, size, rep) == (expected_id, len(group), group[0]), f'block {expected_id}: header mismatch')
        expected = set(group)
        require(set(parents) == expected - {rep}, f'class {cid}: missing, extra or wrong-block children')
        require(set(parents.values()) <= expected, f'class {cid}: parent outside block')
        # Parent order is immaterial. Follow every chain to the declared root,
        # memoizing completed chains and detecting disconnected directed cycles.
        rooted = {rep}
        for child in parents:
            path = set()
            node = child
            while node not in rooted:
                require(node not in path, f'class {cid}: parent cycle at {node}')
                path.add(node)
                require(node in parents, f'class {cid}: unrooted path at {node}')
                node = parents[node]
            rooted.update(path)
        require(rooted == expected, f'class {cid}: root does not reach all members')
        edges += len(parents)
    return len(blocks), edges


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provenance', type=Path, default=ROOT / 'data/provenance8.txt')
    parser.add_argument('--classes', type=Path, default=ROOT / 'data/known_classes8.txt')
    args = parser.parse_args()
    blocks, edges = validate(args.provenance, args.classes)
    print(f'PASS: {edges} provenance moves; {blocks} class blocks with exactly one rooted, acyclic parent tree each')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
