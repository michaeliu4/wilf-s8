// classes_k.cpp -- number of one-move classes of k-point insertions of tau (Sigma_rho beta_0^{(k)}(rho)),
// together with g_k(tau) and the inflation-complex Euler characteristic sum (for comparison).
// One-move classes: occurrences of tau in rho (as position subsets) are adjacent iff they differ in one point.
// Usage: classes_k k tau
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
using namespace std;
static int A,K,N; static int tau[16];
static int par[4096];
static int f(int x){ while(par[x]!=x){ par[x]=par[par[x]]; x=par[x]; } return x; }
int main(int argc,char**argv){
  K=atoi(argv[1]); A=0; for(char*c=argv[2];*c;c++) tau[A++]=*c-'0'; N=A+K;
  vector<int> p(N); for(int i=0;i<N;i++) p[i]=i+1;
  long long g=0, classes=0;
  // precompute all A-subsets of [N] as bitmasks
  vector<int> subs; for(int m=0;m<(1<<N);m++) if(__builtin_popcount(m)==A) subs.push_back(m);
  do{
    vector<int> occ;
    for(int m: subs){ int q[16],k=0; for(int i=0;i<N;i++) if(m>>i&1) q[k++]=p[i];
      bool ok=true; for(int i=0;i<A&&ok;i++) for(int j=i+1;j<A;j++) if((q[i]<q[j])!=(tau[i]<tau[j])){ok=false;break;}
      if(ok) occ.push_back(m); }
    if(occ.empty()) continue;
    g++;
    int m=occ.size(); for(int i=0;i<m;i++) par[i]=i;
    for(int i=0;i<m;i++) for(int j=i+1;j<m;j++) if(__builtin_popcount(occ[i]&occ[j])==A-1){ int a=f(i),b=f(j); if(a!=b) par[a]=b; }
    int c=0; for(int i=0;i<m;i++) if(f(i)==i) c++;
    classes+=c;
  } while(next_permutation(p.begin(),p.end()));
  printf("%s k=%d g_k=%lld classes=%lld diff=%lld\n",argv[2],K,g,classes,classes-g);
  return 0;
}
