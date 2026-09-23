# clusternums.py: cluster numbers c_r(tau) (r = a..a+K) by triangular inversion of
#   g_k(tau) = (a+k)! - |Av_{a+k}(tau)| = sum_{r=a}^{a+k} C(a+k,r)^2 (a+k-r)! c_r(tau),
# using the automaton counter for |Av_n|.  Also prints j(tau) = C_2(a) - g_2(tau) (Ray-West), and the identities
#   c_{a+1} = -2a,   c_{a+2} = K(a) - j,   K(a) = C_2(a) - 2 C(a+2,2)^2 + 2a(a+2)^2.
# Usage: clusternums.py a K   (all patterns of length a; K = number of extra points, needs |Av_{a+K}|)
import sys, subprocess, itertools
if not __debug__: raise RuntimeError("Run without -O/PYTHONOPTIMIZE: assertions are verification checks")
from math import comb, factorial
a=int(sys.argv[1]); K=int(sys.argv[2])
def Av(p,n): return int(subprocess.run(['./autom',p]+[str(n)]*n,capture_output=True,text=True,check=True).stdout.split()[0])
C2=(a**4+2*a**3+a**2+4*a+4)//2
Kc=C2-2*comb(a+2,2)**2+2*a*(a+2)**2
print("# a=%d  C_2(a)=%d  K(a)=%d ; columns: tau  j  c_{a+1} .. c_{a+%d}  |Av_{a+1}| .. |Av_{a+%d}|"%(a,C2,Kc,K,K))
for p in itertools.permutations(range(1,a+1)):
    ps=''.join(map(str,p))
    av=[Av(ps,a+k) for k in range(1,K+1)]
    g=[factorial(a+k)-av[k-1] for k in range(1,K+1)]
    c=[1]
    for k in range(1,K+1):
        n=a+k; s=sum(comb(n,r)**2*factorial(n-r)*c[r-a] for r in range(a,n))
        c.append(g[k-1]-s)
    j=C2-g[1] if K>=2 else None
    assert c[1]==-2*a
    if K>=2: assert c[2]==Kc-j
    print(ps, j, ' '.join(str(x) for x in c[1:]), ' ', ' '.join(str(x) for x in av))
