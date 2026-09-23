# Revision 6: verification and scope

Manuscript: *The Ray–West parameter and the Wilf classification of permutations of length eight*, Mingchang Liu. Revision date: 21 September 2026. This is an author-side revision record, not a journal referee endorsement or formal proof certificate.

## Exact changes and dependencies

The classification certificate and the implemented return test are unchanged. The reference machinery now distinguishes theorem, lemma, proposition, corollary, definition and appendix labels while preserving their common numbering. The Ray–West notation and original-page locators were checked directly. Homberger is cited in published form with explicit preprint statement locators; the downward comparison also credits the corrected proof by Bevan–Homberger–Tenner.

Theorem 10.1(iii) now uses the sharp exponent from Proposition 10.3. The redundant two-by-two determinant expansion has been replaced by that proposition. New Corollary 10.4 proves the previously experimental formula

    c_(2a+3)(iota_a) = (-1)^(a+1) binom(4a+4,a+3) + (a+1) Cat(a+2)^2,

for every a >= 1. Its proof includes the exponential factor in the Poissonized measure and the two one-box enlargements of the rectangle. The finite evidence in Question 2 is extended through pattern length seven by a newly implemented exhaustive program.

A further wording error was repaired in the introduction and after Definition 6.1. The displayed return construction inserts the new minimum immediately before the (b-1)st old point, not immediately before the old minimum, which is the bth old point. The gap coordinates, displayed maps and return indicators are unchanged. The standing nonempty-pattern convention and the nonnegative-index restriction on the displayed Bessel series are explicit.

## Fresh executions in this revision

| Check | Evidence and result |
|---|---|
| Complete project regression suite | `revision6_suite.log` and `revision6_suite_status.json`: exit status 0, elapsed 513.297 seconds in the recorded environment. The script labels distinguish exhaustive and selected checks. |
| Compiled LaTeX reference types | `revision6_reference_check.txt`: all 130 source labels agree with their compiled semantic types; all used internal-reference and bibliography keys resolve. |
| Negative reference tests | `reference_failure_regressions.txt`: seven deliberately wrong/missing/duplicated reference records rejected. |
| Failure-handling tests in the suite | 28 checks passed, including malformed or missing recount records and unsupported counter inputs. |
| Deletion-graph component separation | `component_separation.csv` and `.log`: all 5,913 patterns of lengths 1 through 7; every host of each length 3 through 9 is enumerated and its deletion pairs grouped by resulting pattern. No coordinate-separation failure; maximum number of components is 4 at lengths 6 and 7. |
| Monotone coefficients by a distinct tableau calculation | `monotone_coefficients_rev6.json`: 126 coefficient comparisons for 1 <= a <= 12, including both Catalan corrections. Tableaux are counted by corner removal, not the pre-existing hook-length implementation. |
| Direct Fredholm minors | The same JSON records exact rational expansion for (a,p)=(1,2),(2,2),(1,3); the first powers and coefficients agree with Proposition 10.3. |
| Optimized-Python check of the new coefficient checker | `monotone_coefficients_optimized.json`: a <= 3 passes under `python3 -O`; this particular checker uses effective explicit validation. Other assertion-based project scripts must not be run with `-O`. |
| Certificate, class provenance and literal interval formula | The independently supplied audit driver was replayed privately: all 40,320 S8 permutations, 4,755 classes, 35,565 provenance-tree edges, 24,818 populated transforms, the refinement sequence, and the literal return test on S8 agree. Only its final summary-file diagnostic was adapted to the current filename. |
| Separate fresh-run harness | The supplied harness was executed on the correct source package, compiling its own copies of the project programs. All 4,755 deletion-overlap values agree; fresh cluster and direct-placement counts through n=12 agree for the increasing representative and the eight hardest representatives. Additional deletion-graph, codimension-five, monotone and earlier-certificate checks pass. Elapsed 25.051 seconds; driver and outputs are retained privately, not redistributed as project code. |

The complete suite also reruns all deletion graphs for pattern lengths 2 through 6, selected componentwise Euler-characteristic cases, the codimension-five failure, return tests through length six, known-equivalence class totals, and Appendix A checks through length four. It freshly checks the increasing length-eight pattern through host length fourteen. That last check is not a fresh length-fourteen recount of the four hardest pairs.

## Retained evidence checked, not regenerated in full

- The 9,510 per-representative direct-placement values at n=11,12 were freshly generated in revision 5. Revision 6 retains the actual counts, raw stdout, elapsed times, scope and source/executable identities and checks all rows again. It does not repeat that entire campaign.
- The 16 hardest-representative values at n=13,14 in `bruteforce_hardest.txt` are inherited from revision 4 and checked for agreement. They were not freshly recounted in revision 6.
- The complete codimension-three/four component logs retain their stated 872-pattern and 152-pattern coverage. The current suite validates those records and reruns its explicitly listed cases; it is not a second full enumeration of Theorem 9.5's range.
- The earlier 161,280 per-pattern values and 20,063 representative entries are comparison-checked, not regenerated by the present record.
- The manuscript's general separation and compact-statistical g3 questions remain open in the stated sense. A finite computation does not settle either.

## Production and release

The final 36 pages have been rendered and inspected, with unchanged pages accounted for by pixel identity after the last local prose edit. The small inherited page-one vertical-box warning (2.42233 pt) causes no visible overlap or clipping. There are no unresolved labels/citations, duplicate labels or overfull horizontal boxes. These are build and visual checks, not a PDF/UA or formal-accessibility certification.

The exact final source/PDF identities, clean-build comparison and page-image identities are recorded in `revision6_pdf_qa.json`; the isolated build and retained-data checks are in `revision6_clean_package_check.log`. `SHA256SUMS` identifies the delivered payload, not a hypothetical future public release.

No public repository, DOI, license grant or journal submission was created. `SOURCE_MAP.md` records the bounded literature check and its remaining access limits, including the 2010 problem-session chapter's endpoint discrepancy. The mathematical problem statements are sourced to the inspected 2026 survey.
