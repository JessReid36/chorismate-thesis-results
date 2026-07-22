import math, os, sys
BARE={'reactant':{'homo':-3.4417,'o3':-0.163192},'product':{'homo':-3.4324,'o3':-0.189074}}
IDX={'C1':0,'O3':7,'C4':8,'C6':12}; FLOOR=2.0; OVERPOL=-0.15
def homo_lumo(p):
    L=open(p,errors='ignore').readlines(); s=[i for i,l in enumerate(L) if 'ORBITAL ENERGIES' in l]
    if not s: return None,None
    h=l=None
    for j in range(s[-1]+1,len(L)):
        q=L[j].split()
        if len(q)>=4 and q[0].isdigit():
            try: occ=float(q[1]); e=float(q[3])
            except ValueError: continue
            if occ>0.5: h=e
            elif l is None: l=e
        elif h is not None and L[j].strip() and '---' not in L[j] and not L[j].split()[0].isdigit(): break
    return h,l
def loewdin(p,idx):
    L=open(p,errors='ignore').readlines(); s=[i for i,l in enumerate(L) if 'LOEWDIN ATOMIC CHARGES' in l]
    if not s: return None
    for j in range(s[-1]+2,s[-1]+42):
        if j>=len(L): break
        q=L[j].replace(':',' ').split()
        if len(q)>=3 and q[0].isdigit() and int(q[0])==idx: return float(q[-1])
    return None
def rxyz(p):
    L=open(p,errors='ignore').readlines(); n=int(L[0].split()[0]); return [(float(x.split()[1]),float(x.split()[2]),float(x.split()[3])) for x in L[2:2+n]]
def rtrj(p):
    L=open(p,errors='ignore').readlines(); F=[]; i=0
    while i<len(L):
        try: n=int(L[i].split()[0])
        except: break
        F.append([(float(x.split()[1]),float(x.split()[2]),float(x.split()[3])) for x in L[i+2:i+2+n]]); i+=2+n
    return F
def rpc(p):
    L=open(p,errors='ignore').readlines(); n=int(L[0].split()[0]); return [(float(x.split()[0]),float(x.split()[1]),float(x.split()[2]),float(x.split()[3])) for x in L[1:1+n]]
def dd(a,b): return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2)
def mac(g,ch):
    best=(1e9,-1,0.0)
    for a in g:
        for qq,x,y,z in ch:
            v=dd(a,(x,y,z))
            if v<best[0]: best=(v,0,qq)
    return best
def stat(p):
    t=open(p,errors='ignore').read()
    if 'ORCA TERMINATED NORMALLY' not in t: return 'RUNNING/CRASH'
    if 'SCF NOT CONVERGED' in t: return 'SCF_FAIL'
    if 'HAS CONVERGED' in t or 'OPTIMIZATION RUN DONE' in t: return 'CONVERGED'
    return 'NOCONV'
base=sys.argv[1] if len(sys.argv)>1 else '.'
print("%-12s %-13s %8s %7s %7s %8s %9s %6s %6s  %s"%("tag","status","HOMOeV","O3q","dO3q","minDist","trajMin","O3C4","C1C6","verdict"))
for tag in sorted(os.listdir(os.path.join(base,'runs'))):
    rd=os.path.join(base,'runs',tag); out=os.path.join(rd,'job.out'); ep='product' if 'product' in tag else 'reactant'
    if not os.path.exists(out): print("%-12s MISSING"%tag); continue
    st=stat(out); homo,_=homo_lumo(out); o3q=loewdin(out,IDX['O3']); ch=rpc(os.path.join(rd,'design.pc'))
    fx=os.path.join(rd,'job.xyz'); g=rxyz(fx) if os.path.exists(fx) else rxyz(os.path.join(rd,'start.xyz'))
    md,_,_=mac(g,ch); tj=os.path.join(rd,'job_trj.xyz'); tmin=md
    if os.path.exists(tj):
        for fr in rtrj(tj):
            m,_,_=mac(fr,ch); tmin=min(tmin,m)
    o3c4=dd(g[IDX['O3']],g[IDX['C4']]); c1c6=dd(g[IDX['C1']],g[IDX['C6']])
    dq=(o3q-BARE[ep]['o3']) if o3q is not None else None
    fl=[]
    if st!='CONVERGED': fl.append(st)
    if homo is None or homo>=0: fl.append('SPILLOUT?')
    if dq is not None and dq<=OVERPOL: fl.append('OVERPOL')
    if tmin<FLOOR: fl.append('IMPLODE(%.2f)'%tmin)
    print("%-12s %-13s %8s %7s %7s %8.3f %9.3f %6.3f %6.3f  %s"%(tag,st,
        ('%.3f'%homo if homo is not None else 'NA'),('%.3f'%o3q if o3q is not None else 'NA'),
        ('%+.3f'%dq if dq is not None else 'NA'),md,tmin,o3c4,c1c6,'PASS' if not fl else ' '.join(fl)))
