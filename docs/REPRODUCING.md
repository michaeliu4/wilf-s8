# Reproducing the computations

Run commands from the repository root unless a command explicitly changes directory.
Python 3.10 or later and a C++17 compiler with `__int128` are required.
The symbolic checks use SymPy; install `requirements.txt` in a virtual environment.
The tested environment is recorded in `checks/revision7_environment.txt`.

## Saved evidence: no fresh permutation enumeration

```sh
python3 src/check_certificate.py
python3 src/check_recount_records.py
python3 src/compare_archive_S8.py
```

Expected results: 40,320 patterns partitioned into 4,755 classes; 24,818
cluster/avoidance identities; refinement `1,8,256,4210,4751,4755`.
The recount checker validates all 9,510 saved n=11,12 rows, their raw
counter output, uniqueness and scope, plus the 16 inherited hardest-case
n=13,14 values. The archive comparison checks 20,063 earlier certificate
entries and 161,280 earlier per-pattern values. These commands check
retained evidence, not fresh enumerations.

## Regression checks

```sh
make check             # saved evidence, input-failure tests, exact new identities
make paper             # build PDF; check reference types and bibliography coverage
make test-references   # seven deliberately corrupted reference fixtures
make verify            # full computational regression suite; writes verification.log
```

`make verify` rebuilds the C++ programs. It covers all deletion graphs for
patterns of lengths 2 through 6; component separation for all 5,913 patterns
of lengths 1 through 7; selected higher-codimension components; interval
checks through length 6; known-equivalence classes; monotone coefficients;
certificate assembly and comparison; deletion-box and catalogue checks;
selected fresh direct-placement recounts; and software failure tests.
Its printed labels distinguish exhaustive ranges from selected cases.
It is not a complete regeneration of the S8 census or of the full finite
Euler-characteristic range. The underlying long suite passed in revision 7;
`checks/revision7_suite.log` preserves its output. Machine-dependent timings
from earlier runs are not promises about another machine.

`check_revision7_math.py` additionally checks the cubic identity and leading
coefficients symbolically, 8,803 primitive-support dictionaries through
length 25, 93 modular separated patterns, the return figure, and 400
seeded finite forest instances. The forest tests enumerate all feasible
assignments within each generated instance and check the full projection
invariant; they are not an exhaustive test of the lemma's infinite scope.

Do not run verification with `python -O`: some inherited scripts use
assertions. The shell suite and Makefile clear `PYTHONOPTIMIZE`.

## Supported counter interfaces

```sh
g++ -O3 -std=c++17 src/clusters.cpp -o /tmp/wilf-clusters
/tmp/wilf-clusters 4 13426758

g++ -O3 -std=c++17 src/bruteforce_contain.cpp -o /tmp/wilf-contain
/tmp/wilf-contain 12 13426758
```

`clusters K PATTERN [-list]` takes an excess K and a digit permutation
of length 1–9, with total length at most 14. `-list` is the only optional
flag. Invalid integers, duplicate/out-of-range digits, extra arguments,
and overlong inputs are rejected before copying into fixed arrays.
`bruteforce_contain N PATTERN` takes the total host length instead.
Its pattern length is 1–9 and total length is at most 14. Large excesses
can make enumeration impractical even within the supported input domain.

## Fresh complete direct-placement recounts

```sh
JOBS=4 bash src/run_bruteforce_all12.sh --output /tmp/wilf-all12.csv
JOBS=1 bash src/run_bruteforce_hardest.sh --output /tmp/wilf-hardest.csv
```

The first command enumerates all 4,755 representatives at n=11,12; the
second enumerates the eight hardest representatives at n=13,14. Each CSV
row retains actual containing/avoiding counts, raw stdout, comparison
value, status, elapsed time and provenance. The actual values are parsed
from the counter, never copied from the certificate. Missing, duplicate,
malformed, nonzero-exit or mismatching results cause failure.

Use new output paths to preserve the distributed records. `--resume`
requires identical source, executable, certificate and scope hashes;
otherwise start a new output. At n=14 each worker's bitmap is approximately
0.78 GB. Select concurrency according to memory. The complete n=11,12
recount included here was executed in revision 5 and checked again in
later revisions; the hardest-case log predates that recount. This revision
does not describe those historical runs as fresh independent executions.

## Regenerate the sparse classification

Work in a copy to preserve the distributed evidence.

```sh
cd src
g++ -O3 -std=c++17 -o clusters clusters.cpp
python3 known_classes.py 8 -o ../data/known_classes8.txt
python3 provenance.py 8 ../data/provenance8.txt
# In the working copy only, move aside the three existing output files:
# ../data/reps8_K4.txt ../data/unsep12_K5.txt ../data/unsep13_K6.txt
python3 run_reps.py 4 ../data/reps8.txt ../data/reps8_K4.txt 2
python3 run_reps.py 5 ../data/unsep12.txt ../data/unsep12_K5.txt 2
python3 run_reps.py 6 ../data/unsep13.txt ../data/unsep13_K6.txt 2
python3 assemble_S8.py
python3 check_certificate.py
```

The 4,755, 1,035 and eight representative lists describe the adaptive
campaign. The certificate checker requires a next count for every group
still unresolved at a preceding level. The generation/coverage proof and
its relation to Wilf equivalence are in Section 8 of the paper. This long
regeneration was not repeated in full during revision 7.

## Full finite component campaign

```sh
bash src/run_chi_components.sh
```

The retained `chi_components_k3.txt` and `chi_components_k4.txt` record
all patterns of lengths 2–6 at k=3 and 2–5 at k=4. The one-point pattern
is handled analytically in the manuscript. This finite computation does
not establish the all-length conjecture.

## Build reproducibility

The source is a single `manuscript/main.tex`, including vector TikZ
figures and bibliography. `src/build_manuscript.sh` freezes date metadata
and invokes `latexmk`/`pdflatex`, then checks cross-reference types.
Byte identity is expected in the recorded TeX environment; a different
TeX/font installation can produce a mathematically identical but
byte-different PDF. No font files are distributed.
