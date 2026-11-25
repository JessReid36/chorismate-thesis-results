import os,re,csv,sys
S6=sys.argv[1];D=os.path.join(S6,"d56");H=627.5094740631;EV=27.211386245988
def E(run):
    p=os.path.join(D,run,"job.out")
    if not os.path.isfile(p):return None,"no output"
    t=open(p,errors="replace").read()
    if "ORCA TERMINATED NORMALLY" not in t:return None,"not normal"
    m=re.findall(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)",t)
    return (float(m[-1]) if m else None),"ok"
out={}
for lv in("SV","TZ"):
    cR,_=E(lv+"_C_ctl_R");cT,_=E(lv+"_C_ctl_TS");b0=(cT-cR)*H
    for n in(3,4,5,6,8,10,12,15,20):
        for k in(1,2,3):
            d="S_n%02d_k%d"%(n,k)
            e={x:E("%s_%s_%s"%(lv,d,x))[0] for x in("di_R","di_TS","mo_R","mo_TS")}
            dde=None if None in(e["di_R"],e["di_TS"]) else (e["di_TS"]-e["di_R"])*H-b0
            bR=None if None in(e["di_R"],e["mo_R"]) else (e["mo_R"]-e["di_R"])*EV
            bT=None if None in(e["di_TS"],e["mo_TS"]) else (e["mo_TS"]-e["di_TS"])*EV
            out[(d,lv)]=(dde,bR,bT)
    print(lv,"control barrier %.4f"%b0)
rows=list(csv.DictReader(open(os.path.join(S6,"d56_designs.tsv")),delimiter="\t"))
print("columns:",list(rows[0].keys()))
json=__import__("json");json.dump({"%s|%s"%k:v for k,v in out.items()},open(sys.argv[2],"w"))
for d in sorted(set(k[0] for k in out)):
    s=out[(d,"SV")];t=out[(d,"TZ")]
    f=lambda x:"   -   " if x is None else "%+8.4f"%x
    print(d,"SV",f(s[0]),f(s[1]),f(s[2]),"| TZ",f(t[0]),f(t[1]),f(t[2]))
