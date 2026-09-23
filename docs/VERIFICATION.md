# Revision 7: verification scope

Date: 21 September 2026. This is an author-side revision/checking record,
not a claim of nonparticipant journal refereeing or proof-assistant verification.
The two supplied referee reports were evaluated against the source; their
reported executions are not silently counted as executions performed here.

## Mathematical changes

The retained principal statements are unchanged. The contraction argument
is isolated as Lemma 9.4 with a full feasible-assignment projection invariant;
the separated-pattern theorem is now Theorem 9.5. Corollary 9.6 proves the
cubic comparison for an explicit infinite family, with the interpretation
of Ray–West's conjectural degree clause delimited in the text. The rectangle
proposition now precedes the coefficient theorem. Two exact vector diagrams
illustrate the deletion cycles and the 2413 return.

The Ray–West track family is credited explicitly as earlier mathematics.
The manuscript supplies the primitive-support selection, count and interval
interpretation. Theorem 6.7's dictionary, the historical polynomiality and
leading-coefficient antecedents, and every bibliography entry are documented
in `SOURCE_MAP.md` and `docs/reference-audit.json`. All 24 bibliography keys
are cited and have audit entries. Bibliographic identity and theorem
applicability are separate checks; the source map preserves limits on access
and on original-proof reading.

## Executed checks

| Check | Actual result and scope |
|---|---|
| Existing full named regression suite | `bash src/verify.sh`: exit 0; output in `checks/revision7_suite.log` |
| Saved S8 certificate | 40,320 permutations, 4,755 classes, 24,818 exact transform identities; adaptive refinement 1,8,256,4210,4751,4755 |
| Earlier-stage agreement | Retained 20,063 certificate entries and 161,280 per-pattern values agree |
| Cluster input validation | 26 invalid invocations rejected; six valid boundary/known invocations complete |
| Sanitizers | The same 26 invalid/six valid cluster cases passed under AddressSanitizer and UndefinedBehaviorSanitizer; no diagnostics |
| Inherited verification failure tests | 28 regression checks pass |
| Compiled mathematical references | All 135 label types agree with source environments; no undefined citation/reference |
| Negative reference fixtures | Seven corrupted type/missing/duplicate cases rejected |
| Local release/package fixtures | 16 checks pass, including malformed configuration, missing terms, manifest corruption and deterministic ZIP output; no network actions |
| New exact/bounded checks | Symbolic cubic identity and leading coefficients for k=1,...,6; 93 modular patterns at odd lengths 17,...,201; 8,803 primitive-support dictionaries through length 25; return-figure data |
| Elimination invariant | 400 seeded finite forest instances, 12,691 initial feasible assignments, 1,709 elimination steps; complete assignment projections preserved within each instance |
| Existing coefficient tests | 126 corner-removal tableau comparisons and three exact Fredholm-expansion cases pass |

The full suite's graph check is exhaustive for patterns of lengths 2–6;
its separate component-separation check covers all 5,913 patterns of lengths
1–7. Higher-codimension component checks in that suite are explicitly selected
cases, not a new full sweep. Appendix regression in the quick suite is bounded
and its labels identify the lengths checked. Fresh selected counter executions
are additional evidence, not a complete new classification census.

`checks/revision7_math.json` records the new exact/bounded tests. These tests
support the proofs but do not replace the infinite arguments. The broad suite
and the new mathematical checker were run as separate commands; `make verify`
provides the combined entry point.

## Retained evidence, not freshly regenerated here

The complete 9,510-row direct-placement recount at n=11,12 was performed
in revision 5 and checked again here, including raw stdout, scope and provenance.
The 16 hardest-case values at n=13,14 are inherited and comparison-checked.
The full 1,035-representative n=13 campaign, all decisive n=14 computations,
and the complete finite component campaign of Theorem 9.7 were not repeated
in this revision. No fresh outside implementation is asserted merely because
a referee reports having used one.

All 53 files under `data/` and `reference/archive_stage1_S8/` are byte-identical
to revision 6. The core S8 certificate is unchanged. See
`checks/revision7_evidence_identity.json`. The original contribution/disclosure
source is unchanged as well; automatic reference numbers follow the revised
mathematical ordering.

## Build, visual inspection, and public release

The exact final PDF has 38 pages, two vector figures and two tables.
All pages were inspected in rendered contact sheets, with the new diagrams,
contraction argument, cubic comparison and numerical tables also inspected at
full-page resolution. No unresolved reference/citation or visible clipping
was found. This is not a claim of PDF/UA conformance.

Clean-package replay results are recorded in
`checks/revision7_clean_build.json`. The recorded environment is in
`checks/revision7_environment.txt`; a different TeX installation need not
produce identical PDF bytes. The supplied GitHub Actions workflow is prepared
and its local commands have been exercised, but no remote Actions run is
asserted.

The repository has not been published. The owner/name, release tag and reuse
terms must be selected by the author. `configure_release.py` changes local
metadata; it does not create a public repository, grant rights, test anonymous
access or assign a DOI. Follow `docs/GITHUB_SETUP.md` before citing a real release.
