// Exact g3 from deletion minors and unions of integer boxes.
// This evaluator never constructs or pattern-tests a longer permutation.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
using Int=long long;
struct Del {array<int,3> p{}; int rank=0,id=0;};
struct Data { int m; vector<int> beta; Int choose[64][4]{}; array<vector<Del>,4> dels;array<vector<int>,4> ids;};
Data prepare(vector<int> b){Data z;z.m=b.size();z.beta=b;int m=z.m;
 if(m<1||m>50)throw runtime_error("Compiled evaluator supports lengths 1..50.");
 auto s=b;sort(s.begin(),s.end());for(int i=0;i<m;i++)if(s[i]!=i+1)throw runtime_error("Invalid permutation");
 for(int n=0;n<64;n++){z.choose[n][0]=1;for(int k=1;k<4;k++)z.choose[n][k]=(n?z.choose[n-1][k]+z.choose[n-1][k-1]:0);}
 for(int d=1;d<=min(3,m);d++){
  z.ids[d].resize(z.choose[m][d]); map<string,int> names;
  for(int a=1;a<=m;a++)for(int bb=(d>=2?a+1:m+1);bb<=m+1;bb++){
   if(d>=2&&bb>m)break;
   for(int c=(d==3?bb+1:m+1);c<=m+1;c++){
    if(d==3&&c>m)break;
    Del e;e.p={a,bb,c};e.rank=0;for(int j=0;j<d;j++)e.rank+=z.choose[e.p[j]-1][j+1];
    string key;for(int i=1;i<=m;i++){
     bool removed=false;for(int j=0;j<d;j++)removed|=(i==e.p[j]);if(removed)continue;
     int v=b[i-1];for(int j=0;j<d;j++)v-=b[e.p[j]-1]<b[i-1];key.push_back(char(v));}
    auto res=names.emplace(key,names.size());e.id=res.first->second;z.ids[d][e.rank]=e.id;z.dels[d].push_back(e);
    if(d!=3)break;
   }if(d==1)break;
  }
 }
 return z;
}
Int evaluate(const Data& z){int m=z.m,L=m+2;size_t volume=size_t(L)*L*L;vector<int> grid(volume);Int total=0;
 auto at=[L](int x,int y,int w){return (size_t(x)*L+y)*L+w;};
 for(int c0=0;c0<=m;c0++)for(int c1=c0;c1<=m;c1++)for(int c2=c1;c2<=m;c2++){
  array<int,3>c={c0,c1,c2};array<int,3>sigma={0,1,2};
  do{
   fill(grid.begin(),grid.end(),0);
   for(int mask=1;mask<8;mask++){
    int d=__builtin_popcount((unsigned)mask);if(d>m)continue;array<int,3>X{};int p=0;for(int j=0;j<3;j++)if(mask>>j&1)X[p++]=j;
    for(const Del&e:z.dels[d]){
     if(c[X[0]]>=e.p[0])continue;
     array<int,3>Q{},v{};int qr=0;
     for(int a=0;a<d;a++){int q=c[X[a]]+a+1;for(int j=0;j<d;j++)q-=e.p[j]<=c[X[a]];Q[a]=q;qr+=z.choose[q-1][a+1];v[a]=z.beta[q-1];}
     if(z.ids[d][qr]!=e.id)continue;
     bool good=true;for(int a=0;a<d;a++)for(int b=a+1;b<d;b++)if((sigma[X[a]]<sigma[X[b]])!=(v[a]<v[b]))good=false;
     if(!good)continue;
     array<int,3>removed{};for(int j=0;j<d;j++)removed[j]=z.beta[e.p[j]-1];sort(removed.begin(),removed.begin()+d);
     auto surviving=[&](int t){if(t==0)return 0;if(t==m-d+1)return m+1;int v=t;for(int j=0;j<d;j++)if(removed[j]<=v)v++;return v;};
     array<int,3>lo={0,0,0},hi={m,m,m};
     for(int a=0;a<d;a++){int t=v[a]-1;for(int b=0;b<d;b++)t-=v[b]<v[a];lo[sigma[X[a]]]=surviving(t);hi[sigma[X[a]]]=surviving(t+1)-1;}
     for(int bits=0;bits<8;bits++){int x=(bits&1)?hi[0]+1:lo[0],y=(bits&2)?hi[1]+1:lo[1],w=(bits&4)?hi[2]+1:lo[2];grid[at(x,y,w)]+=__builtin_popcount((unsigned)bits)%2?-1:1;}
    }
   }
   for(int x=1;x<L;x++)for(int y=0;y<L;y++)for(int w=0;w<L;w++)grid[at(x,y,w)]+=grid[at(x-1,y,w)];
   for(int x=0;x<L;x++)for(int y=1;y<L;y++)for(int w=0;w<L;w++)grid[at(x,y,w)]+=grid[at(x,y-1,w)];
   for(int x=0;x<L;x++)for(int y=0;y<L;y++)for(int w=1;w<L;w++)grid[at(x,y,w)]+=grid[at(x,y,w-1)];
   for(int a=0;a<=m;a++)for(int b=a;b<=m;b++)for(int w=b;w<=m;w++){int n=grid[at(a,b,w)];if(n<0)throw runtime_error("Negative box coverage");if(!n)total++;}
  }while(next_permutation(sigma.begin(),sigma.end()));
 }
 return total;
}
int main(int argc,char**argv){try{if(argc!=3)throw runtime_error("Usage: deletion_boxes cases.txt output.csv");ifstream in(argv[1]);ofstream out(argv[2]);if(!in||!out)throw runtime_error("Cannot open files");out<<"pattern,m,g3\n";string line;int num=0;while(getline(in,line)){if(line.empty())continue;stringstream ss(line);string x;vector<int>b;while(getline(ss,x,';'))b.push_back(stoi(x));auto z=prepare(b);Int ans=evaluate(z);out<<line<<','<<b.size()<<','<<ans<<'\n';out.flush();num++;if(num%100==0||b.size()>8)cerr<<"case="<<num<<" m="<<b.size()<<" g3="<<ans<<'\n';}}catch(exception&e){cerr<<e.what()<<'\n';return 1;}}
