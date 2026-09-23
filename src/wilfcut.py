import subprocess, itertools, sys
from collections import defaultdict
g=int(sys.argv[1]); NMAX=int(sys.argv[2])
def F(p,n): return int(subprocess.run(['./autom',p]+[str(n)]*n,capture_output=True,text=True).stdout.split()[0])
pats=[''.join(map(str,p)) for p in itertools.permutations(range(1,g+1))]
seq={p:[F(p,n) for n in range(g+1,NMAX+1)] for p in pats}
# number of classes as a function of cutoff
for cut in range(g+1,NMAX+1):
    cl=defaultdict(list)
    for p in pats: cl[tuple(seq[p][:cut-g])].append(p)
    print("cutoff n<=%d: %d classes"%(cut,len(cl)))
