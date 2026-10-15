"""Produit les trois fichiers du tableau de bord Démarche Numérique (data/demarche-numerique/)."""
import json, csv, collections, os
OUT = 'docs/data/demarche-numerique'
os.makedirs(OUT, exist_ok=True)
SINCE = os.environ.get('SINCE', '2021-10-14')
BASE = 'https://github.com/demarche-numerique/demarche.numerique.gouv.fr'
p = [x for x in json.load(open('build/prs.json')) if x['prod'] and x['prod'] >= SINCE]
months = sorted({x['prod'][:7] for x in p})

# 1. mensuel.csv — par mois et par type
agg = {mo: collections.Counter() for mo in months}
for x in p:
    a = agg[x['prod'][:7]]; a[x['cat']] += 1
    if x['claude']: a['claude_' + x['cat']] += 1; a['claude_all'] += 1
with open(f'{OUT}/mensuel.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['mois', 'fonctionnalites', 'fonctionnalites_avec_claude', 'correctifs', 'technique', 'non_classe', 'total', 'total_avec_claude'])
    for mo in months:
        a = agg[mo]
        w.writerow([mo, a['feat'], a['claude_feat'], a['fix'], a['tech'], a['other'], a['feat'] + a['fix'] + a['tech'] + a['other'], a['claude_all']])

# 2. categories_mensuel.csv — par mois, par nature et par public
c = collections.Counter()
for x in p:
    for axe, cat in (('nature', x['nature']), ('public', x['public'])):
        c[(x['prod'][:7], axe, cat, 'n')] += 1
        if x['claude']: c[(x['prod'][:7], axe, cat, 'c')] += 1
with open(f'{OUT}/categories_mensuel.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['mois', 'axe', 'categorie', 'n', 'n_avec_claude'])
    for k in sorted({k[:3] for k in c}): w.writerow([*k, c[(*k, 'n')], c[(*k, 'c')]])

# 3. mises_en_production.csv — une ligne par changement
TYPE = {'feat': 'Évolution', 'fix': 'Correctif', 'tech': 'Technique', 'other': 'Non classé'}
with open(f'{OUT}/mises_en_production.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['pr', 'titre', 'nature', 'public', 'type', 'mise_en_production', 'version', 'claude', 'lien'])
    for x in sorted(p, key=lambda x: (x['prod'], x['merged']), reverse=True):
        ref = f"#{x['pr']}" if x['pr'] else x['sha']
        link = f"{BASE}/pull/{x['pr']}" if x['pr'] else f"{BASE}/commit/{x['sha']}"
        w.writerow([ref, x['title'], x['nature'], x['public'], TYPE[x['cat']], x['prod'], x['release'], 'oui' if x['claude'] else 'non', link])
print(len(p), 'mises en production')
