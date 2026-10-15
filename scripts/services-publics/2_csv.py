"""Produit les quatre fichiers du tableau de bord multi-services (data/services-publics/)."""
import json, csv, collections, os, re
OUT = 'docs/data/services-publics'
os.makedirs(OUT, exist_ok=True)
SINCE, UNTIL = os.environ.get('SINCE', '2024-10-14'), os.environ.get('UNTIL', '2026-10-14')
R = json.load(open('build/multi.json'))
months = []; y, m = int(SINCE[:4]), int(SINCE[5:7])
while f'{y}-{m:02d}' <= UNTIL[:7]:
    months.append(f'{y}-{m:02d}'); m += 1
    if m == 13: y, m = y + 1, 1
RULE = {'tags': 'Première version publiée (étiquette) qui contient le changement', 'head': 'Fusion sur la branche principale (déploiement continu)'}
with open(f'{OUT}/services.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['service', 'produit', 'groupe', 'depot', 'lien', 'branche', 'mise_en_production'])
    for r in R:
        rule = RULE.get(r['rule']) or f"Arrivée sur la branche {r['rule'].split(':')[1]}"
        prod = re.sub(r'\s*\((web|Android|iOS)[^)]*\)', '', r['service']); prod = re.sub(r'\s*\((moteur udata|nouveau site)\)', '', prod)
        w.writerow([r['service'], prod, r['groupe'], r['repo'], 'https://github.com/' + r['repo'], r['head'], rule])
agg = collections.defaultdict(collections.Counter)
for r in R:
    for u in r['units']:
        if u['bot'] or not u['prod'] or u['prod'] < SINCE or u['prod'] > UNTIL: continue
        a = agg[(u['prod'][:7], r['service'])]
        cl = 'Claude' in u['ai']
        a['changements'] += 1; a['avec_claude'] += cl
        if u['type'] == 'feat': a['evolutions'] += 1; a['evolutions_avec_claude'] += cl
        a['avec_copilot'] += 'Copilot' in u['ai']; a['avec_cursor'] += 'Cursor' in u['ai']
        a['avec_autre_ia'] += any(x not in ('Claude', 'Copilot', 'Cursor') for x in u['ai'])
        a['commits'] += u['ncommits'] - u['nbot_commits']; a['commits_avec_claude'] += u['nclaude_commits']
cols = ['changements', 'avec_claude', 'evolutions', 'evolutions_avec_claude', 'avec_copilot', 'avec_cursor', 'avec_autre_ia', 'commits', 'commits_avec_claude']
with open(f'{OUT}/mensuel_services.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['mois', 'service', 'groupe', *cols])
    for r in R:
        for mo in months:
            a = agg[(mo, r['service'])]; w.writerow([mo, r['service'], r['groupe'], *[a[c] for c in cols]])
with open(f'{OUT}/signaux.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'service', 'signal', 'date']); i = 0
    for r in R:
        for k, v in sorted(r['config'].items(), key=lambda kv: kv[1]):
            i += 1; w.writerow([f's{i:02d}', r['service'], k, v])
TYPE = {'feat': 'Évolution', 'fix': 'Correctif', 'tech': 'Technique', 'other': 'Non classé'}
rows = []
for r in R:
    for u in r['units']:
        if u['bot'] or not u['prod'] or not u['ai'] or u['prod'] < SINCE: continue
        ref = f"{r['repo']}#{u['pr']}" if u['pr'] else f"{r['repo']}@{u['sha'][:7]}"
        link = f"https://github.com/{r['repo']}/pull/{u['pr']}" if u['pr'] else f"https://github.com/{r['repo']}/commit/{u['sha']}"
        rows.append([ref, r['service'], u['title'], TYPE[u['type']], u['prod'], ' + '.join(u['ai']), 'oui' if 'Claude' in u['ai'] else 'non', link])
rows.sort(key=lambda x: x[4], reverse=True)
with open(f'{OUT}/changements_ia.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['ref', 'service', 'titre', 'type', 'mise_en_production', 'outils_ia', 'claude', 'lien']); w.writerows(rows)
print(len(rows), 'changements avec trace d\'IA')
