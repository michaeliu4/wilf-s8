# The Ray–West parameter and the Wilf classification of permutations of length eight

The paper proves the complete **4,755-class classification of S₈**, with
sharp separation cutoff **14**, and an **interval statistic for the
Ray–West parameter j**, derived from their insertion classification.
It also gives a deletion-graph cycle basis, a finite algorithm for g₃,
structural formulas for layered and separated patterns, and exact
monotone cluster coefficients. The full Wilf class of the increasing
pattern is determined in every length. The new cubic comparison refutes
the degree-bound clause of Ray–West's conjecture under the precise
common-coefficient interpretation stated in the paper.

Start with [the manuscript](manuscript/main.pdf).
The general compact-statistic problem for g₃ and the all-length
component claims in codimensions 3 and 4 remain open.

<!-- BEGIN RELEASE -->
Computational companion: [release `v1.0.0`](https://github.com/michaeliu4/wilf-s8/releases/tag/v1.0.0).
The release contains the manuscript, exact certificates, verification
code and retained computational records. See below for the scope of
the quick checks and full regeneration commands.
<!-- END RELEASE -->

## First commands

With Python 3.10+, GNU Make, a C++17 compiler supporting `__int128`, and
SymPy installed:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make check
```

Expected output includes 40,320 patterns, 4,755 classes, 24,818 exact
transform identities, all 35,565 recorded provenance moves, and the
refinement `1,8,256,4210,4751,4755`, followed by input-validation and
bounded mathematical regression checks.
`make check` checks saved census evidence; it does not recount the entire
classification.

```sh
make paper              # TeX Live + latexmk; produces manuscript/main.pdf
make test-references    # deliberately corrupted cross-reference fixtures
make verify             # broader computational suite; see its explicit scope
```

See [reproduction instructions](docs/REPRODUCING.md) for full fresh
recounts, the long adaptive cluster campaign, requirements and limitations.
The commands were tested locally. The saved verification record states
the scope of those tests and distinguishes retained evidence from fresh runs.

## Contents

| Path | Purpose |
|---|---|
| `manuscript/` | Exact source/PDF pair, including two vector figures |
| `src/` | Counting algorithms, certificate checks, regression and release tools |
| `data/` | Sparse S₈ certificate, class/provenance data, retained sweep values |
| `checks/` | Row-level recounts, raw outputs and explicitly scoped check records |
| `reference/archive_stage1_S8/` | Earlier distinct algorithms and certificate comparison data |
| `SOURCE_MAP.md` | All 25 bibliography entries: identity, use, locators and access limits |
| `docs/REVISION8_VERIFICATION.md` | Checks and open release tasks for this revision |
| `docs/GITHUB_SETUP.md` | Author-side procedure for preparing later releases |
| `docs/VERIFICATION.md` | Historical revision-7 verification record |
| `CITATION.cff`, `release.json` | Citation metadata and local release configuration |
| `SHA256SUMS` | SHA-256 identities of all packaged files except this manifest |

## Release and reuse

`make manifest` refreshes the checksum manifest after authorized changes.
`make package` builds a deterministic ZIP under ignored `dist/`, excluding
executables, caches, TeX intermediates, nested archives and private review
material. `make release-check` checks local release metadata and the
presence of the selected reuse terms; it is not an online access test.
The MIT code/data scope and separate manuscript status are stated in
[LICENSE_STATUS.md](LICENSE_STATUS.md).

The paper explains mathematical soundness and coverage. The repository
explains execution. Neither successful checks nor this local package
constitute journal acceptance or a public archival deposit.
