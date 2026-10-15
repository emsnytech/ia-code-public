import json,re,collections,random,sys
p=json.load(open('build/prs.json'))
I=re.I
def any_(pat,s): return re.search(pat,s,I) is not None
SEC=r'secur|sécurit|\bcsp\b|content.security|\bxss\b|csrf|vuln[ée]rab|\bcve\b|brakeman|\b2fa\b|\botp\b|\bmfa\b|double authentif|r[ée]-?authentif|re-authenticate|mot de passe|password|\bsessions?\b|rate.?limit|sanitiz|injection|antivirus|\bvirus|chiffr|encrypt|\bsecrets?\b|bruteforce|brute.force|spam|captcha|permission|unauthori|non autoris|forbidden|\bpentest|audit de s'
A11Y=r'a11y|accessib|\brgaa\b|\baria\b|lecteur d.écran|screen.?reader|contraste|contrast|\balt\b|navigation clavier|keyboard'
DEP=r'^\s*(chore\(deps?\)|chore\(dep\)|build\(deps?\)|bump|upgrade|mont[ée]e de version)|dependabot|\bbump\b|\bruby [0-9]|\brails [0-9]|\bdsfr [0-9]|upgrade|mise à jour (de |des )?(gem|d[ée]pendance)|\bgems?\b|dependencies|d[ée]pendances|\byarn\b|\bnpm\b|\bbun\b|\bnode [0-9]'
PERF=r'\bperf|n\+1|n1-query|optimi[sz]|\blent|slow|\bcache|\bindex(es)?\b|timeout|m[ée]moire|memory|eager|preload|acc[ée]l[ée]r|faster|plus rapide'
TEST=r'^\s*(test|tests|spec|ci)\b|\bspecs?\b|rubocop|\blint|\bflaky|\bci\b|github action|test-optimization|\bcoverage|playwright|selenium|system test'
API=r'\bapi\b|graphql|webhook|api.?entreprise|api.?particulier|france.?connect|agent.?connect|pro.?connect|\bsiret|\binsee|\brna\b|\brnf\b|chorus|r[ée]f[ée]rentiel|referentiel|interop|\bsso\b|oauth|openid|\bjeton|token api|api_token|annuaire.?[ée]ducation|api.?g[ée]o|apigeo|\bban\b'
DESIGN=r'design|\bdsfr|\bcss\b|\bscss|\bui\b|\bux\b|look and feel|dark.?mode|mode sombre|mise en page|affichage|maquette|\bstyle|\bic[oô]ne|\bicon|responsive|\bmobile|\bsticky|\bfooter|\bheader|\bmenu|\bbouton|\bbutton|\bmodal|tableau de bord|\bnouveau look|redesign|refonte|ergonom|\bcard|\bbadge|\bcombobox|layout'
CONTENT=r'wording|\bi18n|traduction|translat|\bfaq\b|\btextes?\b|\bcopy\b|orthograph|\btypo\b|coquille|mentions l[ée]gales|documentation|\bdoc\b|\bwordings?\b|r[ée]daction|formulation|reformul'
def nature(x):
    t=x['title']+' '+x['branch']
    files=x['files']
    if any_(SEC,t): return 'Sécurité'
    if any_(A11Y,t): return 'Accessibilité'
    if any_(DEP,t) or (files and all(re.search(r'(Gemfile|package\.json|bun\.lock|yarn\.lock|\.ruby-version|Gemfile\.lock|\.nvmrc|\.tool-versions)$',f) for f in files)): return 'Dépendances'
    if any_(TEST,t) or (files and all(re.match(r'(spec|test)/|\.github/',f) for f in files)): return 'Tests & qualité'
    if any_(PERF,t): return 'Performance'
    if any_(API,t): return 'API & interopérabilité'
    if files and all(re.search(r'\.(s?css|svg|png)$|app/assets/stylesheets',f) for f in files): return 'Design & ergonomie'
    if any_(DESIGN,t) and x['cat'] in ('feat','fix','other'): return 'Design & ergonomie'
    if files and all(re.search(r'config/locales/|\.yml$|\.md$|doc/',f) for f in files): return 'Contenus & libellés'
    if any_(CONTENT,t) and x['cat'] in ('feat','fix','other'): return 'Contenus & libellés'
    if x['cat']=='feat' and not re.search(r'\betq\s*:?\s*(la\s*)?(tech|d[ée]v)',t,I): return 'Fonctionnalité'
    if x['cat']=='feat': return 'Technique & maintenance'
    if x['cat']=='fix': return 'Correctif'
    if x['cat']=='tech': return 'Technique & maintenance'
    # fallback by files
    if files and sum(1 for f in files if f.startswith(('app/views','app/components','app/javascript'))) > len(files)/2: return 'Fonctionnalité'
    return 'Technique & maintenance'
PUB=[('Usager',r'\betq\s*(un\s*)?usag|\busagers?\b|\bd[ée]posant|\buser\b|\bdemandeur|\bcitoyen|\bbrouillon'),
     ('Instructeur',r'\betq\s*(un\s*)?instruct|\binstructeurs?\b|\binstruction\b|\bgroupe.?instructeur'),
     ('Expert',r'\bexperts?\b|\bavis\b'),
     ('Administrateur',r'\betq\s*(un\s*)?admin(?!\s*super)|\badministrateurs?\b|\badmins?\b(?<!super admin)|\b[ée]diteur de champ|\btype.?de.?champ|\brévision|\bpublication|\bd[ée]marche\b'),
     ('Super-admin & opérateurs',r'super.?admin|\bmanager\b|\bop[ée]rateur|\bsuperadmin|\bbackoffice|\bhelpscout|\bcrisp|\bsupport\b'),
     ('API & intégrateurs',r'\bapi\b|graphql|webhook|\bint[ée]grateur')]
PUBF=[('Usager','app/controllers/users/'),('Instructeur','app/controllers/instructeurs/'),('Expert','app/controllers/experts/'),('Administrateur','app/controllers/administrateurs/'),('Super-admin & opérateurs','app/controllers/manager/'),('API & intégrateurs','app/graphql/'),('API & intégrateurs','app/controllers/api/'),
      ('Usager','app/views/users/'),('Instructeur','app/views/instructeurs/'),('Administrateur','app/views/administrateurs/'),('Administrateur','app/components/procedure'),('Administrateur','app/components/types_de_champ_editor'),('Usager','app/components/editable_champ'),('Instructeur','app/components/instructeurs/'),('Usager','app/components/dossiers/'),('Super-admin & opérateurs','app/views/manager/'),('Super-admin & opérateurs','app/dashboards/')]
def public(x):
    t=x['title']+' '+x['branch'].replace('-',' ').replace('_',' ')
    m=re.search(r'\betq\s*:?\s*(un |une |l\')?\s*(super.?admin|usag|instruct|admin|expert|op[ée]rat|tech|d[ée]v|int[ée]grat|api)',t,I)
    if m:
        k=m.group(2).lower()
        if k.startswith('super'): return 'Super-admin & opérateurs'
        if k.startswith('usag'): return 'Usager'
        if k.startswith('instr'): return 'Instructeur'
        if k.startswith('admin'): return 'Administrateur'
        if k.startswith('exp'): return 'Expert'
        if k.startswith('op'): return 'Super-admin & opérateurs'
        if k.startswith(('api','int')): return 'API & intégrateurs'
        return 'Équipe technique'
    for name,pat in PUB:
        if re.search(pat,t,I): return name
    c=collections.Counter()
    for f in x['files']:
        for name,pre in PUBF:
            if f.startswith(pre): c[name]+=1
    if c: return c.most_common(1)[0][0]
    return 'Équipe technique' if x['cat'] in ('tech',) or x['files'] and not any(f.startswith(('app/views','app/components','app/javascript','app/controllers','app/graphql')) for f in x['files']) else 'Transverse'
for x in p:
    x['nature']=nature(x); x['public']=public(x)
json.dump(p,open('build/prs.json','w'),ensure_ascii=False)
q=[x for x in p if x['prod']]
print(collections.Counter(x['nature'] for x in q).most_common())
print(collections.Counter(x['public'] for x in q).most_common())
if len(sys.argv)>1:
    random.seed(int(sys.argv[1]))
    for nat in sorted(set(x['nature'] for x in q)):
        s=[x for x in q if x['nature']==nat]
        for x in random.sample(s,min(6,len(s))): print(nat[:12],'|',x['public'][:10],'|',x['title'][:95])
