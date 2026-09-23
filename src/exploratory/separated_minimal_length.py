import sys
def exists(a,d):
    # is there a permutation of [a] with max(j-i,|t_j-t_i|) >= d for all i<j, i.e. |t_j - t_i| >= d whenever j-i < d
    used=[False]*(a+1); seq=[]
    def rec():
        if len(seq)==a: return True
        for v in range(1,a+1):
            if used[v]: continue
            if all(abs(v-seq[-k])>=d for k in range(1,min(d-1,len(seq))+1)):
                used[v]=True; seq.append(v)
                if rec(): return True
                seq.pop(); used[v]=False
        return False
    return rec(), list(seq)
for d in (3,4):
    for a in range(2,21):
        ok,w=exists(a,d)
        print(f"d_inf>={d}: length {a}: {'exists, e.g. '+''.join(chr(48+x) if x<10 else chr(55+x) for x in w) if ok else 'none'}")
