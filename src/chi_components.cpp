// chi_components.cpp -- per-component Euler characteristics of the inflation complex K_tau(rho).
//
// For every rho in S_{a+k} containing tau this program
//   (1) lists the occurrences of tau in rho and forms the one-move classes (union-find on
//       "differ in exactly one point"),
//   (2) enumerates every cell of K_tau(rho): a subset T of positions together with an inflation
//       structure rho|_T = tau[pi_1,...,pi_a]; the cell has dimension |T|-a and its vertices are the
//       occurrences obtained by choosing one point in each block; it is assigned to the one-move
//       class of the occurrence formed by the first point of each block,
//   (3) adds (-1)^{|T|-a} to the Euler characteristic of that class.
// It reports the number of rho for which some class has Euler characteristic != 1, the number of
// rho with chi_tau(rho) != beta_0(rho), the total number of classes (must be C_k(a)) and the total
// cell counts f_d.  Usage: chi_components k tau   (tau as digits, e.g. 1324); n = |tau|+k <= 12.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#include <cstdint>
using namespace std;

static int n, a, k;
static int tau[16];
static int rho[16];
static int compOf[1 << 12];      // component id of an occurrence (bitmask of positions), -1 if none
static int parent_[4096];
static int findp(int x) { while (parent_[x] != x) { parent_[x] = parent_[parent_[x]]; x = parent_[x]; } return x; }

// standardized values of rho on the positions of T (sorted), plus the position list
static int posT[32], valT[16], m;

// check order-isomorphism of sequence s (length a) with tau
static bool isTau(const int* s) {
    for (int i = 0; i < a; i++) for (int j = i + 1; j < a; j++)
        if ((s[i] < s[j]) != (tau[i] < tau[j])) return false;
    return true;
}

// enumerate compositions of m into a blocks; blockStart[] / blockSize[]
static int blockStart[16], blockSize[16];
static long long cellsFound;
static vector<long long>* chiComp;
static int sign_;
static long long* fcount;

static void recurse(int b, int start) {
    if (b == a) {
        if (start != m) return;
        int mins[16];
        for (int i = 0; i < a; i++) {
            int mn = 1 << 30;
            for (int j = blockStart[i]; j < blockStart[i] + blockSize[i]; j++) mn = min(mn, valT[j]);
            mins[i] = mn;
        }
        if (!isTau(mins)) return;
        // first vertex: first position of each block
        int mask = 0;
        for (int i = 0; i < a; i++) mask |= 1 << posT[blockStart[i]];
        int c = compOf[mask];
        if (c < 0) { fprintf(stderr, "internal error: cell vertex is not an occurrence\n"); exit(1); }
        (*chiComp)[findp(c)] += sign_;
        cellsFound++;
        return;
    }
    int remaining = a - b;           // blocks still to place including this one
    for (int s = 1; start + s + (remaining - 1) <= m; s++) {
        // block [start, start+s) must be a value interval
        int mn = 1 << 30, mx = -1;
        for (int j = start; j < start + s; j++) { mn = min(mn, valT[j]); mx = max(mx, valT[j]); }
        if (mx - mn != s - 1) continue;
        blockStart[b] = start; blockSize[b] = s;
        recurse(b + 1, start + s);
    }
}

int main(int argc, char** argv) {
    if (argc != 3) { fprintf(stderr, "usage: chi_components k tau\n"); return 1; }
    // Validate before copying or sizing arrays; accumulate with a small bound
    // so arbitrarily long integer arguments cannot overflow.
    if (!argv[1][0]) { fprintf(stderr, "k must be a nonnegative decimal integer\n"); return 1; }
    k = 0;
    for (const char* p = argv[1]; *p; ++p) {
        if (*p < '0' || *p > '9' || k > (12 - (*p - '0')) / 10) {
            fprintf(stderr, "k must be a nonnegative decimal integer at most 12\n"); return 1;
        }
        k = 10 * k + (*p - '0');
    }
    const size_t length = strlen(argv[2]);
    if (length < 1 || length > 9) { fprintf(stderr, "tau must have 1 through 9 digits\n"); return 1; }
    a = static_cast<int>(length);
    bool seen[10] = {};
    for (int i = 0; i < a; i++) {
        const char digit = argv[2][i];
        if (digit < '1' || digit > '0' + a || seen[digit - '0']) {
            fprintf(stderr, "tau must be a permutation of 1 through its length\n"); return 1;
        }
        seen[digit - '0'] = true;
        tau[i] = digit - '0';
    }
    if (k > 12 - a) { fprintf(stderr, "n = a+k must be at most 12\n"); return 1; }
    n = a + k;
    vector<int> perm(n); for (int i = 0; i < n; i++) perm[i] = i + 1;
    long long nContain = 0, nBadComp = 0, nBadChi = 0, totalClasses = 0;
    long long fd[16]; memset(fd, 0, sizeof fd);
    fcount = fd;
    // list all a-subsets of [n] as masks
    vector<int> asubs;
    for (int mask = 0; mask < (1 << n); mask++) if (__builtin_popcount(mask) == a) asubs.push_back(mask);
    vector<int> subsets;  // all subsets with >= a elements
    for (int mask = 0; mask < (1 << n); mask++) if (__builtin_popcount(mask) >= a) subsets.push_back(mask);
    vector<long long> chi;
    long long worst[4] = {0,0,0,0}; int worstRho[16]; bool haveWorst = false;
    do {
        for (int i = 0; i < n; i++) rho[i] = perm[i];
        // occurrences
        vector<int> occ;
        for (int mask : asubs) {
            int s[16], t = 0;
            for (int i = 0; i < n; i++) if (mask >> i & 1) s[t++] = rho[i];
            if (isTau(s)) occ.push_back(mask);
        }
        if (occ.empty()) continue;
        nContain++;
        for (int mask : subsets) compOf[mask] = -1;
        for (size_t i = 0; i < occ.size(); i++) { compOf[occ[i]] = (int)i; parent_[i] = (int)i; }
        // one-moves: occurrences sharing an (a-1)-subset
        // for each occurrence and each point, key = mask without that point; use array keyed by mask
        static int keyRep[1 << 12];
        for (int mask = 0; mask < (1 << n); mask++) keyRep[mask] = -1;
        for (size_t i = 0; i < occ.size(); i++) {
            int mask = occ[i];
            for (int p = 0; p < n; p++) if (mask >> p & 1) {
                int key = mask & ~(1 << p);
                if (keyRep[key] < 0) keyRep[key] = (int)i;
                else { int x = findp(keyRep[key]), y = findp((int)i); if (x != y) parent_[x] = y; }
            }
        }
        chi.assign(occ.size(), 0);
        chiComp = &chi;
        // cells
        for (int mask : subsets) {
            m = 0;
            for (int i = 0; i < n; i++) if (mask >> i & 1) { posT[m] = i; valT[m] = rho[i]; m++; }
            // standardize the values within T
            for (int i = 0; i < m; i++) { int r = 0; for (int j = 0; j < m; j++) if (valT[j] < valT[i]) r++; posT[m + i] = r + 1; }
            for (int i = 0; i < m; i++) valT[i] = posT[m + i];
            // quick necessary condition: T must contain an occurrence -> the pattern must contain tau;
            // the recursion checks the inflation condition directly (cheap for these sizes).
            sign_ = ((m - a) & 1) ? -1 : 1;
            cellsFound = 0;
            recurse(0, 0);
            fd[m - a] += cellsFound;
        }
        // evaluate
        long long b0 = 0, chiTotal = 0; bool bad = false;
        for (size_t i = 0; i < occ.size(); i++) if (findp((int)i) == (int)i) {
            b0++; chiTotal += chi[i];
            if (chi[i] != 1) bad = true;
        }
        totalClasses += b0;
        if (bad) {
            nBadComp++;
            if (!haveWorst) { haveWorst = true; for (int i = 0; i < n; i++) worstRho[i] = rho[i]; }
        }
        if (chiTotal != b0) nBadChi++;
    } while (next_permutation(perm.begin(), perm.end()));
    printf("tau=%s k=%d n=%d  rho containing tau: %lld  classes total: %lld  ", argv[2], k, n, nContain, totalClasses);
    printf("rho with a class of chi!=1: %lld  rho with chi!=beta0: %lld  cells:", nBadComp, nBadChi);
    for (int d = 0; d <= k; d++) printf(" f%d=%lld", d, fd[d]);
    if (haveWorst) { printf("  first bad rho:"); for (int i = 0; i < n; i++) printf("%d", worstRho[i]); }
    printf("\n");
    return 0;
}
