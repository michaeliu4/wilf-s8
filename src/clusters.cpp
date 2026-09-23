// clusters.cpp -- cluster numbers c_r(tau) and avoidance counts |Av_n(tau)| by the cluster expansion.
//
//   g_k(tau) = #{pi in S_{a+k} containing tau} = sum_{r=a}^{a+k} C(a+k,r)^2 (a+k-r)! c_r(tau),
//   c_r(tau) = sum_{rho in S_r} c(rho),  c(rho) = sum_{T subset [r]} (-1)^{r-|T|} [rho|_T contains tau].
//
// c(rho) vanishes unless every point of rho lies in an occurrence of tau ("cluster").  Clusters are
// generated level by level: a cluster of size a+t is obtained from a smaller cluster rho' by merging a new
// occurrence of tau that shares a-s points with rho' (s >= 1 new points), all interleavings of the new
// points with the old ones being taken in positions and in values.  Every cluster arises this way
// (order a covering set of occurrences and take successive unions).  Exact deduplication by hashing.
//
// Usage: clusters K tau            e.g.  clusters 6 21534867
// Output: for r = a..a+K: c_r, #clusters, and |Av_{r}(tau)| as a decimal string (unsigned 128-bit).
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <unordered_set>
#include <algorithm>
#include <string>
#include <chrono>
using namespace std;
typedef uint64_t u64; typedef unsigned __int128 u128; typedef __int128 i128;
static int A; static int tau[16];
static inline u64 pack(const int* p,int n){ u64 k=0; for(int i=0;i<n;i++) k|=(u64)(p[i])<<(4*i); return k; }
static inline void unpack(u64 k,int n,int* p){ for(int i=0;i<n;i++) p[i]=(k>>(4*i))&15; }

// all embeddings of pattern sig (length L, values 1..L) into perm p (length N): callback with positions q[0..L-1]
template<class F> static void embed_rec(const int* sig,int L,const int* p,int N,int i,int start,int* q,F&& f){
  if(i==L){ f(q); return; }
  for(int pos=start; pos<=N-(L-i); pos++){
    bool ok=true;
    for(int j=0;j<i&&ok;j++){ if((p[q[j]]<p[pos])!=(sig[j]<sig[i])) ok=false; }
    if(!ok) continue;
    q[i]=pos; embed_rec(sig,L,p,N,i+1,pos+1,q,f);
  }
}


struct HSet { // open addressing, linear probing, keys != 0
  vector<u64> tab; size_t cnt=0; size_t mask=0;
  HSet(){ tab.assign(1<<10,0); mask=(1<<10)-1; }
  static inline u64 h(u64 k){ k^=k>>31; k*=0x9E3779B97F4A7C15ULL; k^=k>>29; return k; }
  void grow(){ vector<u64> old; old.swap(tab); tab.assign(old.size()*2,0); mask=tab.size()-1; cnt=0; for(u64 k: old) if(k) insert(k); }
  bool insert(u64 k){ size_t i=h(k)&mask; while(tab[i]){ if(tab[i]==k) return false; i=(i+1)&mask; } tab[i]=k; cnt++; if(cnt*2>tab.size()) grow(); return true; }
  size_t size() const { return cnt; }
  template<class F> void each(F&& f) const { for(u64 k: tab) if(k) f(k); }
};
static vector<HSet> level; // level[t] = clusters of size A+t

// merge: rho' = p (length N), shared positions Q (length L, increasing) matched to tau positions P (length L, increasing)
// new points = tau positions not in P.  Enumerate all interleavings.
static int N_, L_, S_;
static int Pm[16], Qm[16], newpos[16]; // newpos: tau positions of new points (sorted)
static int pgap_new[16][16], pgap_cnt[16];  // for each position gap j: list of new points (indices into newpos) in that gap
static int vgap_new[16][16], vgap_cnt[16];  // for each value gap: new points in that value gap
static int pold[16][16], pold_cnt[16];      // old non-Q positions in gap j (positions in p)
static int vold[16][16], vold_cnt[16];      // old non-Q values in value gap j
static int pp_[16];
static int tgt_level;
// position order: sequence of items; item = (type,idx): type 0 old position idx, type 1 new point idx
static int posseq[16], posseq_len; static int valseq[16], valseq_len;
static long long merges_generated=0;

static void emit(){
  int n=N_+S_;
  int rankOldVal[17], rankNewVal[16];
  for(int i=0;i<n;i++){ int it=valseq[i]; if(it>=1) rankOldVal[it]=i+1; else rankNewVal[-it-1]=i+1; }
  int rho[16];
  for(int i=0;i<n;i++){ int it=posseq[i]; if(it>=0) rho[i]=rankOldVal[pp_[it]]; else rho[i]=rankNewVal[-it-1]; }
  level[tgt_level].insert(pack(rho,n)); merges_generated++;
}
// value sequence: walk value gaps 0..L_ ; gap j holds old values (vold) and new values (vgap_new), each internally increasing
// choose interleavings: recursive over gaps, then within gap over subsets.
static int sv_[16]; // shared values sorted
static void val_rec(int gap,int len){
  if(gap>L_){ valseq_len=len; emit(); return; }
  int m=vgap_cnt[gap], nn=vold_cnt[gap]; int tot=m+nn;
  int idx[16]; for(int i=0;i<m;i++) idx[i]=i;
  while(true){
    int len2=len; int io=0, in=0;
    for(int s=0;s<tot;s++){ bool isnew=false; for(int i=0;i<m;i++) if(idx[i]==s){isnew=true;break;}
      if(isnew){ valseq[len2++]=-(vgap_new[gap][in++])-1; } else { valseq[len2++]=vold[gap][io++]; } }
    if(gap<L_){ valseq[len2++]=sv_[gap]; }
    val_rec(gap+1,len2);
    if(m==0) break;
    int i=m-1; while(i>=0 && idx[i]==tot-m+i) i--; if(i<0) break; idx[i]++; for(int j=i+1;j<m;j++) idx[j]=idx[j-1]+1;
  }
}
static void pos_rec(int gap,int len){
  if(gap>L_){ posseq_len=len; val_rec(0,0); return; }
  int m=pgap_cnt[gap], nn=pold_cnt[gap]; int tot=m+nn;
  int idx[16]; for(int i=0;i<m;i++) idx[i]=i;
  while(true){
    int len2=len; int io=0, in=0;
    for(int s=0;s<tot;s++){ bool isnew=false; for(int i=0;i<m;i++) if(idx[i]==s){isnew=true;break;}
      if(isnew){ posseq[len2++]=-(pgap_new[gap][in++])-1; } else { posseq[len2++]=pold[gap][io++]; } }
    if(gap<L_){ posseq[len2++]=Qm[gap]; }
    pos_rec(gap+1,len2);
    if(m==0) break;
    int i=m-1; while(i>=0 && idx[i]==tot-m+i) i--; if(i<0) break; idx[i]++; for(int j=i+1;j<m;j++) idx[j]=idx[j-1]+1;
  }
}

int main(int argc,char** argv){
  // Validate every argument before writing into a fixed-size buffer or
  // allocating generation tables. K must be a fully consumed decimal integer.
  if(argc!=3 && argc!=4){
    fprintf(stderr,"usage: clusters K tau [-list]\n"); return 1;
  }
  if(argc==4 && string(argv[3])!="-list"){
    fprintf(stderr,"clusters: the only optional argument is -list\n"); return 1;
  }
  int K=0;
  if(argv[1][0]=='\0'){
    fprintf(stderr,"clusters: K must be a nonnegative decimal integer\n"); return 1;
  }
  for(const char* c=argv[1]; *c; ++c){
    if(*c<'0' || *c>'9'){
      fprintf(stderr,"clusters: K must be a nonnegative decimal integer\n"); return 1;
    }
    // K never exceeds 14 here, so the next multiplication cannot overflow.
    K=10*K+(*c-'0');
    if(K>14){ fprintf(stderr,"clusters: K exceeds the supported host-length bound\n"); return 1; }
  }
  const size_t length=strlen(argv[2]);
  if(length<1 || length>9){
    fprintf(stderr,"clusters: tau must have length 1 through 9\n"); return 1;
  }
  A=static_cast<int>(length);
  if(A+K>14){
    fprintf(stderr,"clusters: |tau|+K must be at most 14 (fixed 2^14-bit tables)\n"); return 1;
  }
  bool seen[10]={false};
  for(int i=0;i<A;++i){
    const char c=argv[2][i];
    if(c<'1' || c>'0'+A || seen[c-'0']){
      fprintf(stderr,"clusters: tau must contain each digit 1,...,|tau| exactly once\n"); return 1;
    }
    seen[c-'0']=true;
  }
  for(int i=0;i<A;++i) tau[i]=argv[2][i]-'0';
  auto T0=std::chrono::steady_clock::now();
  level.assign(K+1,HSet());
  level[0].insert(pack(tau,A));
  // generate
  for(int t=0;t<K;t++){
    vector<u64> cur; cur.reserve(level[t].size()); level[t].each([&](u64 k){cur.push_back(k);});
    for(u64 key: cur){
      int p[16]; int N=A+t; unpack(key,N,p);
      for(int s=1; t+s<=K; s++){
        int L=A-s; if(L<0) continue;
        // choose P subset of [A] of size L
        int P[16]; for(int i=0;i<L;i++) P[i]=i;
        while(true){
          // pattern sig = std(tau|_P)
          int sig[16]; { int vals[16]; for(int i=0;i<L;i++) vals[i]=tau[P[i]]; for(int i=0;i<L;i++){ int r=0; for(int j=0;j<L;j++) if(vals[j]<vals[i]) r++; sig[i]=r+1; } }
          int q[16];
          embed_rec(sig,L,p,N,0,0,q,[&](int* Q){
            // set up merge data
            N_=N; L_=L; S_=s; tgt_level=t+s;
            for(int i=0;i<L;i++){ Pm[i]=P[i]; Qm[i]=Q[i]; }
            // new points = tau positions not in P
            int ns=0; { int inP[16]={0}; for(int i=0;i<L;i++) inP[P[i]]=1; for(int i=0;i<A;i++) if(!inP[i]) newpos[ns++]=i; }
            // position gaps: gap j = number of P positions before it
            for(int j=0;j<=L;j++){ pgap_cnt[j]=0; vgap_cnt[j]=0; pold_cnt[j]=0; vold_cnt[j]=0; }
            for(int i=0;i<ns;i++){ int g=0; for(int j=0;j<L;j++) if(P[j]<newpos[i]) g++; pgap_new[g][pgap_cnt[g]++]=i; }
            // value gaps: number of P-values below tau[newpos[i]]
            // new points sorted by value for vgap lists
            int ordv[16]; for(int i=0;i<ns;i++) ordv[i]=i; sort(ordv,ordv+ns,[&](int x,int y){return tau[newpos[x]]<tau[newpos[y]];});
            for(int ii=0;ii<ns;ii++){ int i=ordv[ii]; int g=0; for(int j=0;j<L;j++) if(tau[P[j]]<tau[newpos[i]]) g++; vgap_new[g][vgap_cnt[g]++]=i; }
            // old non-Q positions per gap
            { int inQ[16]={0}; for(int i=0;i<L;i++) inQ[Q[i]]=1; int g=0; for(int pos=0;pos<N;pos++){ if(inQ[pos]){ g++; continue;} pold[g][pold_cnt[g]++]=pos; } }
            // old non-Q values per value gap: shared values sorted
            { int sv[16]; for(int i=0;i<L;i++) sv[i]=p[Q[i]]; sort(sv,sv+L); for(int i=0;i<L;i++) sv_[i]=sv[i]; int isShared[17]={0}; for(int i=0;i<L;i++) isShared[sv[i]]=1;
              int g=0; for(int v=1;v<=N;v++){ if(isShared[v]){ g++; continue; } vold[g][vold_cnt[g]++]=v; } }
            for(int i=0;i<N;i++) pp_[i]=p[i];
            pos_rec(0,0);
          });
          int i=L-1; while(i>=0 && P[i]==A-L+i) i--; if(i<0) break; P[i]++; for(int j=i+1;j<L;j++) P[j]=P[j-1]+1;
        }
      }
    }
  }
  fprintf(stderr,"merges generated: %lld  gen time %.1fs\n",merges_generated, std::chrono::duration<double>(std::chrono::steady_clock::now()-T0).count());
  if(argc>3 && string(argv[3])=="-list"){
    int n=A+K; vector<u64> keys; level[K].each([&](u64 k){keys.push_back(k);}); sort(keys.begin(),keys.end());
    for(u64 key: keys){ int p[16]; unpack(key,n,p); vector<vector<int>> occ; int q[16];
      embed_rec(tau,A,p,n,0,0,q,[&](int* Q){ occ.push_back(vector<int>(Q,Q+A)); });
      for(int i=0;i<n;i++) printf("%d%s",p[i],i+1<n?".":""); printf(" %zu",occ.size());
      for(auto& o: occ){ printf(" "); for(int x: o) printf("%d,",x); } printf("\n"); }
    return 0;
  }
  // cluster numbers: c(rho) = sum_T (-1)^{r-|T|} [rho|_T contains tau], via a bit-parallel OR-zeta transform
  vector<i128> c(K+1,0);
  static const u64 M6[6]={0x5555555555555555ULL,0x3333333333333333ULL,0x0F0F0F0F0F0F0F0FULL,0x00FF00FF00FF00FFULL,0x0000FFFF0000FFFFULL,0x00000000FFFFFFFFULL};
  u64 EVEN=0; for(int i=0;i<64;i++) if(!(__builtin_popcount(i)&1)) EVEN|=1ULL<<i;
  for(int t=0;t<=K;t++){
    int n=A+t;
    vector<u64> keys; keys.reserve(level[t].size()); level[t].each([&](u64 k){keys.push_back(k);});
    static u64 W[256];
    for(u64 key: keys){
      int p[16]; unpack(key,n,p);
      long long cv=0;
      if(n<=6){
        // small: direct
        vector<int> occ; int q[16];
        embed_rec(tau,A,p,n,0,0,q,[&](int* Q){ int m=0; for(int i=0;i<A;i++) m|=1<<Q[i]; occ.push_back(m); });
        vector<unsigned char> f(1<<n,0); for(int o: occ) f[o]=1;
        for(int b=0;b<n;b++) for(int T=0;T<(1<<n);T++) if(T>>b&1) f[T]|=f[T^(1<<b)];
        for(int T=0;T<(1<<n);T++) if(f[T]) cv += ((n-__builtin_popcount(T))&1)? -1:1;
      } else {
        int nw=1<<(n-6); for(int w=0;w<nw;w++) W[w]=0;
        // occurrences by backtracking with value bounds
        int lo[16],hi[16]; // per pattern letter index
        // iterative DFS
        int q[16]; 
        // recursive lambda via explicit stack
        struct Fr{int i; int pos;};
        // simple recursion using std::function-free approach:
        auto dfs=[&](auto&& self,int i,int start,int* lo,int* hi)->void{
          if(i==A){ int m=0; for(int j=0;j<A;j++) m|=1<<q[j]; W[m>>6]|=1ULL<<(m&63); return; }
          for(int pos=start; pos<=n-(A-i); pos++){
            int v=p[pos]; if(v<=lo[i]||v>=hi[i]) continue;
            int lo2[16],hi2[16]; for(int j=i+1;j<A;j++){ lo2[j]=lo[j]; hi2[j]=hi[j]; if(tau[j]>tau[i]){ if(v>lo2[j]) lo2[j]=v; } else { if(v<hi2[j]) hi2[j]=v; } }
            q[i]=pos; self(self,i+1,pos+1,lo2,hi2);
          }
        };
        for(int j=0;j<A;j++){ lo[j]=0; hi[j]=n+1; }
        dfs(dfs,0,0,lo,hi);
        // OR-zeta transform (superset closure): f(T) |= f(T minus bit b)
        for(int b=0;b<6;b++){ u64 M=M6[b]; int sh=1<<b; for(int w=0;w<nw;w++) W[w]|=(W[w]&M)<<sh; }
        for(int b=6;b<n;b++){ int d=1<<(b-6); for(int w=0;w<nw;w++) if(w&d) W[w]|=W[w^d]; }
        for(int w=0;w<nw;w++){ u64 ev= (__builtin_popcount(w)&1)? ~EVEN:EVEN; cv += __builtin_popcountll(W[w]&ev) - __builtin_popcountll(W[w]&~ev); }
        if(n&1) cv=-cv;
      }
      c[t]+=cv;
    }
  }
  fprintf(stderr,"total time %.1fs\n", std::chrono::duration<double>(std::chrono::steady_clock::now()-T0).count());
  // print
  auto pr=[&](i128 v){ char buf[64]; int p=63; buf[p]=0; bool neg=v<0; u128 u= neg? (u128)(-v):(u128)v; if(u==0) buf[--p]='0'; while(u>0){ buf[--p]='0'+(int)(u%10); u/=10;} if(neg) buf[--p]='-'; return string(buf+p); };
  // factorials and binomials in u128
  u128 fact[32]; fact[0]=1; for(int i=1;i<32;i++) fact[i]=fact[i-1]*i;
  auto C=[&](int n,int k)->u128{ u128 r=1; for(int i=1;i<=k;i++){ r=r*(n-k+i)/i; } return r; };
  for(int t=0;t<=K;t++){
    int n=A+t; i128 g=0;
    for(int r=A;r<=n;r++){ i128 w=(i128)(C(n,r)*C(n,r)*fact[n-r]); g+= w*c[r-A]; }
    i128 av=(i128)fact[n]-g;
    printf("r=%d c_r=%s clusters=%zu Av_%d=%s\n",n,pr(c[t]).c_str(),level[t].size(),n,pr(av).c_str());
  }
  return 0;
}
