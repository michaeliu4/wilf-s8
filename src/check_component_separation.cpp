// Exhaustively group all two-point deletions of every host of length a+2.
// Each resulting (pattern, host) group is exactly its deletion graph.
// Check separation of the NON-ISOLATED components, without using returns.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
struct Edge { uint64_t key; int u,v; bool operator<(const Edge& b) const {return key<b.key;} };
struct Stats {uint64_t hosts=0, components=0, pairs=0, failures=0; int maximum=0; std::string witness;};
std::string decode(uint64_t key,int a){std::string s(a,'0');for(int j=a-1;j>=0;--j){s[j]=char('0'+(key&15));key>>=4;}return s;}
std::string word(const std::vector<int>& p){std::string s;for(int v:p)s+=char('0'+v);return s;}
uint64_t fact(int a){uint64_t v=1;for(int j=2;j<=a;++j)v*=j;return v;}
uint64_t C2(uint64_t a){return (a*a*a*a+2*a*a*a+a*a+4*a+4)/2;}
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("usage: check_component_separation MAX_A OUTPUT.csv (1<=MAX_A<=7)");
 std::string arg=argv[1];size_t consumed=0;int maxa=std::stoi(arg,&consumed);
 if(consumed!=arg.size()||maxa<1||maxa>7)throw std::runtime_error("MAX_A must be in 1..7");
 std::ofstream file(argv[2]);if(!file)throw std::runtime_error("cannot open output CSV");
 file<<"a,pattern,containing_hosts,component_total,component_pairs_tested,separation_failures,max_beta0,first_max_witness\n";
 uint64_t failures=0;
 for(int a=1;a<=maxa;++a){int n=a+2;std::vector<int> p(n);std::iota(p.begin(),p.end(),1);std::map<uint64_t,Stats> stats;
  uint64_t hosts=0,deletions=0,groups=0,pairs=0;int maxbeta=0;
  do{++hosts;std::vector<Edge> edges;edges.reserve(n*(n-1)/2);
   for(int u=0;u<n;++u)for(int v=u+1;v<n;++v){uint64_t key=0;
    for(int i=0;i<n;++i)if(i!=u&&i!=v)key=(key<<4)|(p[i]-(p[u]<p[i])-(p[v]<p[i]));
    edges.push_back({key,u,v});++deletions;}
   std::sort(edges.begin(),edges.end());
   for(size_t lo=0;lo<edges.size();){size_t hi=lo+1;while(hi<edges.size()&&edges[hi].key==edges[lo].key)++hi;
    std::array<int,9> parent;std::iota(parent.begin(),parent.end(),0);unsigned active=0;
    auto root=[&](int x){while(parent[x]!=x){parent[x]=parent[parent[x]];x=parent[x];}return x;};
    for(size_t i=lo;i<hi;++i){int u=edges[i].u,v=edges[i].v;active|=(1u<<u)|(1u<<v);parent[root(u)]=root(v);}
    std::array<int,9> minp,maxp,minv,maxv;minp.fill(n);maxp.fill(-1);minv.fill(n+1);maxv.fill(-1);
    for(int i=0;i<n;++i)if(active&(1u<<i)){int r=root(i);minp[r]=std::min(minp[r],i);maxp[r]=std::max(maxp[r],i);minv[r]=std::min(minv[r],p[i]);maxv[r]=std::max(maxv[r],p[i]);}
    std::vector<int> comp;for(int i=0;i<n;++i)if(maxp[i]>=0)comp.push_back(i);
    auto& s=stats[edges[lo].key];++s.hosts;s.components+=comp.size();++groups;
    if((int)comp.size()>s.maximum){s.maximum=(int)comp.size();s.witness=word(p);}maxbeta=std::max(maxbeta,s.maximum);
    for(size_t i=0;i<comp.size();++i)for(size_t j=i+1;j<comp.size();++j){int r=comp[i],t=comp[j];++s.pairs;++pairs;
     bool horizontal=maxp[r]<minp[t]||maxp[t]<minp[r];bool vertical=maxv[r]<minv[t]||maxv[t]<minv[r];
     if(!horizontal||!vertical){++s.failures;++failures;std::cerr<<"FAIL tau="<<decode(edges[lo].key,a)<<" host="<<word(p)<<"\n";}}
    lo=hi;}
  }while(std::next_permutation(p.begin(),p.end()));
  if(hosts!=fact(n)||deletions!=fact(n)*n*(n-1)/2||stats.size()!=fact(a))throw std::runtime_error("exhaustive coverage mismatch");
  for(const auto& kv:stats){const auto&s=kv.second;if(s.components!=C2(a))throw std::runtime_error("component total differs from proved C2");
   file<<a<<','<<decode(kv.first,a)<<','<<s.hosts<<','<<s.components<<','<<s.pairs<<','<<s.failures<<','<<s.maximum<<','<<s.witness<<'\n';}
  std::cout<<"a="<<a<<" patterns="<<stats.size()<<" hosts="<<hosts<<" deletion_pairs="<<deletions<<" containing_pairs="<<groups<<" component_pairs_tested="<<pairs<<" max_beta0="<<maxbeta<<" failures="<<failures<<'\n';
 }
 file.flush();if(!file)throw std::runtime_error("output write failed");return failures?1:0;
 }catch(const std::exception&e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 2;}}
