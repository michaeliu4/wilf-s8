// Automaton counter: number of p-avoiding full placements on the Ferrers board given by a Dyck word (or column heights).
// State = active permutation (encoded u64, 4 bits/entry, length in top 4 bits). O: append last entry of every rank; C: delete max.
#include <cstdio>
#include <cstdint>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <unordered_map>
#include <string>
#include <algorithm>
using namespace std;
typedef uint64_t u64; typedef unsigned __int128 u128;
static int m; static int pat[16];
static inline int len(u64 x){ return (int)(x>>60); }
static inline int at(u64 x,int i){ return (int)((x>>(4*i))&15); }
// does sigma' = sigma + x (x appended last, values >= x shifted) contain pat using the last point? sigma avoids pat.
static bool creates(const int* s, int h, int x){ // s has h entries (values 1..h), new last value x in 1..h+1 ; shifted array t
  int t[16]; for(int i=0;i<h;i++) t[i]= s[i]>=x? s[i]+1: s[i]; t[h]=x; int n=h+1;
  if(n<m) return false;
  // choose m-1 positions among first h to combine with last (index h); pattern's last entry must correspond to position h
  int idx[16]; int k=m-1; for(int i=0;i<k;i++) idx[i]=i;
  if(k==0) return true;
  while(true){
    bool ok=true;
    for(int a=0;a<k&&ok;a++){ // compare with last
      if((t[idx[a]]<t[h])!=(pat[a]<pat[m-1])){ok=false;break;}
      for(int b=a+1;b<k;b++) if((t[idx[a]]<t[idx[b]])!=(pat[a]<pat[b])){ok=false;break;}
    }
    if(ok) return true;
    int i=k-1; while(i>=0 && idx[i]==h-k+i) i--; if(i<0) break; idx[i]++; for(int j=i+1;j<k;j++) idx[j]=idx[j-1]+1;
  }
  return false;
}
int main(int argc,char**argv){
  // usage: autom pattern heights...   (Ferrers board column heights, nonincreasing) ; converts to Dyck word
  for(char*c=argv[1];*c;c++) pat[m++]=*c-'0';
  vector<int> h; for(int i=2;i<argc;i++) h.push_back(atoi(argv[i])); int n=h.size();
  // Dyck word: opener i has n-h_i closers before it
  string w; int closers=0; for(int i=0;i<n;i++){ int need=n-h[i]; while(closers<need){ w+='C'; closers++; } w+='O'; } while(closers<n){ w+='C'; closers++; }
  unordered_map<u64,u128> cur; cur[(u64)0]=1; // empty state: length 0
  for(char ch: w){ unordered_map<u64,u128> nxt; nxt.reserve(cur.size()*4);
    for(auto& kv: cur){ u64 x=kv.first; int hgt=len(x); int s[16]; for(int i=0;i<hgt;i++) s[i]=at(x,i);
      if(ch=='O'){ for(int v=1; v<=hgt+1; v++){ if(creates(s,hgt,v)) continue; u64 y=0; for(int i=0;i<hgt;i++){ int t= s[i]>=v? s[i]+1:s[i]; y|=(u64)t<<(4*i);} y|=(u64)v<<(4*hgt); y|=(u64)(hgt+1)<<60; nxt[y]+=kv.second; } }
      else { if(hgt==0) continue; u64 y=0; int k=0; for(int i=0;i<hgt;i++){ if(s[i]==hgt) continue; y|=(u64)s[i]<<(4*k); k++; } y|=(u64)(hgt-1)<<60; nxt[y]+=kv.second; }
    }
    cur.swap(nxt);
  }
  u128 r=cur[(u64)0]; // print
  char buf[64]; int p=63; buf[p]=0; if(r==0){ buf[--p]='0'; } while(r>0){ buf[--p]='0'+(int)(r%10); r/=10; } printf("%s\n",buf+p);
}
