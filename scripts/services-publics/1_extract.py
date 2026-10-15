"""Extract integrated changes (PR merges, squash or rebased commits) from public repos,
classify type, detect AI-assistant traces, and compute production dates."""
import subprocess, re, json, sys, os
from concurrent.futures import ProcessPoolExecutor

ROOT = os.environ.get('REPOS_DIR', 'sources/repos')
SINCE = '2024-10-14'
UNTIL = '2026-10-14'

# repo -> (service, groupe, prod rule)
REPOS = {
 'demarche-numerique/demarche.numerique.gouv.fr': ('Démarche Numérique', 'DINUM', 'tags'),
 'betagouv/rdv-service-public': ('RDV Service Public', 'ANCT / beta.gouv', 'head'),
 'tchapgouv/tchap-web-v4': ('Tchap (web)', 'DINUM', 'tags'),
 'tchapgouv/tchap-x-android': ('Tchap (Android, nouvelle app)', 'DINUM', 'branch:main'),
 'tchapgouv/tchap-x-ios': ('Tchap (iOS, nouvelle app)', 'DINUM', 'tags'),
 'tchapgouv/tchap-android': ('Tchap (Android, historique)', 'DINUM', 'branch:main'),
 'tchapgouv/tchap-ios': ('Tchap (iOS, historique)', 'DINUM', 'branch:master'),
 'suitenumerique/docs': ('Docs (La Suite)', 'DINUM', 'tags'),
 'suitenumerique/meet': ('Visio (La Suite)', 'DINUM', 'tags'),
 'suitenumerique/drive': ('Fichiers (La Suite)', 'DINUM', 'tags'),
 'suitenumerique/messages': ('Messagerie (La Suite)', 'DINUM', 'tags'),
 'suitenumerique/people': ('Régie (La Suite)', 'DINUM', 'tags'),
 'suitenumerique/conversations': ('Assistant IA (La Suite)', 'DINUM', 'tags'),
 'suitenumerique/calendars': ('Agenda (La Suite)', 'DINUM', 'head'),
 'suitenumerique/find': ('Recherche (La Suite)', 'DINUM', 'head'),
 'suitenumerique/projects': ('Projets (La Suite)', 'DINUM', 'head'),
 'opendatateam/udata': ('data.gouv.fr (moteur udata)', 'DINUM', 'tags'),
 'datagouv/cdata': ('data.gouv.fr (nouveau site)', 'DINUM', 'head'),
 'annuaire-entreprises-data-gouv-fr/site': ('Annuaire des Entreprises', 'DINUM', 'head'),
 'proconnect-gouv/proconnect-identite': ('ProConnect', 'DINUM', 'tags'),
 'france-connect/sources': ('FranceConnect', 'DINUM', 'head'),
 'MTES-MCT/trackdechets': ('Trackdéchets', 'Ministère de la Transition écologique', 'branch:master'),
 'MTES-MCT/carbure': ('CarbuRe', 'Ministère de la Transition écologique', 'branch:master', 'dev'),
 'SocialGouv/code-du-travail-numerique': ('Code du travail numérique', 'Ministère du Travail', 'branch:master'),
 'betagouv/mon-entreprise': ('Mon-entreprise (Urssaf)', 'Urssaf', 'head'),
 'pass-culture/pass-culture-main': ('pass Culture', 'Ministère de la Culture', 'head'),
 'gip-inclusion/les-emplois': ("Les emplois de l'inclusion", 'GIP Plateforme de l\'inclusion', 'head'),
 'betagouv/collectif-objets': ('Collectif Objets', 'Ministère de la Culture', 'head'),
 'betagouv/france-chaleur-urbaine': ('France Chaleur Urbaine', 'Ministère de la Transition écologique', 'branch:main'),
 'incubateur-ademe/nosgestesclimat-site-nextjs': ('Nos Gestes Climat', 'ADEME', 'head'),
 'betagouv/aides-jeunes': ('Aides jeunes (1jeune1solution)', 'beta.gouv', 'head'),
 'BaseAdresseNationale/adresse.data.gouv.fr': ('adresse.data.gouv.fr', 'IGN / ANCT', 'tags'),
 'numerique-gouv/sites-faciles': ('Sites Faciles', 'DINUM', 'branch:production'),
}

AI = [
 ('Claude', re.compile(r'co-authored-by:[^\n]*claude|noreply@anthropic\.com|generated with \[?claude|claude\.ai/code|claude-session:|\bclaude\[bot\]', re.I)),
 ('Copilot', re.compile(r'co-authored-by:[^\n]*copilot|copilot-swe-agent|copilot@github\.com|\bcopilot\[bot\]', re.I)),
 ('Cursor', re.compile(r'co-authored-by:[^\n]*cursor|cursoragent@cursor\.com|cursor agent|\[cursor\]', re.I)),
 ('Codex', re.compile(r'co-authored-by:[^\n]*(codex|openai|chatgpt)|chatgpt-codex-connector|codex\[bot\]', re.I)),
 ('Gemini', re.compile(r'co-authored-by:[^\n]*gemini|gemini-code-assist|google-labs-jules|jules\[bot\]', re.I)),
 ('Mistral', re.compile(r'co-authored-by:[^\n]*(mistral|le chat)|mistral vibe|mistral-vibe', re.I)),
 ('Autre IA', re.compile(r'co-authored-by:[^\n]*(aider|devin|windsurf|codeium|amazon q|tabnine|cline|roo)|^aider: |devin-ai-integration', re.I | re.M)),
]
BOT = re.compile(r'\[bot\]|dependabot|renovate|github-actions|snyk|weblate|crowdin|pre-commit-ci|mergify|semantic-release|transifex|imgbot|greenkeeper|allcontributors|lokalise|tolgee', re.I)
AIBOT = re.compile(r'claude|copilot|cursor|codex|jules|gemini|devin', re.I)

GM_FEAT = ('✨', '💄', '🎉', '🚸', '🌐', '♿')
GM_FIX = ('🐛', '🚑', '🩹', '🥅')
FEAT = re.compile(r'^\s*(\[?feat|feature|features?\b|etq\b|en tant qu|us\b|add\b|added|adds|ajout|ajoute|nouveau|nouvelle|new\b|implement|allow|permet|support\b|enable|introduc)', re.I)
FIX = re.compile(r'^\s*(fix|hotfix|bugfix|correctif|corrige|corrig|repair|revert|patch\b)|\bfix(es|ed)?\b|\bbug\b|correctif|r[ée]gression', re.I)
TECH = re.compile(r'^\s*(\[?tech\b|chore|refactor|test|tests|ci\b|build|deps?\b|bump|perf|task|i18n|docs?\b|style|lint|upgrade|update|maj\b|mise à jour|migration|release|version|bump|merge|wip)', re.I)


def g(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, errors='replace').stdout


STRIP = re.compile(r'^\s*(?:(?:\([^)]{1,40}\)|\[[^\]]{1,40}\]|[A-Z]{2,6}-\d+\s*:?|#\d+\s*:?|[\u2600-\u27BF\U0001F300-\U0001FAFF\uFE0F]+)\s*)+')
FEATV = re.compile(r'^\s*(feat|feature|features?|etq|en tant qu|us\b|add|adds|added|ajout|ajoute|ajouter|nouveau|nouvelle|new|implement|allow|allows|permet|permettre|support|enable|introduc|display|afficher|affiche|show|create|cr[ée]er|cr[ée]ation|let\b|propose|proposer|g[ée]rer|gestion|mise en place|amélior|ameliore|improve|enhance|evolution|évolution)', re.I)
TECHV = re.compile(r'^\s*(tech|chore|refactor|refacto|test|tests|ci\b|build|deps?\b|bump|perf|task|i18n|docs?\b|style|lint|upgrade|update|maj\b|mise à jour|migration|migrate|release|version|merge|wip|remove|removes|drop|delete|supprim|retire|rename|renomme|clean|nettoy|move|extract|simplif|config|configure|use\b|utilise|assert|log|logs|monitoring|sentry|prepare|bump|revert|typing|types?\b|format)', re.I)
FIXV = re.compile(r'^\s*(fix|fixes|fixed|hotfix|bugfix|correctif|correction|corrige|corriger|corrig|repair|répare|patch)|\bfix(es|ed)?\b|\bbug\b|correctif|r[ée]gression', re.I)


def classify(title, msgs):
    t = title.strip()
    lead = t[:3]
    if any(lead.startswith(e) for e in GM_FEAT): return 'feat'
    if any(lead.startswith(e) for e in GM_FIX): return 'fix'
    if re.match(r'^[\u2600-\u27BF\U0001F300-\U0001FAFF]', t): return 'tech'
    core = STRIP.sub('', t)
    # "scope: text" (conventional commits or django-style scopes)
    m = re.match(r'^\s*([\w\- /.]{1,30}?)(\([^)]*\))?!?\s*:\s*(.*)$', core)
    words = [core]
    if m:
        words = [m.group(1), m.group(3)]
    for w in words:
        if re.match(r'^\s*feat', w, re.I): return 'feat'
        if FIXV.search(w[:60]) and not re.match(r'^\s*(feat)', w, re.I): return 'fix'
        if TECHV.search(w): return 'tech'
        if FEATV.search(w): return 'feat'
    heads = [STRIP.sub('', mm.split('\n', 1)[0]) for mm in msgs]
    nf = sum(1 for h in heads if re.match(r'^\s*(feat|✨)', h, re.I))
    nx = sum(1 for h in heads if re.match(r'^\s*(fix|🐛)', h, re.I))
    if nf and nf >= nx: return 'feat'
    if nx: return 'fix'
    return 'other'


def markers(repo, rule, head):
    """Return list of (unix, date, ref) release markers in topological order, or None for merge-date."""
    if rule == 'head':
        return None
    if rule.startswith('branch:'):
        br = rule.split(':', 1)[1]
        out = g(repo, 'log', '--first-parent', br, f'--since={SINCE}', '--format=%H %ct %cs')
        rows = [l.split() for l in out.splitlines()][::-1]
        return [(int(u), d, h) for h, u, d in rows]
    # tags: use dereferenced commit date for ordering, tag creation date for prod date
    out = g(repo, 'for-each-ref', '--format=%(if)%(*objectname)%(then)%(*objectname) %(*committerdate:unix)%(else)%(objectname) %(committerdate:unix)%(end) %(creatordate:short) %(refname:short)', 'refs/tags')
    rows = []
    for l in out.splitlines():
        p = l.split()
        if len(p) < 4: continue
        h, u, d, name = p[0], int(p[1]), p[2], ' '.join(p[3:])
        if d < SINCE: continue
        if re.search(r'demo|hackathon|preprod|rc\d*$|beta|alpha|test|tmp|sdk|testing|components/', name, re.I): continue
        rows.append((u, d, h))
    rows.sort()
    return rows


def analyse(full):
    service, groupe, rule, *dev = REPOS[full]
    repo = os.path.join(ROOT, full.replace('/', '_') + '.git')
    head = dev[0] if dev else g(repo, 'symbolic-ref', '--short', 'HEAD').strip()
    # production reach dates
    mk = markers(repo, rule, head)
    reach = {}
    if mk:
        prev = None
        for u, d, h in mk:
            args = ['rev-list', h] + (['^' + prev] if prev else [])
            for s in g(repo, *args).split():
                reach.setdefault(s, d)
            prev = h
    SEP = '\x1e'
    log = g(repo, 'log', '--first-parent', head, f'--since={SINCE}', f'--until={UNTIL} 23:59',
            '--format=%H%x1f%P%x1f%cs%x1f%an <%ae>%x1f%s%x1f%b' + SEP)
    units = []
    for rec in log.split(SEP):
        rec = rec.strip('\n')
        if not rec: continue
        parts = rec.split('\x1f')
        if len(parts) < 6: continue
        h, p, d, author, s, b = parts
        parents = p.split()
        pr = None
        m = re.match(r'Merge pull request #(\d+) from (\S+)', s)
        if len(parents) == 2:
            cnt = int(g(repo, 'rev-list', '--count', f'{parents[0]}..{parents[1]}').strip() or 0)
            if cnt > 300 or re.search(r"merge (tag|remote-tracking|branch '?(develop|master|main)'? of|upstream|element-|v\d+\.\d+\.\d+)", s, re.I):
                if not m:
                    continue  # upstream sync or big integration merge: not a change of this team
            if cnt > 300: continue
            raw = g(repo, 'log', f'{parents[0]}..{parents[1]}', '--format=%an <%ae>%x1f%B%x1e')
            commits = [c.strip('\n').split('\x1f', 1) for c in raw.split('\x1e') if c.strip()]
            msgs = [c[1] if len(c) > 1 else '' for c in commits]
            authors = [c[0] for c in commits]
            title = (b.strip().split('\n')[0] if (m and b.strip()) else s)
            if m: pr = int(m.group(1))
            if not m and re.match(r"^Merge (branch|remote)", s):
                # merge of a branch without PR: keep only if it is not a release/sync merge
                if re.search(r"(dev|develop|main|master|staging|production|release)'? into", s, re.I):
                    continue
        else:
            msgs = [s + '\n' + b]
            authors = [author]
            title = s
            mm = re.search(r'\(#(\d+)\)\s*$', s)
            if mm: pr = int(mm.group(1))
            cnt = 1
        if full.startswith('tchapgouv/') and re.search(r'element|upstream|^\s*(upgrade|merge|rebase|sync)\b.*\d+\.\d+', title + ' ' + s, re.I) and len(msgs) > 5:
            continue  # synchronisation with the upstream Element code base
        alltext = '\n'.join(msgs) + '\n' + '\n'.join(authors)
        ai = [name for name, rx in AI if rx.search(alltext)]
        human = [a for a in authors if not (BOT.search(a) and not AIBOT.search(a))]
        bot = not human and not ai
        ncommits = len(msgs)
        nclaude_commits = sum(1 for msg, a in zip(msgs, authors) if AI[0][1].search(msg + '\n' + a))
        nbot_commits = sum(1 for a in authors if BOT.search(a) and not AIBOT.search(a))
        prod = reach.get(h) if mk else d
        units.append(dict(repo=full, service=service, groupe=groupe, sha=h[:10], pr=pr, title=title[:200], merged=d,
                          prod=prod, type=classify(title, msgs), ai=ai, bot=bot,
                          ncommits=ncommits, nclaude_commits=nclaude_commits, nbot_commits=nbot_commits))
    # agent configuration files on the main line (first addition by this team)
    cfg = {}
    sh = set(open(os.path.join(repo, 'shallow')).read().split()) if os.path.exists(os.path.join(repo, 'shallow')) else set()
    first = g(repo, 'log', '--first-parent', '--format=%H %cs', '--reverse', head).split('\n', 1)[0].split()
    shallow_root = first[1] if first and first[0] in sh else None
    UP = re.compile(r"merge (element|elementx|tag|upstream|remote-tracking)|into tchap|element x v|elementx-ios", re.I)
    ci = [f.split(':', 1)[1] for f in g(repo, 'grep', '-l', '-i', '-E', 'claude-code-action|anthropic_api_key', head, '--', '.github').split() if ':' in f]
    signals = (('Instructions Claude (CLAUDE.md, .claude/)', ['CLAUDE.md', ':(glob)**/CLAUDE.md', '.claude', ':(glob)**/.claude/**']),
               ('Instructions agents (AGENTS.md)', ['AGENTS.md', ':(glob)**/AGENTS.md']),
               ('Règles Cursor', ['.cursor', '.cursorrules', ':(glob)**/.cursor/**']),
               ('Instructions Copilot', ['.github/copilot-instructions.md', '.github/instructions']),
               ('Claude Code en CI (revue de PR…)', ci))
    for name, paths in signals:
        if not paths: continue
        out = g(repo, 'log', '--first-parent', head, '--diff-filter=A', '--format=%cs\x1f%s', '--reverse', '--', *paths).split('\n')
        out = [l.split('\x1f') for l in out if l.strip()]
        out = [o for o in out if not UP.search(o[1] if len(o) > 1 else '')]
        if out:
            cfg[name] = out[0][0] if out[0][0] != shallow_root else 'avant 2024-06'
    return dict(repo=full, service=service, groupe=groupe, rule=rule, head=head, units=units, config=cfg,
                markers=len(mk) if mk else 0)


if __name__ == '__main__':
    repos = sys.argv[1:] or list(REPOS)
    with ProcessPoolExecutor(6) as ex:
        res = list(ex.map(analyse, repos))
    json.dump(res, open('build/multi.json', 'w'), ensure_ascii=False)
    for r in res:
        u = [x for x in r['units'] if not x['bot']]
        inprod = [x for x in u if x['prod']]
        c = [x for x in inprod if 'Claude' in x['ai']]
        others = {}
        for x in inprod:
            for a in x['ai']:
                others[a] = others.get(a, 0) + 1
        f = [x for x in inprod if x['type'] == 'feat']
        print(f"{r['service'][:34]:34} units={len(r['units']):5} human={len(u):5} prod={len(inprod):5} feat={len(f):4} claude={len(c):4} featClaude={sum(1 for x in f if 'Claude' in x['ai']):4} ai={others} cfg={r['config']} mk={r['markers']}")
