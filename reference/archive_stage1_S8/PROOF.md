# A computer-assisted classification of classical Wilf equivalence in S_8

**Computation and audit date:** September 14, 2026.

## 1. Statement

For a permutation \(\beta\), write
\[
a_n(\beta)=|\operatorname{Av}_n(\beta)|,
\qquad g_n(\beta)=n!-a_n(\beta).
\]
Containment is classical, not consecutive. Repeated occurrences of a pattern
inside one permutation contribute only once to \(g_n\).

Let \(\iota_k=12\cdots k\), \(\delta_k=k\cdots21\), and let \(\oplus\) denote
direct sum. Thus, for \(\alpha\in S_k\) and \(\gamma\in S_l\),
\[
\alpha\oplus\gamma
=\alpha_1\cdots\alpha_k\,(k+\gamma_1)\cdots(k+\gamma_l).
\]
The empty permutation is allowed when \(l=0\).

Define an undirected graph \(\mathcal G_8\) with vertex set \(S_8\) and the
following edges, and no additional generators:

1. A permutation is joined to its reverse, complement, and inverse.
2. For \(2\le k\le8\) and \(\gamma\in S_{8-k}\), join
   \(\iota_k\oplus\gamma\) to \(\delta_k\oplus\gamma\).
3. For \(\gamma\in S_5\), join \(231\oplus\gamma\) to \(312\oplus\gamma\).

**Theorem.** The graph \(\mathcal G_8\) has 4,755 connected components, and
these components are exactly the Wilf-equivalence classes of \(S_8\).
Moreover, for \(\sigma,\tau\in S_8\), the following conditions are equivalent:

- \(a_n(\sigma)=a_n(\tau)\) for every \(n\ge0\);
- \(\sigma\) and \(\tau\) belong to the same component of \(\mathcal G_8\);
- \(a_n(\sigma)=a_n(\tau)\) for \(10\le n\le14\).

The universal cutoff 14 is sharp: some inequivalent patterns agree at every
length from 0 through 13.

The full class membership table, canonical representatives, all-n equivalence
paths, exact count data, and executable sources accompany this proof. This is
a computer-assisted result with internal checks, not an independently
peer-reviewed or proof-assistant-verified result.

## 2. Every graph edge is an all-n Wilf equivalence

Reverse, complement, and inverse commute with classical pattern containment.
Each therefore restricts to a bijection between the corresponding sets of
avoiding permutations of any fixed length.

For the other edges use the established shape-Wilf theorems
\[
\iota_k\sim_s\delta_k\quad(k\ge1),
\qquad 231\sim_s312,
\]
proved by Backelin–West–Xin [1] and Stankova–West [2], respectively.
Bloom–Saracino [3] give a bijection for the second theorem. Here shape-Wilf
equivalence means equality of avoidance counts for full rook placements on
every southwest-closed Ferrers board, with pattern containment requiring the
whole bounding rectangle to lie in the board.

The right-extension property [1, Proposition 2.3] gives
\[
\alpha\sim_s\beta\quad\Longrightarrow\quad
\alpha\oplus\gamma\sim_s\beta\oplus\gamma.
\tag{1}
\]
Only this right-extension property is used. No arbitrary left extension or
replacement inside an arbitrary internal direct-sum block is assumed.

### An explicit justification of the extension mechanism

In a full rook placement, color a cell white when some copy of \(\gamma\)
lies strictly northeast of that cell. The white cells form a Ferrers board.
The remaining cells are gray. The white region is determined by the gray
rooks alone: for a given white cell, choose a northeast \(\gamma\)-copy
maximizing the sum of its minimum row and minimum column. If one of that
copy's rooks were white, a \(\gamma\)-copy northeast of that rook would have
strictly larger minima, a contradiction. Thus there is a certifying copy
consisting entirely of gray rooks.

Keep gray rooks fixed and delete their rows and columns from the white board.
The remaining white rooks form a full placement \(Q\). The original placement
avoids \(\alpha\oplus\gamma\) exactly when \(Q\) avoids \(\alpha\). Apply a
shape-Wilf bijection to replace \(Q\) by a \(\beta\)-avoiding placement of the
same shape, then restore deleted rows and columns and gray rooks.

The white region is unchanged. It cannot shrink because its gray certificates
remain. It cannot grow: any new \(\gamma\)-copy involving a white rook casts
its shadow inside the shadow of that rook's old gray certificate; a copy using
only gray rooks already existed. Hence the construction is invertible and
proves (1).

Applying (1) to the two displayed shape equivalences proves every edge in
\(\mathcal G_8\). Consequently, every connected component is contained in a
single true Wilf class. This conclusion holds for all lengths, not just the
computed lengths.

## 3. Enumerating the proved components

Enumerate the 40,320 permutations lexicographically. For each vertex generate
exactly the neighbors specified in Section 1, and take connected components.
The included discovery program uses union-find; the certificate validator
independently reconstructs the graph using breadth-first search, with both
directions of every rule explicitly generated. Their component assignments
agree on all 40,320 vertices.

The output is 4,755 components. Their sizes are:

| Size | Number of components | Size | Number of components |
|---:|---:|---:|---:|
| 2 | 29 | 20 | 1 |
| 4 | 260 | 24 | 39 |
| 8 | 4,094 | 32 | 9 |
| 12 | 10 | 40 | 1 |
| 16 | 309 | 48 | 1 |
| 18 | 1 | 56 | 1 |

The counts of components sum to 4,755, and size times multiplicity sums to
40,320. There are 5,282 symmetry orbits before applying the shape-Wilf moves.

The forest certificate has 35,565 non-root edges, namely
\(40,320-4,755\). Every edge is checked directly against one of the stated
rules. Thus following a parent path gives an explicit proof of equivalence
from any pattern to its canonical representative.

It remains to prove that distinct components cannot merge into a larger Wilf
class. This is the finite, exact enumeration part of the proof.

## 4. Exact counting, first method: D4-weighted distinct subpatterns

For \(\pi\in S_n\), let \(D_8(\pi)\) be the **set of distinct** classical
patterns of length eight contained in \(\pi\). Let \(O\) be a symmetry orbit
in \(S_8\), and let \(R_n\) contain one representative of every symmetry orbit
in \(S_n\). Then, for \(\beta\in O\),
\[
|O|g_n(\beta)
=\sum_{\pi\in R_n}|\operatorname{Orb}(\pi)|\,
 |D_8(\pi)\cap O|.
\tag{2}
\]
Indeed, the intersection size is invariant under the symmetry action on
\(\pi\). Expanding the weighted sum over all \(S_n\) counts pairs
\((\pi,\rho)\) with \(\rho\in O\) and \(\rho\le\pi\). Every \(\rho\in O\)
is contained in exactly \(g_n(\beta)\) permutations, by symmetry.

`count_all.cpp` implements (2). It generates domain permutations, keeps the
lexicographically least element of each orbit, determines the stabilizer and
hence its orbit weight, and enumerates all eight-position subsets. A timestamp
array removes repeated occurrences of the same pattern. Importantly, patterns
are deduplicated individually, not after collapsing a target symmetry orbit.
The final sums are divided by target-orbit sizes as in (2).

Its internal subpattern code is a bijective mixed-radix insertion code. When
appending the next selected value \(v\) to a selected word of length \(j\),
update the code by
\[
c_{j+1}=(j+1)c_j+\#\{\text{earlier selected values smaller than }v\}.
\]
A complete conversion table maps the 8! codes to ordinary Lehmer ranks, so
the output has unambiguous conventional indexing.

The program checks that the sum of domain orbit weights is \(n!\), that all
divisions by target-orbit sizes are exact, and that all containment counts lie
between 0 and \(n!\). It was run for all 40,320 target patterns at
\(n=9,10,11,12\).

## 5. Exact counting, second method: prefix/tail block unions

The degrees 13 and 14 are handled by a different exact decomposition.
Fix a tail width \(W\). Partition \(S_n\) by an ordered prefix \(u\) of length
\(n-W\). Let \(T\) be its set of unused values. A block consists of the \(W!\)
possible orders of \(T\), represented by \(W!\) bits.

Fix a target \(\beta\in S_8\). Every occurrence of \(\beta\) chooses a prefix
subsequence of length \(k\) and a subset \(U\subseteq T\) of size
\(\ell=8-k\). These choices are compatible if the selected prefix values,
ranked among all eight selected values, are the first \(k\) values of
\(\beta\). If compatible, the last \(\ell\) values of \(\beta\) prescribe a
unique relative order \(\rho\) of the selected tail values.

Precompute \(B(U,\rho)\), the bitmap of tail orders in which the specified
values \(U\) occur in the specified order \(\rho\). Each bitmap contains
exactly \(W!/\ell!\) set bits. For a fixed prefix, OR these bitmaps over all
compatible choices of prefix subsequence and tail-value subset. The result
has a set bit **if and only if** the corresponding full permutation contains
\(\beta\). Therefore, if \(N_u(\beta)\) is the population count of that union,
\[
g_n(\beta)=\sum_u N_u(\beta).
\tag{3}
\]
Overlapping occurrences cause no overcount because the operation is set union.

### Efficient exact compatibility tests

For a chosen prefix subsequence \(s_0,\ldots,s_{k-1}\), define
\[
A=\sum_{j=0}^{k-1}\#\{h>j:s_h<s_j\}\frac{(7-j)!}{\ell!},
\qquad
w(t)=\sum_{j:s_j>t}\frac{(7-j)!}{\ell!}.
\]
For a selected tail subset \(U\), the key
\[
A+\sum_{t\in U}w(t)
\tag{4}
\]
is exactly the prefix part of the Lehmer rank of the complete eight-element
pattern, divided by \(\ell!\). The remaining suffix rank is in
\(\{0,\ldots,\ell!-1\}\). Thus (4) can be compared with
\(\lfloor\operatorname{rank}(\beta)/\ell!\rfloor\) using an exact lookup table.
This tests the ranks among all eight values, not merely the standardized order
of the prefix by itself. Fixed-cardinality Gray ordering of tail subsets
updates (4) by one addition and one subtraction.

### Complement symmetry

Write \(c\) for complement, using the relevant ambient size. Prefixes occur
in distinct pairs \(u,c(u)\), and
\[
N_{c(u)}(\beta)=N_u(c(\beta)).
\]
Hence it suffices to enumerate one prefix from each pair and accumulate
\[
g_n(\beta)=\sum_{u<c(u)}\bigl(N_u(\beta)+N_u(c(\beta))\bigr).
\tag{5}
\]
The two bitmap unions are maintained **separately**; they are not ORed
together. There is no subsequent division by two. The program checks
\(2W!\times\#\{u<c(u)\}=n!\).

`count_blocks.cpp` implements (3)–(5) for widths 5, 6, and 7. All counts and
bitmap words use 64-bit unsigned integers. At width 7 there are 5,040 bits per
bitmap; unused bits of its final machine word remain zero.

## 6. The separation certificate

Use one representative per proved component. Starting with all 4,755
representatives in one group, refine groups by their exact avoidance counts.
Only groups still containing more than one representative require the next
degree. Every representative in each such group is counted before that group
is refined. In particular, a missing value is never compared with an integer
to manufacture an inequivalence witness.

The exact refinement sizes are:

| Counts through degree | Distinct groups | Ambiguous groups | Components in ambiguous groups |
|---:|---:|---:|---:|
| 9 | 1 | 1 | 4,755 |
| 10 | 8 | 8 | 4,755 |
| 11 | 256 | 235 | 4,734 |
| 12 | 4,210 | 490 | 1,035 |
| 13 | 4,751 | 4 | 8 |
| 14 | 4,755 | 0 | 0 |

All patterns of length eight have counts \(a_n=n!\) for \(n<8\),
\(a_8=40,319\), and the exact degree-nine enumeration gives
\(a_9=362,815\) for every pattern.

Exactly four pairs of component representatives remain indistinguishable
through degree 13:

| First pattern | Second pattern | Common a10 | Common a11 | Common a12 | Common a13 |
|---|---|---:|---:|---:|---:|
| 13426758 | 13427568 | 3,626,194 | 39,832,606 | 476,576,815 | 6,161,552,875 |
| 13678254 | 32718564 | 3,626,193 | 39,832,503 | 476,570,602 | 6,161,264,067 |
| 14567823 | 14567832 | 3,626,196 | 39,832,782 | 476,585,968 | 6,161,922,266 |
| 23815764 | 25876314 | 3,626,193 | 39,832,501 | 476,570,338 | 6,161,244,848 |

Their degree-14 counts are:

| First pattern | Second pattern | a14 of first | a14 of second | Second minus first |
|---|---|---:|---:|---:|
| 13426758 | 13427568 | 85,472,873,492 | 85,472,873,496 | 4 |
| 13678254 | 32718564 | 85,461,367,267 | 85,461,369,287 | 2,020 |
| 14567823 | 14567832 | 85,485,717,761 | 85,485,717,376 | −385 |
| 23815764 | 25876314 | 85,460,332,594 | 85,460,331,546 | −1,048 |

Thus distinct graph components have different avoidance counts at some
length at most 14. No two graph components can belong to the same Wilf class.
Together with Section 2 this proves the theorem. The first row alone proves
that cutoff 13 would not suffice, so cutoff 14 is sharp.

## 7. Completed audits and reproducibility

The following checks were executed, not merely suggested:

- Union-find and independently written breadth-first graph traversals agree
  on all 40,320 component assignments. Every forest edge satisfies a valid
  all-n equivalence rule.
- For all 40,320 patterns at each of degrees 9, 10, 11 and 12, counts are
  constant on each proved component.
- Tail widths 5 and 6 at degree 11 agree with the D4 method on all 1,035
  representatives needed at degree 13. Width 7 also agrees on the nine
  final/control representatives.
- At degree 12, width 6 agrees on those 1,035 representatives, and width 7
  agrees on all 4,755 component representatives.
- At degree 13, width 6 and width 7 agree on all 1,035 required representatives.
- At degree 14, width 6 and width 7 agree on all eight final representatives.
  These decompositions use 60,540,480 and 8,648,640 complement-prefix orbits,
  respectively; both cover exactly 87,178,291,200 full permutations.
- Independently, for the monotone pattern, Robinson–Schensted and the
  hook-length formula give
  \[
  a_n(12345678)=\sum_{\lambda\vdash n,\,\lambda_1\le7}
  \left(\frac{n!}{\prod_{x\in\lambda}h(x)}\right)^2.
  \]
  This agrees with all available monotone enumeration controls. In particular,
  at degree 14 both methods give 85,494,566,892.
- The final delivered sources compile with warnings enabled. Both the smoke
  test and a fresh full reproduction were executed successfully. The latter
  recomputed all primary degrees 9–14 from the delivered sources and matched
  every stored primary count exactly.

Alternative tail widths are independent decompositions of the domain, not
independent implementations of every low-level operation. The graph traversal
and the two main counting methods supply separate implementation checks.
No claim of external independent review or formal verification is made.

`src/reproduce.py` recompiles and recomputes the primary proof data, and its
`--extra` flag repeats both hard degrees at both tail widths. The quick
`src/validate.py` checks the stored certificates and numerical consistency;
it does not itself rerun the exhaustive degree-14 enumeration. See `README.md`.

## 8. Scope

This resolves the displayed length-eight Wilf-equivalence classification.
It does not establish the separate general conjecture that the rank sequence
of distinct patterns contained in a fixed permutation is unimodal.

## References

[1] Jörgen Backelin, Julian West, and Guoce Xin. *Wilf-equivalence for singleton
classes*. Advances in Applied Mathematics 38 (2007), 133–148.
Theorem 2.1 and Proposition 2.3. DOI: `10.1016/j.aam.2004.11.006`.

[2] Zvezdelina Stankova and Julian West. *A new class of Wilf-equivalent
permutations*. Journal of Algebraic Combinatorics 15 (2002), 271–290.
Preprint: `arXiv:math/0103152`. Matrix conventions in the original paper differ
from the southwest-board convention; [3] states the 231/312 version explicitly.

[3] Jonathan Bloom and Dan Saracino. *A simple bijection between 231-avoiding
and 312-avoiding placements*. Journal of Combinatorial Mathematics and
Combinatorial Computing 89 (2014), 23–32. Preprint: `arXiv:1110.2564`.

[4] Vincent Vatter. *An assortment of problems in permutation patterns:
unimodality, equivalence, derangements, and sorting*. `arXiv:2602.16355` (2026).
Question 3.1 asks for the length-eight classification; Proposition 3.2 and
Theorems 3.3–3.4 summarize the shape-Wilf results used above. The finite
classification and exact counts in this package are computations made here,
not results quoted from that survey.

[5] C. Schensted. *Longest increasing and decreasing subsequences*. Canadian
Journal of Mathematics 13 (1961), 179–191; J. S. Frame, G. de B. Robinson, and
R. M. Thrall. *The hook graphs of the symmetric group*. Canadian Journal of
Mathematics 6 (1954), 316–324. These supply the independent monotone control.
