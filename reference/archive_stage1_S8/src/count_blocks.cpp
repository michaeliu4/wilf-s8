// Exact simultaneous counts for selected classical patterns of length 8.
// Partition S_n into blocks with an ordered prefix and W remaining values.
// Within each block, represent all W! orders of the remaining values by a bitmap.
// A target occurrence is split between prefix and tail. Union tail-order bitmaps
// to count DISTINCT containing permutations. Complement symmetry halves prefixes.
// Uses C++17 and OpenMP; no sampling and no guessed recurrences.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
#include <omp.h>
using U64=uint64_t;
constexpr int M=8,K=40320;
constexpr int fact[]={1,1,2,6,24,120,720,5040,40320};
U64 factorial(int n){U64 a=1;for(int i=2;i<=n;++i)a*=i;return a;}
int rank_perm(const std::vector<int>&p){int r=0,m=p.size();for(int i=0;i<m;++i){int s=0;for(int j=i+1;j<m;++j)s+=p[j]<p[i];r=r*(m-i)+s;}return r;}
std::vector<int> unrank(int rank,int m){std::vector<int>v(m),p;std::iota(v.begin(),v.end(),0);for(int i=m;i>0;--i){int j=rank/fact[i-1];rank%=fact[i-1];p.push_back(v[j]);v.erase(v.begin()+j);}return p;}
struct Entry{uint16_t id,suffix_rank;};
struct Info{int k,ell;std::array<int,8>indices,coeff;};
struct Choice{int mask,base,add,del;};

template<int W>struct Counter{
 static constexpr int Words=(fact[W]+63)/64;
 struct Bitmap{std::array<U64,Words>b{};std::array<uint8_t,Words> nonzero{};uint8_t n_nonzero=0;};
 int n,plen,ntarget,nactual;
 std::vector<int>targets;
 std::vector<std::vector<int>>actual;
 std::array<std::vector<int>,9>offset;
 std::array<std::vector<Entry>,9>entry;
 std::vector<Info>infos;
 std::array<std::vector<Choice>,W+1>choices;
 std::array<int,1<<W>base;
 std::vector<Bitmap>bitmaps;
 Counter(int nn,const char*filename):n(nn),plen(nn-W){
  if(n<8 || plen<2 || n>15)throw std::runtime_error("unsupported n for tail width");
  std::ifstream f(filename);if(!f)throw std::runtime_error("cannot open target ranks");int r;
  while(f>>r){if(r<0||r>=K)throw std::runtime_error("bad target rank");targets.push_back(r);}
  std::sort(targets.begin(),targets.end());targets.erase(std::unique(targets.begin(),targets.end()),targets.end());ntarget=targets.size();nactual=2*ntarget;
  if(!ntarget)throw std::runtime_error("empty target list");
  if(nactual>65535)throw std::runtime_error("too many targets");
  for(int t:targets){auto p=unrank(t,8),q=p;for(int&v:q)v=7-v;actual.push_back(p);actual.push_back(q);}
  for(int k=std::max(0,M-W);k<=std::min(M,plen);++k){
   int ell=M-k,N=K/fact[ell];offset[k].assign(N+1,0);
   for(auto&p:actual)++offset[k][rank_perm(p)/fact[ell]+1];
   for(int j=1;j<=N;++j)offset[k][j]+=offset[k][j-1];
   entry[k].resize(nactual);auto at=offset[k];
   for(int id=0;id<nactual;++id){auto&p=actual[id];int key=rank_perm(p)/fact[ell];std::vector<int>suffix(p.begin()+k,p.end());entry[k][at[key]++]={uint16_t(id),uint16_t(rank_perm(suffix))};}
  }
  for(int mask=0;mask<(1<<plen);++mask){int k=__builtin_popcount(unsigned(mask)),ell=M-k;if(k>M || ell<0 || ell>W)continue;
   Info s{};s.k=k;s.ell=ell;int j=0;for(int i=0;i<plen;++i)if(mask>>i&1){s.indices[j]=i;s.coeff[j]=fact[7-j]/fact[ell];++j;}infos.push_back(s);
  }
  int total=0;for(int mask=0;mask<(1<<W);++mask){base[mask]=total;total+=fact[__builtin_popcount(unsigned(mask))];}bitmaps.resize(total);
  for(int ell=0;ell<=W;++ell){int prev=-1;for(int j=0;j<(1<<W);++j){int mask=j^(j>>1);if(__builtin_popcount(unsigned(mask))!=ell)continue;Choice c{mask,base[mask],-1,-1};if(prev>=0){unsigned add=mask&~prev,del=prev&~mask;assert(__builtin_popcount(add)==1 && __builtin_popcount(del)==1);c.add=__builtin_ctz(add);c.del=__builtin_ctz(del);}choices[ell].push_back(c);prev=mask;}}
  std::vector<int>p(W);std::iota(p.begin(),p.end(),0);int prank=0;
  do{for(int posmask=0;posmask<(1<<W);++posmask){int valuemask=0;std::vector<int>s;for(int i=0;i<W;++i)if(posmask>>i&1){s.push_back(p[i]);valuemask|=1<<p[i];}auto&b=bitmaps[base[valuemask]+rank_perm(s)];b.b[prank/64]|=1ull<<(prank%64);}++prank;}while(std::next_permutation(p.begin(),p.end()));
  for(int mask=0;mask<(1<<W);++mask){int ell=__builtin_popcount(unsigned(mask));for(int r=0;r<fact[ell];++r){auto&b=bitmaps[base[mask]+r];int c=0;for(int j=0;j<Words;++j){c+=__builtin_popcountll(b.b[j]);if(b.b[j])b.nonzero[b.n_nonzero++]=j;}assert(c==fact[W]/fact[ell]);}}
 }
 struct Worker{
  Counter&z;
  std::array<int,16>p{},tail{};
  std::vector<U64>bits,count;
  std::vector<uint32_t>stamp;
  std::vector<int>touched;
  uint32_t epoch=0;U64 prefixes=0;
  Worker(Counter&zz):z(zz),bits(z.nactual*Words),count(z.ntarget),stamp(z.nactual){touched.reserve(z.nactual);}
  inline void add(int id,const Bitmap&b,int ell){
   U64*dst=bits.data()+id*Words;
   if(stamp[id]!=epoch){stamp[id]=epoch;touched.push_back(id);std::memcpy(dst,b.b.data(),Words*sizeof(U64));}
   else{
    if constexpr(W==5){dst[0]|=b.b[0];dst[1]|=b.b[1];}
    else{
     if(ell>=W-2){for(int h=0;h<b.n_nonzero;++h){int j=b.nonzero[h];dst[j]|=b.b[j];}}
     else{for(int j=0;j<Words;++j)dst[j]|=b.b[j];}
    }
   }
  }
  void process(unsigned used){
   ++epoch;assert(epoch);++prefixes;touched.clear();unsigned unused=((1u<<z.n)-1)^used;int t=0;
   while(unused){int v=__builtin_ctz(unused);unused&=unused-1;tail[t++]=v;}assert(t==W);
   for(const auto&s:z.infos){
    int k=s.k,ell=s.ell;unsigned selected=0;for(int j=0;j<k;++j)selected|=1u<<p[s.indices[j]];
    std::array<int,W>weight{};int a=0;
    for(int j=0;j<k;++j){int v=p[s.indices[j]],q=s.coeff[j];selected^=1u<<v;a+=q*__builtin_popcount(selected&((1u<<v)-1));for(int h=0;h<W;++h)weight[h]+=(tail[h]<v)*q;}
    int key=a;bool first=true;
    for(const auto&c:z.choices[ell]){
     if(first){unsigned mask=c.mask;while(mask){int h=__builtin_ctz(mask);mask&=mask-1;key+=weight[h];}first=false;}
     else key+=weight[c.add]-weight[c.del];
     assert(key>=0&&key+1<(int)z.offset[k].size());
     int begin=z.offset[k][key],end=z.offset[k][key+1];
     for(int j=begin;j<end;++j){const auto&e=z.entry[k][j];add(e.id,z.bitmaps[c.base+e.suffix_rank],ell);}
    }
   }
   for(int id:touched){U64 sum=0;const U64*src=bits.data()+id*Words;for(int j=0;j<Words;++j)sum+=__builtin_popcountll(src[j]);count[id/2]+=sum;}
  }
  void generate(int depth,unsigned used){
   if(depth==z.plen){process(used);return;}
   unsigned available=((1u<<z.n)-1)^used;
   while(available){int v=__builtin_ctz(available);available&=available-1;p[depth]=v;generate(depth+1,used|(1u<<v));}
  }
 };
 void run(const char*output,int threads){
  std::vector<std::pair<int,int>>tasks;
  for(int a=0;a<n;++a)for(int b=0;b<n;++b)if(a!=b&&std::make_pair(a,b)<std::make_pair(n-1-a,n-1-b))tasks.push_back({a,b});
  std::vector<Worker>workers;workers.reserve(threads);for(int i=0;i<threads;++i)workers.emplace_back(*this);
  omp_set_num_threads(threads);auto start=std::chrono::steady_clock::now();
  #pragma omp parallel for schedule(dynamic,1)
  for(int j=0;j<(int)tasks.size();++j){auto&w=workers[omp_get_thread_num()];auto[a,b]=tasks[j];w.p[0]=a;w.p[1]=b;w.generate(2,(1u<<a)|(1u<<b));}
  std::vector<U64>count(ntarget);U64 prefixes=0;for(auto&w:workers){prefixes+=w.prefixes;for(int j=0;j<ntarget;++j)count[j]+=w.count[j];}
  assert(prefixes*2*fact[W]==factorial(n));std::ofstream out(output);if(!out)throw std::runtime_error("cannot open output");out<<"rank,pattern,contains_"<<n<<",avoids_"<<n<<"\n";
  for(int j=0;j<ntarget;++j){assert(count[j]<=factorial(n));out<<targets[j]<<",";for(int v:unrank(targets[j],8))out<<v+1;out<<","<<count[j]<<","<<factorial(n)-count[j]<<"\n";}
  std::cout<<"n="<<n<<" tail_width="<<W<<" targets="<<ntarget<<" complement_prefix_orbits="<<prefixes<<" weighted_domain="<<prefixes*2*fact[W]<<" elapsed="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"\n";
 }
};
int main(int argc,char**argv){try{
 if(argc<4){std::cerr<<"usage: count_blocks n targets.txt output.csv [threads] [tail-width=5|6|7]\n";return 2;}
 int n=std::stoi(argv[1]),threads=argc>4?std::stoi(argv[4]):4,w=argc>5?std::stoi(argv[5]):5;
 if(threads<1 || threads>256)throw std::runtime_error("require 1<=threads<=256");
 if(w==5){Counter<5>c(n,argv[2]);c.run(argv[3],threads);}else if(w==6){Counter<6>c(n,argv[2]);c.run(argv[3],threads);}else if(w==7){Counter<7>c(n,argv[2]);c.run(argv[3],threads);}else throw std::runtime_error("tail width must be 5, 6, or 7");
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 2;}}
