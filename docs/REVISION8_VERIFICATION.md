# Revision 8: correction and verification record

Date: 23 September 2026. Revision 7 is preserved in the supplied source
archive; this record concerns the revised manuscript and local companion.
This record describes the pre-release checks; the versioned release URL in
the README is the authority for the public snapshot. No journal submission
or archival DOI is claimed.

The abstract now defines the counted objects and identifies the universal
Ray--West polynomial. The introduction states the conjectural status and
precise scope of the contradicted degree restriction. Section 9 cites Ray
and West's Corollary 9.5 unambiguously. The projection-elimination lemma
states the planar candidate hypothesis before using coordinate order.
Hegarty's primary article is cited for the necessity direction of the
distinct-deletions criterion. Cambridge's publisher record confirms the
retained page range 339--345 for Vatter's chapter. The appendix gives
slightly fuller exhaustion descriptions; the main theorem statements and
the stored finite certificate are unchanged.

The quick check now validates every recorded provenance edge and its
rooted class tree, in addition to the numerical classification certificate.
The auxiliary component program rejects malformed argument counts,
integers and patterns before enumeration. The build script can use three
pdfLaTeX passes when `latexmk` is unavailable; the documented Ubuntu route
still uses `latexmk`.

Checks run on this local package:

- `make PYTHON=/opt/anaconda3/bin/python check`: passed. The standard
  certificate checks all 40,320 permutations, 4,755 classes, 24,818
  retained transform identities and 35,565 recorded provenance moves.
  The input tests reject 26 malformed cluster calls and 25 malformed
  component calls and pass the stated valid boundary cases.
- `make PYTHON=/opt/anaconda3/bin/python test-references`: passed all seven
  deliberately corrupted reference fixtures.
- `make paper` with TeX Live 2025 Basic plus CTAN `cleveref` 0.21.4 supplied
  temporarily through `TEXINPUTS`: produced a 38-page PDF. The compiled
  reference check reports 135 typed labels and no unresolved citations or
  references. The original 38-page revision-7 PDF remains untouched.
- Every page of the new PDF was inspected in contact sheets. Both figures,
  both tables, and the availability/disclosure page were also inspected
  at full-page resolution. The figures remain legible and mathematically
  unchanged. Table 1's caption has additional space below its bottom rule.
- A clean extraction of the companion ZIP passed `make check` and rebuilt
  the PDF with the same hash as the working copy:
  `95fd0b58c490536b7fe201992c205a97100cab9cde3b573997972bb3417ba958`.

The saved direct-placement values were compared with their records; the
complete long recount and full finite component campaign were not rerun
for this revision. Reported external reviewer computations are not counted
as local executions here. This record does not certify global research
priority, the cited theorems' proofs, or the infinite arguments by machine.

The release locator and MIT code/data terms are recorded in `release.json`
and `LICENSE`. The manuscript has separate reuse terms. This local record
alone does not establish anonymous access; the published GitHub release and
its assets must be checked directly. An archival DOI can be cited only after
an actual deposit.
