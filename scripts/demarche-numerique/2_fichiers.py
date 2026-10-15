import json,subprocess,os
from concurrent.futures import ThreadPoolExecutor
R=os.environ.get('DN_REPO','sources/demarche.numerique.gouv.fr')
p=json.load(open('build/prs.json'))
full=subprocess.run(['git','-C',R,'log','--first-parent','main','--since=2021-10-14','--format=%H'],capture_output=True,text=True).stdout.split()
m={h[:10]:h for h in full}
def f(x):
    h=m[x['sha']]
    out=subprocess.run(['git','-C',R,'diff','--name-only',h+'^1',h],capture_output=True,text=True).stdout.split('\n')
    return [o for o in out if o][:300]
with ThreadPoolExecutor(8) as ex: res=list(ex.map(f,p))
for x,r in zip(p,res): x['files']=r
json.dump(p,open('build/prs.json','w'),ensure_ascii=False)
print(sum(1 for x in p if not x['files']))
