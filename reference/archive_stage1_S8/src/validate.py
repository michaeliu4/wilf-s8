#!/usr/bin/env python3
"""Audit the S_8 Wilf-classification certificate using only Python's stdlib.

This rebuilds the graph independently of generate_components.py, validates
all membership/equivalence certificates, and checks the numerical separation.
It does not pretend to re-enumerate S_14: use reproduce.py to recompute counts.
Run from any directory. --write regenerates the human-readable certificates.
"""
from __future__ import annotations
import argparse
import collections
import csv
import functools
import io
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = 8
PERMS = list(itertools.permutations(range(M)))
INDEX = {p: i for i, p in enumerate(PERMS)}

def text(p):
    return ''.join(str(x + 1) for x in p)

def neighbors(p):
    """Generate BOTH directions of precisely the stated, proved graph rules."""
    yield p[::-1], 'reverse'
    yield tuple(M - 1 - x for x in p), 'complement'
    inv = [0] * M
    for i, x in enumerate(p):
        inv[x] = i
    yield tuple(inv), 'inverse'
    for k in range(2, M + 1):
        inc, dec = tuple(range(k)), tuple(range(k - 1, -1, -1))
        if p[:k] == inc:
            yield dec + p[k:], f'BWX_{k}'
        if p[:k] == dec:
            yield inc + p[k:], f'BWX_{k}'
    if p[:3] == (1, 2, 0):
        yield (2, 0, 1) + p[3:], 'SW_231_312'
    if p[:3] == (2, 0, 1):
        yield (1, 2, 0) + p[3:], 'SW_231_312'

def graph_components():
    """BFS, not the union-find implementation used in the discovery run."""
    rep = [-1] * len(PERMS)
    parent, rule, components = {}, {}, {}
    for root in range(len(PERMS)):
        if rep[root] != -1:
            continue
        rep[root] = root
        parent[root], rule[root] = -1, 'root'
        queue = collections.deque([root])
        members = []
        while queue:
            a = queue.popleft()
            members.append(a)
            for b, label in sorted((INDEX[q], label) for q, label in neighbors(PERMS[a])):
                if rep[b] == -1:
                    rep[b], parent[b], rule[b] = root, a, label
                    queue.append(b)
                else:
                    assert rep[b] == root
        components[root] = sorted(members)
    return rep, parent, rule, components

def symmetry_count():
    seen, count = set(), 0
    for p in PERMS:
        if p in seen:
            continue
        count += 1
        inv = [0] * M
        for i, x in enumerate(p):
            inv[x] = i
        for q in (p, tuple(inv)):
            for u in (q, q[::-1]):
                seen.add(u)
                seen.add(tuple(M - 1 - x for x in u))
    assert len(seen) == math.factorial(M)
    return count

def load_counts(path, n, full=False):
    values = {}
    with path.open(newline='') as f:
        for row in csv.DictReader(f):
            rank = int(row['rank'])
            assert 0 <= rank < len(PERMS) and rank not in values, (path, rank)
            assert row['pattern'] == text(PERMS[rank]), (path, rank)
            avoid, contain = int(row[f'avoids_{n}']), int(row[f'contains_{n}'])
            assert 0 <= avoid <= math.factorial(n)
            assert 0 <= contain <= math.factorial(n)
            assert avoid + contain == math.factorial(n)
            values[rank] = avoid
    if full:
        assert len(values) == math.factorial(M)
    return values

@functools.lru_cache(None)
def partitions(n, maximum):
    if n == 0:
        return ((),)
    return tuple((k,) + q for k in range(min(n, maximum), 0, -1)
                 for q in partitions(n-k, k))

def tableaux(shape):
    hooks = 1
    for i, row in enumerate(shape):
        for j in range(row):
            hooks *= row - j + sum(other > j for other in shape[i+1:])
    numerator = math.factorial(sum(shape))
    assert numerator % hooks == 0
    return numerator // hooks

def monotone_rsk(n):
    return sum(tableaux(shape)**2 for shape in partitions(n, M-1))

def csv_content(header, rows):
    buf = io.StringIO(newline='')
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue()

def verify_or_write(name, content, write):
    path = ROOT / name
    if write:
        path.write_text(content)
    else:
        assert path.read_text() == content, f'Certificate mismatch: {name}'

def main(write=False):
    rep, parent, rule, components = graph_components()
    representatives = sorted(components)
    class_id = {r: i+1 for i, r in enumerate(representatives)}
    assert len(components) == 4755
    size_distribution = dict(sorted(collections.Counter(map(len, components.values())).items()))
    assert sum(k*v for k, v in size_distribution.items()) == math.factorial(M)
    assert symmetry_count() == 5282

    # Check the originally generated union-find partition, without using it to
    # build our independently reconstructed graph.
    original = ROOT / 'data' / 'discovery_components.csv'
    with original.open(newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == math.factorial(M)
    for a, row in enumerate(rows):
        assert int(row['rank']) == a
        assert row['pattern'] == text(PERMS[a])
        assert int(row['proved_component_representative_rank']) == rep[a]

    counts = {n: load_counts(ROOT/'data'/f'counts_{n}.csv', n, full=True)
              for n in (9, 10, 11, 12)}
    counts[13] = load_counts(ROOT/'data'/'selected13.csv', 13)
    counts[14] = load_counts(ROOT/'data'/'selected14.csv', 14)
    assert set(counts[9].values()) == {362815}
    for n in (9, 10, 11, 12):
        for r, members in components.items():
            assert all(counts[n][a] == counts[n][r] for a in members), (n, r)
        assert counts[n][0] == monotone_rsk(n)

    # IMPORTANT: refine only an already ambiguous bucket. At the next degree,
    # every member of that bucket must have a computed value. No missing entry
    # is ever used as an inequivalence witness.
    buckets = [representatives]
    refinement, final_pairs = [], []
    expected = {9: 1, 10: 8, 11: 256, 12: 4210, 13: 4751, 14: 4755}
    for n in (9, 10, 11, 12, 13, 14):
        if n == 14:
            final_pairs = [b[:] for b in buckets if len(b) > 1]
        new = []
        for bucket in buckets:
            if len(bucket) == 1:
                new.append(bucket)
                continue
            assert all(r in counts[n] for r in bucket), (n, bucket)
            by_count = collections.defaultdict(list)
            for r in bucket:
                by_count[counts[n][r]].append(r)
            new.extend(by_count.values())
        buckets = sorted(new, key=min)
        ambiguous = [b for b in buckets if len(b) > 1]
        refinement.append([n, len(buckets), len(ambiguous), sum(map(len, ambiguous))])
        assert len(buckets) == expected[n], (n, len(buckets))
    assert len(buckets) == 4755 and all(len(b) == 1 for b in buckets)
    assert len(final_pairs) == 4 and all(len(b) == 2 for b in final_pairs)

    # Cross-check the tail-block method against the D4 enumeration, and check
    # different tail widths against one another at the two hardest levels.
    crosschecks = []
    for filename, n, control in [
        ('blocks11_w5.csv', 11, counts[11]),
        ('blocks11_w6.csv', 11, counts[11]),
        ('blocks11_w7.csv', 11, counts[11]),
        ('blocks12_w6.csv', 12, counts[12]),
        ('blocks12_all_w7.csv', 12, counts[12]),
        ('blocks13_w7.csv', 13, counts[13]),
        ('selected14_w7.csv', 14, counts[14]),
    ]:
        data = load_counts(ROOT/'checks'/filename, n)
        for r, value in data.items():
            if r in control:
                assert value == control[r], (filename, r)
            else:
                assert r == 0 and value == monotone_rsk(n), (filename, r)
        if n == 13:
            assert set(data) == set(control)
        if n == 14:
            assert set(data) == set(control) | {0}
        crosschecks.append({'file': filename, 'degree': n, 'rows_checked': len(data)})

    # Every non-root forest edge is one application of an allowed all-n rule.
    for a in range(len(PERMS)):
        b = parent[a]
        if b < 0:
            assert a == rep[a]
        else:
            assert (PERMS[b], rule[a]) in set(neighbors(PERMS[a]))
            assert rep[a] == rep[b]
    assert sum(parent[a] >= 0 for a in parent) == 40320-4755

    membership = [[class_id[rep[a]], text(p), a, text(PERMS[rep[a]]), rep[a], len(components[rep[a]])]
                  for a, p in enumerate(PERMS)]
    verify_or_write('class_membership.csv', csv_content(
        ['class_id', 'pattern', 'lex_rank', 'representative', 'representative_rank', 'class_size'], membership), write)
    rep_rows = [[class_id[r], text(PERMS[r]), r, len(components[r])] +
                [counts[n].get(r, '') for n in (9, 10, 11, 12, 13, 14)]
                for r in representatives]
    verify_or_write('class_representatives.csv', csv_content(
        ['class_id', 'representative', 'lex_rank', 'class_size'] + [f'avoid_{n}' for n in (9,10,11,12,13,14)], rep_rows), write)
    forest = [[a, parent[a], rule[a], rep[a]] for a in range(len(PERMS))]
    verify_or_write('equivalence_forest.csv', csv_content(
        ['rank', 'parent_rank', 'edge_rule', 'representative_rank'], forest), write)
    verify_or_write('refinement_summary.csv', csv_content(
        ['maximum_degree', 'distinguished_groups', 'ambiguous_groups', 'components_in_ambiguous_groups'], refinement), write)
    pairs = []
    for a, b in final_pairs:
        assert all(counts[n][a] == counts[n][b] for n in (9,10,11,12,13))
        assert counts[14][a] != counts[14][b]
        pairs.append([text(PERMS[a]), text(PERMS[b])] + [counts[n][a] for n in (10,11,12,13)] +
                     [counts[14][a], counts[14][b], counts[14][b]-counts[14][a]])
    verify_or_write('last_four_pairs.csv', csv_content(
        ['pattern_a', 'pattern_b', 'common_avoid_10', 'common_avoid_11', 'common_avoid_12', 'common_avoid_13',
         'avoid_14_a', 'avoid_14_b', 'b_minus_a_at_14'], pairs), write)

    summary = {
        'pattern_length': 8, 'permutations': 40320, 'symmetry_orbits': 5282,
        'wilf_classes': 4755, 'sharp_distinguishing_cutoff': 14,
        'class_size_distribution': size_distribution,
        'refinement': refinement,
        'last_four_pairs': pairs,
        'forest_nonroot_edges': 35565,
        'crosschecks': crosschecks,
        'monotone_RSK_counts': {n: monotone_rsk(n) for n in range(8,15)},
        'status': 'Graph certificate and stagewise numerical separation verified; exact counts are reproducible from the included enumerators.'
    }
    verify_or_write('validation_report.json', json.dumps(summary, indent=2)+'\n', write)
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate derived certificate files')
    args = parser.parse_args()
    main(args.write)
