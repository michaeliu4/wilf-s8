import sys, itertools
from math import factorial
def std(seq):
    s=sorted(seq); return tuple(s.index(x)+1 for x in seq)
def analyze(tau,k):
    a=len(tau); n=a+k; totchi=0; totb0=0; mism=0; examples=[]
    for rho in itertools.permutations(range(1,n+1)):
        Ds=[D for D in itertools.combinations(range(n),k) if std([rho[i] for i in range(n) if i not in D])==tau]
        if not Ds: continue
        # beta_0 of occurrence graph (differ in one point)
        par={D:D for D in Ds}
        def f(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for D,E in itertools.combinations(Ds,2):
            if len(set(D)&set(E))==k-1:
                r1,r2=f(D),f(E)
                if r1!=r2: par[r1]=r2
        b0=len(set(f(D) for D in Ds))
        # Euler characteristic of the inflation complex: sum over T (supersets of occurrences) of (-1)^{|T|-a} * I(rho|_T)
        # I(sigma) = number of ways sigma = tau[blocks]: count block structures directly
        chi=0
        for size in range(a,n+1):
            for T in itertools.combinations(range(n),size):
                sig=std([rho[i] for i in T]); m=len(sig)
                # count compositions of positions into a consecutive blocks such that contracting gives tau and each block is an interval in values
                cnt=0
                for cuts in itertools.combinations(range(1,m),a-1):
                    bounds=[0]+list(cuts)+[m]; ok=True; reps=[]
                    for i in range(a):
                        blk=sig[bounds[i]:bounds[i+1]]
                        if max(blk)-min(blk)!=len(blk)-1: ok=False; break
                        reps.append(min(blk))
                    if ok and std(reps)==tau: cnt+=1
                chi+= (-1)**(size-a)*cnt
        totchi+=chi; totb0+=b0
        if chi!=b0:
            mism+=1
            if len(examples)<5: examples.append((''.join(map(str,rho)),chi,b0))
    return totchi,totb0,mism,examples
tau=tuple(int(c) for c in sys.argv[1]); k=int(sys.argv[2])
print(sys.argv[1],"k=",k,analyze(tau,k))
