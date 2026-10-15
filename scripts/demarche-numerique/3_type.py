import json,re,collections,random
p=json.load(open('build/prs.json'))
T=re.compile(r'^\s*(\[?tech\b|chore|refactor|test|tests|ci\b|build|deps?\b|bump|perf|task|i18n|docs?\b|style|revert|lint|rubocop|upgrade|update|maj\b|mise à jour|migration|dev\b|bundle|yarn|gem)',re.I)
TB=re.compile(r'^(auto/|dependabot|tech|chore|refactor|bump|upgrade|test|ci|deps|renovate|maj-|update-)',re.I)
F=re.compile(r'^\s*(fix|hotfix|bugfix|correctif|corrige|corrig|répare|repare|revert)|\bfix\b|correctif|régression|regression|\bbug\b',re.I)
FB=re.compile(r'^(us/)?(fix|hotfix|bugfix|bug)',re.I)
N=re.compile(r'^\s*(feat|feature|etq|en tant qu|us\b|add|ajout|ajoute|permet|nouveau|nouvelle|new|improve|amélior|ameliore|enhance|allow|support|implement|affiche|display|show|admin|instructeur|usager|api)',re.I)
NB=re.compile(r'^(us/|feat|feature|add|improve|enhance|new)',re.I)
def cat(x):
    t,b=x['title'],x['branch']
    if T.search(t): return 'tech'
    if F.search(t) or FB.search(b): return 'fix'
    if N.search(t) or NB.search(b): return 'feat'
    if TB.search(b): return 'tech'
    if re.search(r'^\s*(clean|remove|supprim|nettoy|migrat|migrate|spec|use |convert|drop |rename|move |extract|simplif|optimi|split)|feature.?flag|\bspec\b|selenium|vite|webpack|sentry|rubocop',t,re.I): return 'tech'
    if re.search(r'a11y|accessib|rgaa',t+' '+b,re.I): return 'fix'
    if re.search(r'refonte|maquette|mutation|graphql|un administrateur|un instructeur|un usager|les usagers|peut |pouvoir|prefill|préremp|tableau de bord|nouvel|export|email|e-mail|mail|dsfr|dark|page',t,re.I): return 'feat'
    return 'other'
for x in p: x['cat']=cat(x)
json.dump(p,open('build/prs.json','w'),ensure_ascii=False)
c=collections.Counter((x['merged'][:4],x['cat']) for x in p)
for y in range(2021,2027): print(y,{k:c[(str(y),k)] for k in ['feat','fix','tech','other']})
random.seed(3)
o=[x for x in p if x['cat']=='other']
for x in random.sample(o,25): print('O|',x['branch'][:30],'|',x['title'][:90])
f=[x for x in p if x['cat']=='feat']
for x in random.sample(f,15): print('F|',x['branch'][:30],'|',x['title'][:90])
