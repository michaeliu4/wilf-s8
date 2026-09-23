// Exact simultaneous classical-pattern containment enumeration.
// C++17 with OpenMP; no other libraries.
// Enumerates one representative of each D4 orbit in S_n, counts DISTINCT
// length-8 patterns, weights by domain orbit size, and divides by target orbit size.
// Output rows indexed by ordinary lexicographic (Lehmer) rank in S_8.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
#include <chrono>
#include <omp.h>
using U64=uint64_t;
constexpr int M=8,K=40320;
int n;
std::array<int,K> symrep, osize, code_to_lex;
std::array<std::array<int,M>,K> patterns;
U64 factorial(int t){U64 r=1;for(int i=2;i<=t;++i)r*=i;return r;}
int lexrank(const std::array<int,M>&p){int r=0;for(int i=0;i<M;++i){int s=0;for(int j=i+1;j<M;++j)s+=p[j]<p[i];r=r*(M-i)+s;}return r;}
int insertioncode(const std::array<int,M>&p){int r=0;unsigned mask=0;for(int i=0;i<M;++i){r=r*(i+1)+__builtin_popcount(mask&((1u<<p[i])-1));mask|=1u<<p[i];}return r;}
void init(){
  std::array<int,M>p;std::iota(p.begin(),p.end(),0);int rank=0;
  do{
    patterns[rank]=p;code_to_lex[insertioncode(p)]=rank;
    std::array<int,M>inv;for(int i=0;i<M;++i)inv[p[i]]=i;
    std::array<int,8>o;
    for(int t=0;t<8;++t){auto src=(t&4)?inv:p;std::array<int,M>q;for(int i=0;i<M;++i){int v=src[(t&1)?M-1-i:i];q[i]=(t&2)?M-1-v:v;}o[t]=lexrank(q);}
    std::sort(o.begin(),o.end());symrep[rank]=o[0];osize[rank]=std::unique(o.begin(),o.end())-o.begin();++rank;
  }while(std::next_permutation(p.begin(),p.end()));
}
struct Worker{
  uint32_t epoch=0;std::array<uint32_t,K>seen{};std::array<U64,K>count{};
  std::array<int,16>p{},inv{};std::array<unsigned,16>bit{},less{};
  U64 orbits=0,weighttotal=0;int weight;
  int orbit_weight(){
    // No complement/reverse comparison can tie for n>1; reverse-complement can.
    int a=p[0];
    if(a>n-1-a || a>p[n-1] || a>n-1-p[n-1])return 0;
    for(int i=0;i<n;++i)inv[p[i]]=i;
    for(int x:{inv[0],n-1-inv[0],inv[n-1],n-1-inv[n-1]})if(x<a)return 0;
    int stabilizer=1;
    for(int t=1;t<8;++t){
      bool inverse=t&4,reverse=t&1,comp=t&2;auto &src=inverse?inv:p;
      int compare=0;
      for(int i=0;i<n;++i){int v=src[reverse?n-1-i:i];if(comp)v=n-1-v;if(v!=p[i]){compare=(v>p[i]?1:-1);break;}}
      if(compare<0)return 0;
      if(compare==0)++stabilizer;
    }
    assert(8%stabilizer==0);return 8/stabilizer;
  }
  template<int depth> inline void visit(int start,unsigned mask,int code){
    // depth is the number selected before this call.
    for(int i=start;i<=n-(M-depth);++i){
      int c=code*(depth+1)+__builtin_popcount(mask&less[i]);
      if constexpr(depth==M-1){
        if(seen[c]!=epoch){seen[c]=epoch;count[symrep[code_to_lex[c]]]+=weight;}
      }else visit<depth+1>(i+1,mask|bit[i],c);
    }
  }
  void process(){
    weight=orbit_weight();if(!weight)return;
    ++orbits;weighttotal+=weight;++epoch;assert(epoch!=0);
    for(int i=0;i<n;++i){bit[i]=1u<<p[i];less[i]=bit[i]-1;}
    visit<0>(0,0,0);
  }
};
int main(int argc,char**argv){
  if(argc<3){std::cerr<<"usage: count_all n output.csv [threads]\n";return 2;}
  n=std::stoi(argv[1]);if(n<M || n>13){std::cerr<<"require 8<=n<=13\n";return 2;}
  int threads=argc>3?std::stoi(argv[3]):4;
  if(threads<1 || threads>256){std::cerr<<"require 1<=threads<=256\n";return 2;}
  omp_set_num_threads(threads);init();
  std::vector<std::pair<int,int>>tasks;
  for(int a=0;a<=(n-1)/2;++a)for(int b=0;b<n;++b)if(a!=b)tasks.push_back({a,b});
  std::vector<Worker>workers(threads);auto begin=std::chrono::steady_clock::now();
  #pragma omp parallel for schedule(dynamic,1)
  for(int t=0;t<(int)tasks.size();++t){
    auto&w=workers[omp_get_thread_num()];auto [a,b]=tasks[t];w.p[0]=a;w.p[1]=b;int k=2;
    for(int v=0;v<n;++v)if(v!=a&&v!=b)w.p[k++]=v;
    do{w.process();}while(std::next_permutation(w.p.begin()+2,w.p.begin()+n));
  }
  std::array<U64,K>count{};U64 orbits=0,wt=0;
  for(auto&w:workers){orbits+=w.orbits;wt+=w.weighttotal;for(int i=0;i<K;++i)count[i]+=w.count[i];}
  assert(wt==factorial(n));
  std::ofstream out(argv[2]);if(!out){std::cerr<<"cannot open output\n";return 2;}out<<"rank,pattern,contains_"<<n<<",avoids_"<<n<<"\n";
  for(int i=0;i<K;++i){assert(count[symrep[i]]%osize[i]==0);U64 c=count[symrep[i]]/osize[i];assert(c<=factorial(n));out<<i<<",";for(int x:patterns[i])out<<x+1;out<<","<<c<<","<<factorial(n)-c<<"\n";}
  double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
  std::cout<<"n="<<n<<" domain_orbits="<<orbits<<" weighted_domain="<<wt<<" elapsed="<<sec<<"\n";
}
