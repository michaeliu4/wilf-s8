// delgraph.cpp -- exhaustive verification of the two-point structure theorems for all patterns of length A.
// For every tau in S_A and every rho in S_{A+2} containing tau, build the deletion graph
//   E_rho = { {x,y} : rho minus {x,y} is order-isomorphic to tau },
// and compute: beta_0 (components), beta_1 (cycle rank), t = number of 3-intervals of rho all of whose
// three pairs are edges, s = number of pairs of disjoint bonds of rho all of whose four cross pairs are edges.
// Checks per rho:  (L2)  beta_1 = t + s;   (LE) leading-edge property: every edge {u,v} (u<v) that is the
// lex-largest edge of a cycle is the leading edge of a 3-interval triangle (v=u+1, {u-1,u,u+1} interval with
// all pairs edges) or of a bond square (v>=u+2, {u-1,u},{v-1,v} bonds, cross pairs edges).
// Sums per tau: sum beta_0 = C_2(A), sum(beta_0 - 1) = j(tau) = C_2(A) - g_2(tau), sum beta_1 = 2A(A+2).
// Usage: delgraph A [maxtau]   (prints one line per pattern if maxtau given, else summary)
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;
static int A,N; static int tau[12];
static bool isTau(const int* p,int n,int x,int y){ // rho minus positions x,y equals tau (pattern test)
  int q[12],k=0; for(int i=0;i<n;i++) if(i!=x&&i!=y) q[k++]=p[i];
  for(int i=0;i<A;i++) for(int j=i+1;j<A;j++) if((q[i]<q[j])!=(tau[i]<tau[j])) return false;
  return true;
}
int main(int argc,char**argv){
  A=atoi(argv[1]); N=A+2; long long maxtau = argc>2? atoll(argv[2]) : -1;
  vector<int> t(A); for(int i=0;i<A;i++) t[i]=i+1;
  long long C2=( (long long)A*A*A*A + 2LL*A*A*A + (long long)A*A + 4LL*A + 4 )/2;
  long long ntau=0, badL2=0, badLE=0, badSum=0, badB1=0;
  do{
    for(int i=0;i<A;i++) tau[i]=t[i];
    ntau++; if(maxtau>0 && ntau>maxtau) break;
    vector<int> p(N); for(int i=0;i<N;i++) p[i]=i+1;
    long long sb0=0, sb1=0, g2=0, st=0, ss=0;
    do{
      // edges
      int adj[12]; for(int i=0;i<N;i++) adj[i]=0; int ne=0;
      for(int x=0;x<N;x++) for(int y=x+1;y<N;y++) if(isTau(p.data(),N,x,y)){ adj[x]|=1<<y; adj[y]|=1<<x; ne++; }
      if(ne==0) continue;
      g2++;
      int V=0; for(int i=0;i<N;i++) if(adj[i]) V|=1<<i;
      // components
      int seen=0,b0=0;
      for(int i=0;i<N;i++) if((V>>i&1)&&!(seen>>i&1)){ b0++; int st_[12],sp=0; st_[sp++]=i; seen|=1<<i; while(sp){ int u=st_[--sp]; int m=adj[u]&~seen; while(m){ int v=__builtin_ctz(m); m&=m-1; seen|=1<<v; st_[sp++]=v; } } }
      int nv=__builtin_popcount(V); int b1=ne-nv+b0;
      // t: 3-intervals {i,i+1,i+2} with consecutive values and all pairs edges
      int tt=0;
      for(int i=0;i+2<N;i++){ int a_=p[i],b_=p[i+1],c_=p[i+2]; int mx=max(a_,max(b_,c_)), mn=min(a_,min(b_,c_)); if(mx-mn!=2) continue;
        if((adj[i]>>(i+1)&1)&&(adj[i]>>(i+2)&1)&&(adj[i+1]>>(i+2)&1)) tt++; }
      // s: disjoint bonds {x,x+1},{y,y+1}, x+1<y, all cross edges
      int ssq=0;
      for(int x=0;x+1<N;x++){ if(abs(p[x]-p[x+1])!=1) continue; for(int y=x+2;y+1<N;y++){ if(abs(p[y]-p[y+1])!=1) continue;
        if((adj[x]>>y&1)&&(adj[x]>>(y+1)&1)&&(adj[x+1]>>y&1)&&(adj[x+1]>>(y+1)&1)) ssq++; } }
      if(b1!=tt+ssq){ badL2++; if(badL2<=3){ printf("L2 fail tau="); for(int i=0;i<A;i++) printf("%d",tau[i]); printf(" rho="); for(int i=0;i<N;i++) printf("%d",p[i]); printf(" b1=%d t=%d s=%d\n",b1,tt,ssq);} }
      // leading edge property
      for(int u=0;u<N;u++) for(int v=u+1;v<N;v++) if(adj[u]>>v&1){
        // connectivity from u to v using edges lex-smaller than (u,v): edge (a,b),a<b, smaller iff a<u or (a==u && b<v)
        int reach=1<<u, frontier=1<<u;
        while(frontier){ int a=__builtin_ctz(frontier); frontier&=frontier-1; int m=adj[a]&~reach; while(m){ int b=__builtin_ctz(m); m&=m-1; int lo=min(a,b),hi=max(a,b); bool smaller = (lo<u) || (lo==u && hi<v); if(smaller){ reach|=1<<b; frontier|=1<<b; } } }
        if(!(reach>>v&1)) continue;
        bool ok=false;
        if(v==u+1){ if(u>=1){ int a_=p[u-1],b_=p[u],c_=p[v]; int mx=max(a_,max(b_,c_)),mn=min(a_,min(b_,c_)); ok = (mx-mn==2) && (adj[u-1]>>u&1) && (adj[u-1]>>v&1); } }
        else { if(u>=1 && abs(p[u-1]-p[u])==1 && abs(p[v-1]-p[v])==1) ok = (adj[u-1]>>(v-1)&1)&&(adj[u-1]>>v&1)&&(adj[u]>>(v-1)&1); }
        if(!ok){ badLE++; if(badLE<=3){ printf("LE fail tau="); for(int i=0;i<A;i++) printf("%d",tau[i]); printf(" rho="); for(int i=0;i<N;i++) printf("%d",p[i]); printf(" edge=(%d,%d)\n",u+1,v+1);} }
      }
      sb0+=b0; sb1+=b1; st+=tt; ss+=ssq;
    } while(next_permutation(p.begin(),p.end()));
    long long j = C2 - g2;
    if(sb0!=C2) badSum++;
    if(sb1!=2LL*A*(A+2)) badB1++;
    if(maxtau>0) { for(int i=0;i<A;i++) printf("%d",tau[i]); printf(" g2=%lld j=%lld sum_b0=%lld (C2=%lld) sum_b1=%lld t=%lld s=%lld\n",g2,j,sb0,C2,sb1,st,ss); }
  } while(next_permutation(t.begin(),t.end()));
  printf("A=%d patterns=%lld  L2 failures=%lld  LE failures=%lld  sum_b0!=C2: %lld  sum_b1!=2A(A+2): %lld\n",A,ntau-(maxtau>0&&ntau>maxtau?1:0),badL2,badLE,badSum,badB1);
  return 0;
}
