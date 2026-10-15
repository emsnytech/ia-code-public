# Consigne pour Claude Code — publier « L'IA dans le code public »

Contexte : ce dossier `ia-code-public` contient un travail prêt à publier (site statique dans `docs/`, données CSV, scripts d'extraction, README). Il doit devenir un **nouveau dépôt GitHub public, `emsnytech/ia-code-public`**, distinct de `form2026`, publié sur GitHub Pages.

## À faire

1. **Ne touche pas au dépôt `form2026`** ni à `Documents/cartographie`. Travaille uniquement dans ce dossier.
2. Vérifie que je suis connecté à GitHub (`gh auth status`, compte `emsnytech`). Sinon, arrête-toi et dis-moi quoi faire.
3. Relis le contenu avant de publier :
   - aucun secret, jeton, chemin personnel ni fichier volumineux (> 5 Mo) ;
   - `sources/` et `build/` sont bien ignorés par `.gitignore` ;
   - les liens internes du site sont relatifs, et ceux du README pointent vers `https://emsnytech.github.io/ia-code-public/`.
4. Teste le site en local : `python3 -m http.server 8000 --directory docs`, puis ouvre `/`, `/services-publics/` et `/demarche-numerique/`. Vérifie que les graphiques s'affichent et qu'il n'y a pas d'erreur dans la console. Signale-moi tout problème avant de pousser.
5. Initialise le dépôt et fais un premier commit :
   `git init -b main && git add . && git commit -m "Observatoire : l'IA dans le code public (données au 14/10/2026)"`
6. Crée le dépôt public et pousse :
   `gh repo create emsnytech/ia-code-public --public --source . --push --description "Place des assistants IA (dont Claude Code) dans les dépôts open source des services numériques de l'État"`
7. Active GitHub Pages sur la branche `main`, dossier `/docs` :
   `gh api -X POST repos/emsnytech/ia-code-public/pages -f "source[branch]=main" -f "source[path]=/docs"`
   (si Pages existe déjà : même appel avec `-X PUT`).
8. Ajoute les sujets du dépôt : `gh repo edit emsnytech/ia-code-public --add-topic open-source --add-topic numerique-public --add-topic ia --add-topic claude-code --add-topic open-data`.
9. Attends la fin du déploiement (`gh api repos/emsnytech/ia-code-public/pages/builds/latest`). Vérifie ensuite que `https://emsnytech.github.io/ia-code-public/` et les deux tableaux de bord répondent et affichent les données.
10. Donne-moi en fin de travail : l'adresse du dépôt, l'adresse du site, et la liste de ce que tu as éventuellement corrigé.

## Pour plus tard (ne pas faire maintenant)

- Mise à jour des chiffres : `bash scripts/run_all.sh`, contrôle des écarts, puis commit « Données au JJ/MM/AAAA ».
- Ce dossier pourra devenir un skill « maj-ia-code-public » sur le modèle de `maj-demarches-form2026`.
