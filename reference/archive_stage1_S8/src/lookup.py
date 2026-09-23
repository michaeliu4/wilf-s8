#!/usr/bin/env python3
"""Look up an S_8 Wilf class, an equivalence path, or an inequivalence witness."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def read(name):
    with (ROOT/name).open(newline='') as f:
        return list(csv.DictReader(f))

def pattern(value):
    if len(value) != 8 or set(value) != set('12345678'):
        raise argparse.ArgumentTypeError('use a permutation of 12345678, e.g. 13426758')
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sigma', type=pattern)
    parser.add_argument('tau', nargs='?', type=pattern)
    args = parser.parse_args()
    rows = read('class_membership.csv')
    by_pattern = {row['pattern']: row for row in rows}
    by_rank = {int(row['lex_rank']): row for row in rows}
    a = by_pattern[args.sigma]
    if args.tau is None:
        print(f"Class {a['class_id']}: representative {a['representative']}, size {a['class_size']}")
        print('Members:', ', '.join(row['pattern'] for row in rows if row['class_id'] == a['class_id']))
        return
    b = by_pattern[args.tau]
    if a['class_id'] != b['class_id']:
        representatives = {row['class_id']: row for row in read('class_representatives.csv')}
        x, y = representatives[a['class_id']], representatives[b['class_id']]
        for n in range(9, 15):
            u, v = x[f'avoid_{n}'], y[f'avoid_{n}']
            if u and v and u != v:
                print(f'INEQUIVALENT; first differing length is {n}.')
                print(f"a_{n}({args.sigma}) = {int(u):,}")
                print(f"a_{n}({args.tau}) = {int(v):,}")
                print(f"Classes {a['class_id']} and {b['class_id']}.")
                return
        raise AssertionError('No common numerical witness: corrupt or incomplete certificate')
    print(f"WILF-EQUIVALENT for every n; class {a['class_id']}, representative {a['representative']}.")
    forest = {int(row['rank']): row for row in read('equivalence_forest.csv')}
    def chain(rank):
        result = [rank]
        while int(forest[result[-1]]['parent_rank']) >= 0:
            result.append(int(forest[result[-1]]['parent_rank']))
        return result
    left, right = chain(int(a['lex_rank'])), chain(int(b['lex_rank']))
    right_set = set(right)
    common = next(rank for rank in left if rank in right_set)
    left = left[:left.index(common)+1]
    right = right[:right.index(common)+1]
    path = left + list(reversed(right[:-1]))
    print('Equivalence path:')
    print('  ' + by_rank[path[0]]['pattern'])
    for u, v in zip(path, path[1:]):
        label = forest[u]['edge_rule'] if int(forest[u]['parent_rank']) == v else forest[v]['edge_rule']
        print(f"  --[{label}]-- {by_rank[v]['pattern']}")

if __name__ == '__main__':
    main()
