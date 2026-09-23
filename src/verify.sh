#!/bin/bash
# Reruns the short verifications of the package (about 25 minutes on one core). Every advertised comparison is checked; failures stop the suite.
# Long runs (their outputs are in ../checks and ../data): verify_B.py 8 (25 min), delgraph 7 (8 min),
# run_classes_k.sh 3 6 (~1 h), run_classes_k.sh 4 5 (~30 min), the S_8 sweeps (~4 h: see ../README.md).
set -euo pipefail
export PYTHONOPTIMIZE=""
cd "$(dirname "$0")"
g++ -O2 -std=c++17 -o clusters clusters.cpp
python3 test_cluster_cli.py --executable ./clusters
g++ -O2 -std=c++17 -o delgraph delgraph.cpp
g++ -O2 -std=c++17 -o classes_k classes_k.cpp
g++ -O2 -std=c++17 -o autom autom.cpp
g++ -O2 -std=c++17 -o chi_components chi_components.cpp

echo "== 1. Cluster expansion: brute force vs formula, patterns of length <= 4, k <= 3"
python3 cluster_bruteforce.py
echo "== 2. Cluster numbers by inversion; asserts c_{a+1} = -2a and c_{a+2} = 2a(a+2) - j (lengths 3, 4)"
python3 clusternums.py 3 4 | tail -3; python3 clusternums.py 4 4 | tail -3

echo "== 3. Theorem A / cycle basis / leading-edge lemma, ALL patterns of length 2 through 6 (delgraph.cpp; length 7 is logged in ../checks/delgraph7.txt)"
for a in 2 3 4 5 6; do ./delgraph $a | python3 check_output.py "L2 failures=0  LE failures=0  sum_b0!=C2: 0  sum_b1!=2A(A+2): 0" || { echo "FAIL: delgraph $a"; exit 1; }; done

echo "== 3b. Separation of deletion-graph components, ALL patterns of length 1 through 7"
g++ -O2 -std=c++17 -o check_component_separation check_component_separation.cpp
separation_csv=$(mktemp)
./check_component_separation 7 "$separation_csv"
rm -f "$separation_csv"

echo "== 4. One-move classes, SELECTED patterns only: sum_rho beta_0^{(k)} = C_k(a) for 10 patterns with k=3 and 6 with k=4"
echo "   (exhaustive runs for all patterns of length <= 6 (k=3) and <= 5 (k=4) are logged in ../checks/classes_k3_a6.txt, classes_k4_a5.txt)"
C3=(x x 128 628 2374 7176); C4=(x x 780 5140 26504)
for t in 12 21 123 132 1234 1324 1342 12345 13245 24135; do ./classes_k 3 $t | python3 check_output.py "classes=${C3[${#t}]}\b" || { echo "FAIL: classes_k 3 $t"; exit 1; }; done
for t in 12 123 132 1234 1324 2413; do ./classes_k 4 $t | python3 check_output.py "classes=${C4[${#t}]}\b" || { echo "FAIL: classes_k 4 $t"; exit 1; }; done
echo "   (checked against C_3 = 128, 628, 2374, 7176 for a=2..5 and C_4 = 780, 5140, 26504 for a=2..4)"
echo "== 4b. Per-component Euler characteristics (Theorem on codimensions 3, 4), SELECTED patterns; expect 'chi!=1: 0' on every line"
echo "   (exhaustive runs: run_chi_components.sh, ~12 min; logs in ../checks/chi_components_k3.txt, chi_components_k4.txt)"
for t in 12 132 1324 2413 13245 132465; do ./chi_components 3 $t | python3 check_output.py "chi!=1: 0 " || { echo "FAIL: chi_components 3 $t"; exit 1; }; done
for t in 12 132 1324 2413 13245; do ./chi_components 4 $t | python3 check_output.py "chi!=1: 0 " || { echo "FAIL: chi_components 4 $t"; exit 1; }; done
echo "== 4c. Codimension five is not universal (Proposition on codimension five): a=3 gives 44892 (C_5(3)=44888); a=4: 1234, 2413 differ; 4 hosts with chi != beta_0 for tau=123"
./classes_k 5 123 | python3 check_output.py "classes=44892\b" || { echo "FAIL"; exit 1; }
./classes_k 5 1234 | python3 check_output.py "classes=302001\b" || { echo "FAIL"; exit 1; }
./classes_k 5 2413 | python3 check_output.py "classes=301992\b" || { echo "FAIL"; exit 1; }
./chi_components 5 123 | python3 check_output.py "chi!=beta0: 4 " || { echo "FAIL"; exit 1; }

echo "== 5. Interval formula certificate w = U + D, ALL patterns of length <= 6 (length <= 8 is logged in ../checks/verify_B8.log)"
python3 verify_B.py 6 | tail -8

echo "== 6. Monotone cluster numbers (binomial law for k <= a+1, Catalan corrections), a <= 8"
python3 monotone_clusters.py 8 12
echo "== 6b. Exact corner-removal and direct Fredholm coefficient checks, a <= 12"
python3 check_monotone_coefficients.py --amax 12

echo "== 7. Known-theorem classes of S_4..S_8: expect 4 16 91 595 4755, and provenance trees"
python3 check_known_sequences.py classes
python3 provenance.py 8 /dev/stdout | tail -2

echo "== 8. Cluster program vs known sequences"
python3 check_known_sequences.py clusters

echo "== 9. S_8 certificate assembly (uses the sweep outputs in ../data)"
python3 assemble_S8.py
python3 check_certificate.py

echo "== 10. Stage-1 certificate (reference/archive_stage1_S8) vs the present certificate: expect 4755 identical classes, 0 mismatches"
python3 compare_archive_S8.py

echo "== 11. Deletion-overlap formula (Theorem 7.2) vs cluster g_3: 830 patterns of length 4..7, expect 0 mismatches"
python3 check_deletion_boxes.py
echo "   (the 4,755 representatives of length 8: g++ -O2 -std=c++17 -o dbox deletion_boxes.cpp; see ../checks/deletion_boxes_vs_clusters.txt)"

echo "== 12. Return catalogue (Theorem 6.7) vs pure-return indicator U for l <= 7; r_l; j on all patterns of length <= 5"
python3 check_catalogue.py

echo "== 12b. Brute-force containment counter (third method) vs certificate at n = 12 for the eight hardest representatives"
echo "   (n = 13, 14 take ~10 min per pattern at n = 14: run_bruteforce_hardest.sh; log in ../checks/bruteforce_hardest.txt)"
g++ -O2 -std=c++17 -o bruteforce_contain bruteforce_contain.cpp
tempdir=$(mktemp -d)
trap 'rm -rf "$tempdir"' EXIT
python3 recount_containment.py --scope hardest --n 12 --output "$tempdir/values.csv"
python3 check_recount_records.py
python3 check_component_records.py
python3 test_verification.py

echo "== 13. Layered formula, Appendix A: intersection table, prefix statistic, Lemma A.6 and the recurrence, layered patterns of length <= 4"
python3 check_layered.py 4
echo "   (length <= 5 was run for ../checks/layered_identities.txt; about 20 min)"
echo "done"
