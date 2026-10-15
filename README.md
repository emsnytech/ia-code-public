# L'IA dans le code public

Observatoire de la place des assistants de programmation IA, et de **Claude Code** en particulier, dans les dépôts open source des services numériques de l'État.

Site : https://emsnytech.github.io/ia-code-public/

## Deux tableaux de bord

| Page | Périmètre | Ce qu'elle montre |
|---|---|---|
| [Services publics](https://emsnytech.github.io/ia-code-public/services-publics/) | 33 dépôts, 14/10/2024 → 14/10/2026 | Adoption par les équipes, activité par projet et par mois, poids de Claude, autres assistants (Copilot, Cursor…), fichiers d'instructions pour agents |
| [Démarche Numérique](https://emsnytech.github.io/ia-code-public/demarche-numerique/) | 1 dépôt, 14/10/2021 → 14/10/2026 | Mises en production par mois, par nature (sécurité, accessibilité, API, design…) et par public, part de Claude |

## Principaux constats (au 14 octobre 2026)

- **20 dépôts sur 33** portent au moins un changement en production signé par Claude ; aucun en octobre 2024.
- **10 dépôts** contiennent des fichiers d'instructions pour agents IA (CLAUDE.md, AGENTS.md, règles Cursor…), dont 7 ajoutés depuis juillet 2025.
- Le volume reste **concentré** : 565 des 697 changements avec Claude (81 %) viennent de Démarche Numérique, où Claude figure dans plus de la moitié des évolutions des six derniers mois. Hors Démarche Numérique, c'est moins de 1 % des changements.

## Méthode

- **Source** : l'historique Git public de chaque dépôt (aucune API, aucun accès privilégié).
- **Changement** : une pull request fusionnée, ou un commit squashé/rebasé sur la branche principale. Les contributions des seuls robots (Dependabot, Renovate…) sont écartées, ainsi que les synchronisations de Tchap avec le code amont d'Element.
- **Mise en production** : première version étiquetée qui contient le changement ; à défaut, arrivée sur la branche de production ; à défaut, date de fusion (déploiement continu). La règle retenue pour chaque dépôt est dans `docs/data/services-publics/services.csv`.
- **Trace de Claude** : un commit du changement porte `Co-Authored-By: Claude`, `Generated with Claude Code`, un lien `claude.ai/code`, ou a pour auteur l'application Claude. Même logique pour Copilot, Cursor, Codex, Gemini, Mistral…
- **Classements** (évolution / correctif / technique ; nature ; public) : automatiques, par mots-clés sur le titre et les fichiers modifiés. Fiables en tendance, pas ligne à ligne.

### Limites

- Les mentions de co-auteur sont ajoutées par défaut mais **désactivables** ; un usage de l'IA en conversation, en relecture ou par copier-coller ne laisse aucune trace. **Les chiffres sont un plancher.**
- Les volumes ne se comparent pas d'un projet à l'autre : certaines équipes fusionnent une PR par fonctionnalité, d'autres intègrent commit par commit.

## Reproduire

Prérequis : `git`, `python3` (bibliothèque standard uniquement).

```bash
bash scripts/run_all.sh
```

Le script clone les dépôts sans le contenu des fichiers (`--filter=blob:none`) dans `sources/`, extrait l'historique dans `build/`, puis régénère les CSV de `docs/data/`. Pour changer la période : variables `SINCE` et `UNTIL`.

## Arborescence

```
docs/                     site publié (GitHub Pages)
  index.html              accueil
  services-publics/       tableau de bord multi-dépôts
  demarche-numerique/     tableau de bord Démarche Numérique
  data/                   fichiers CSV (réutilisables)
  assets/                 charte FORM 2026, moteur de chargement des données
scripts/                  extraction et calcul
```

## Licence

Code : MIT. Données : Licence Ouverte 2.0 (Etalab).

---

Un travail de la série FORM 2026. Réalisé avec Claude.
