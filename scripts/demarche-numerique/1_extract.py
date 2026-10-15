import subprocess, re, json, sys
import os
R=os.environ.get('DN_REPO','sources/demarche.numerique.gouv.fr')
def g(*a): return subprocess.run(['git','-C',R,*a],capture_output=True,text=True).stdout
SINCE='2021-10-14'
# release tags ascending
raw=[l.split('|') for l in g('for-each-ref','--format=%(if)%(*objectname)%(then)%(*committerdate:unix)%(else)%(committerdate:unix)%(end)|%(creatordate:short)|%(refname:short)','refs/tags').splitlines()]
tags=sorted([(int(u),d,t) for u,d,t in raw if re.match(r'\d{4}-\d{2}-\d{2}(-\d+)?$',t) and d>='2021-09-01'])
tags=[(d,t) for u,d,t in tags]
rel={}  # merge sha -> (tag,date)
prev=None
for d,t in tags:
    args=['rev-list',t]+(['^'+prev] if prev else [])
    for s in g(*args).split():
        rel.setdefault(s,(t,d))
    prev=t
SEP='\x1e'
log=g('log','--first-parent','main','--since='+SINCE,'--format=%H%x1f%P%x1f%cs%x1f%s%x1f%b'+SEP)
prs=[]
for rec in log.split(SEP):
    rec=rec.strip('\n')
    if not rec: continue
    h,p,d,s,b=rec.split('\x1f')
    m=re.match(r'Merge pull request #(\d+) from ([^/]+)/(\S+)',s)
    parents=p.split()
    if m and len(parents)==2:
        num,branch=int(m.group(1)),m.group(3)
        title=b.strip().split('\n')[0] if b.strip() else branch
        body=g('log',f'{parents[0]}..{parents[1]}','--format=%s%n%b%n---')
        ncommits=int(g('rev-list','--count',f'{parents[0]}..{parents[1]}').strip() or 0)
        subjects=g('log',f'{parents[0]}..{parents[1]}','--format=%s').splitlines()
        claude=bool(re.search(r'co-authored-by:\s*claude|generated with \[?claude|claude\.ai/code|claude-session',body,re.I))
    else:
        num,branch,title,claude,ncommits,subjects=None,'',s,bool(re.search(r'co-authored-by:\s*claude|claude-session',b,re.I)),1,[s]
    r=rel.get(h)
    prs.append(dict(sha=h[:10],pr=num,branch=branch,title=title,merged=d,claude=claude,ncommits=ncommits,subjects=subjects[:40],release=r[0] if r else None,prod=r[1] if r else None))
json.dump(prs,open('build/prs.json','w'),ensure_ascii=False)
print(len(prs),sum(1 for x in prs if x['pr']),sum(1 for x in prs if x['release']),sum(x['claude'] for x in prs))
