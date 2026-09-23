// bruteforce_contain.cpp -- a third, deliberately naive counter of g_k(tau) = #{pi in S_n : pi contains tau}
// (n = |tau| + k), independent of the cluster method (clusters.cpp) and of the prefix/tail bitmap method of
// the earlier certificate.  It enumerates every way of placing an occurrence of tau in [n] x [n] (position set P,
// value set V) together with every arrangement of the remaining k points, and records each resulting
// permutation in a bitmap indexed by its rank, so that permutations containing tau several times are counted
// once.  Memory is kept small by processing the permutations with a fixed first entry pi(1) = c separately
// (a bitmap of (n-1)! bits per chunk: 778 MB for n = 14).
//   usage: bruteforce_contain n tau        (tau as digits, |tau| <= 9, n <= 14)
//   output: g_k(tau) and |Av_n(tau)| = n! - g_k(tau)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <exception>
#include <vector>
#include <cstdint>
#include <algorithm>
using namespace std;

static int n, a, k, tau[16];
static uint64_t fact[16];

int main(int argc, char** argv) try {
    if (argc != 3) { fprintf(stderr, "usage: bruteforce_contain n tau\n"); return 1; }
    char* end = nullptr;
    errno = 0;
    long parsed_n = strtol(argv[1], &end, 10);
    if (errno || end == argv[1] || *end || parsed_n < 1 || parsed_n > 14) {
        fprintf(stderr, "n must be an integer in [1,14]\n"); return 1;
    }
    n = static_cast<int>(parsed_n);
    a = static_cast<int>(strlen(argv[2]));
    if (a < 1 || a > 9 || a > n) {
        fprintf(stderr, "need 1 <= |tau| <= min(9,n)\n"); return 1;
    }
    bool seen[10] = {false};
    for (int i = 0; i < a; ++i) {
        int v = argv[2][i] - '0';
        if (v < 1 || v > a || seen[v]) {
            fprintf(stderr, "tau must be a permutation of 1,...,|tau|, written as digits\n"); return 1;
        }
        seen[v] = true; tau[i] = v;
    }
    k = n - a;
    fact[0] = 1; for (int i = 1; i < 16; i++) fact[i] = fact[i - 1] * i;
    // all a-subsets of [n] as sorted arrays
    vector<vector<int>> subs;
    { vector<int> s(a); for (int i = 0; i < a; i++) s[i] = i + 1;
      while (true) { subs.push_back(s);
        int i = a - 1; while (i >= 0 && s[i] == n - a + i + 1) i--; if (i < 0) break;
        s[i]++; for (int j = i + 1; j < a; j++) s[j] = s[j - 1] + 1; } }
    uint64_t chunkBits = fact[n - 1];
    vector<uint64_t> bitmap((chunkBits + 63) / 64);
    uint64_t total = 0;
    int pi[16];
    for (int c = 1; c <= n; c++) {
        fill(bitmap.begin(), bitmap.end(), 0ULL);
        for (const auto& P : subs) {
            bool oneInP = (P[0] == 1);
            for (const auto& V : subs) {
                // occurrence: position P[i] gets value V[tau[i]-1]
                if (oneInP) { if (V[tau[0] - 1] != c) continue; }
                else { bool cInV = false; for (int x : V) if (x == c) { cInV = true; break; } if (cInV) continue; }
                for (int i = 0; i < n; i++) pi[i] = 0;
                for (int i = 0; i < a; i++) pi[P[i] - 1] = V[tau[i] - 1];
                // free positions and free values
                int F[16], W[16], nf = 0, nw = 0;
                for (int p = 1; p <= n; p++) if (pi[p - 1] == 0) F[nf++] = p;
                { bool inV[16] = {false}; for (int x : V) inV[x] = true;
                  for (int v = 1; v <= n; v++) if (!inV[v]) W[nw++] = v; }
                // if 1 is free, it must receive c: remove 1 from F and c from W
                int F2[16], W2[16], m = 0;
                if (!oneInP) {
                    pi[0] = c;
                    for (int i = 0; i < nf; i++) if (F[i] != 1) F2[m++] = F[i];
                    int m2 = 0; for (int i = 0; i < nw; i++) if (W[i] != c) W2[m2++] = W[i];
                } else { for (int i = 0; i < nf; i++) F2[i] = F[i]; for (int i = 0; i < nw; i++) W2[i] = W[i]; m = nf; }
                // all arrangements of W2 onto F2
                int idx[16]; for (int i = 0; i < m; i++) idx[i] = i;
                do {
                    for (int i = 0; i < m; i++) pi[F2[i] - 1] = W2[idx[i]];
                    // rank pi(2..n) as a permutation of [n] \ {c}
                    uint64_t r = 0; unsigned used = 0;
                    for (int i = 1; i < n; i++) {
                        int v = pi[i] - 1 - (pi[i] > c ? 1 : 0);      // 0..n-2
                        unsigned smaller = ((1u << v) - 1) & ~used;
                        r += (uint64_t)__builtin_popcount(smaller) * fact[n - 1 - i];
                        used |= 1u << v;
                    }
                    bitmap[r >> 6] |= 1ULL << (r & 63);
                } while (next_permutation(idx, idx + m));
            }
        }
        uint64_t cnt = 0; for (uint64_t w : bitmap) cnt += __builtin_popcountll(w);
        total += cnt;
        fprintf(stderr, "chunk pi(1)=%d: %llu permutations containing tau\n", c, (unsigned long long)cnt);
    }
    printf("tau=%s n=%d g_%d=%llu Av_%d=%llu\n", argv[2], n, k, (unsigned long long)total, n,
           (unsigned long long)(fact[n] - total));
    return 0;
} catch (const std::exception& e) {
    fprintf(stderr, "counter failed: %s\n", e.what());
    return 2;
}
