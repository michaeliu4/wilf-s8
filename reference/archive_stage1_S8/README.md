# The 4,755 Wilf-equivalence classes of S_8

**Result:** The connected components of the explicit graph in `PROOF.md` are
exactly the classical Wilf-equivalence classes of the 40,320 permutations of
length eight. There are **4,755** classes. Agreement of avoidance counts through
length **14** is equivalent to Wilf equivalence in S_8, and 14 is the smallest
such universal cutoff.

This is a computer-assisted proof: published shape-Wilf theorems certify
within-class equivalence for every n; exact exhaustive counting certifies
inequivalence between the resulting components. Finite agreement alone is
never used to assert an all-n equivalence. The computations and internal audits
were performed on September 14, 2026. This package has not been independently
peer-reviewed or formally verified in a proof assistant.

The result concerns Wilf classification. It makes no claim about the
different conjecture on rank-unimodality of principal permutation downsets.

## Finding a class or a witness

`class_membership.csv` contains one row for every permutation of S_8. Two
patterns are Wilf-equivalent exactly when their `class_id` fields agree. Class
IDs run from 1 to 4,755, in increasing order of the lexicographically least
representative. `lex_rank` is zero-based ordinary Lehmer rank in S_8; values in
one-line pattern strings are one-based.

`class_representatives.csv` gives the representative, size and computed
avoidance counts for every class. Blank entries at degrees 13 or 14 mean
**not needed for separation**, not zero. Comparisons use degrees 9 through 12
first; a higher degree is supplied for every representative in a still-ambiguous
group. Thus no blank value is ever used as an inequivalence witness.

`equivalence_forest.csv` gives an explicit spanning forest with 35,565
non-root edges. Follow `parent_rank` to reach the canonical representative.
Each edge is a proved symmetry, a monotone-prefix BWX move, or the
231/312 shape-Wilf move, precisely as defined in `PROOF.md`. Root rows have
`parent_rank=-1` and `edge_rule=root`.

`last_four_pairs.csv` records the four pairs that agree through degree 13 and
first separate at degree 14. `refinement_summary.csv` records all refinement
sizes. `validation_report.json` records the completed consistency checks.

## Query a class or get a proof witness

```bash
python3 src/lookup.py 13426758
python3 src/lookup.py 13426758 13427568
python3 src/lookup.py 12345678 21345678
```

With one pattern, the tool lists its whole class. With two, it prints either
a path of proved equivalences or the first length and exact counts proving
inequivalence.

## Validate the supplied certificates

Python 3.9 or later, with only the standard library:

```bash
python3 src/validate.py
```

This independently rebuilds the transformation graph using breadth-first
search, compares it with the discovery union-find computation, verifies the
spanning forest and class tables, checks all lower-degree within-component
identities, and performs stagewise numerical separation. It also compares the
stored cross-check computations and checks monotone counts by the
Robinson-Schensted/hook-length formula.

**This quick validator checks supplied numerical data; it does not by itself
re-enumerate S_14.** For fresh enumeration, use the following commands.

## Recompute the exact enumeration

Requirements: a C++17 compiler with OpenMP (tested with GCC on Linux), plus
Python 3.9+. No external datasets, Python packages, sampling, network calls,
or guessed recurrences are used.

```bash
python3 src/reproduce.py --threads 4 --native
```

The script recompiles both counters, recomputes all length-8 pattern counts at
n=9,10,11,12, the 1,035 required representatives at n=13, and the eight final
representatives plus a monotone control at n=14. It compares the exact integer
outputs with the supplied files and runs the certificate validator.

To repeat the hardest counts using both tail widths:

```bash
python3 src/reproduce.py --threads 4 --native --extra
```

A smaller compiler and low-degree regression test is available:

```bash
python3 src/reproduce.py --threads 4 --smoke
```

`--native` is optional compiler tuning. Omit it for a generic binary. The
`CXX` environment variable can select another compatible compiler. Fresh
outputs go to `build/`; the delivered data are not overwritten. Do not disable
assertions with `-DNDEBUG` when auditing these programs.

## Files and mathematical roles

- `PROOF.md`: theorem, proof, exact algorithms, numerical separation, references.
- `class_membership.csv`, `class_representatives.csv`: the complete classification.
- `equivalence_forest.csv`: all-n equivalence witnesses.
- `data/counts_9.csv` through `data/counts_12.csv`: counts for all 40,320 patterns.
- `data/selected13.csv`, `data/selected14.csv`: sparse final separation counts.
- `data/discovery_components.csv`: original union-find component computation.
- `data/*targets*`, `data/needed*.txt`, `data/all_reps.txt`: lex ranks to count.
- `checks/`: independent-method or alternative-tail-width cross-check tables.
- `src/count_all.cpp`: D4 orbit-weighted, distinct-subpattern enumeration.
- `src/count_blocks.cpp`: exact prefix/tail bitmap enumeration, widths 5, 6, 7.
- `src/generate_components.py`: the original component generator for lengths 3–8.
  Its isolated length-4 sporadic equivalence is used only at length 4, never
  extended or used in the length-8 graph.
- `src/validate.py`: independently rebuilds and audits the classification.
- `src/lookup.py`: queries classes and prints individual proof witnesses.
- `src/reproduce.py`: recompiles and recomputes the count certificates.
- `SHA256SUMS`: integrity manifest of the delivered files (excluding itself).
