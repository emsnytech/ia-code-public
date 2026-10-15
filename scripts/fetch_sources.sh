#!/usr/bin/env bash
# Clone (sans le contenu des fichiers) les dépôts publics analysés.
set -euo pipefail
mkdir -p sources/repos build
git clone --filter=blob:none --no-checkout https://github.com/demarche-numerique/demarche.numerique.gouv.fr.git sources/demarche.numerique.gouv.fr || git -C sources/demarche.numerique.gouv.fr fetch --tags origin
python3 - <<'PY' > build/repos.txt
import importlib.util
spec = importlib.util.spec_from_file_location('m', 'scripts/services-publics/1_extract.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print('\n'.join(m.REPOS))
PY
while read -r r; do
  d="sources/repos/${r//\//_}.git"
  [ -d "$d" ] || git clone -q --bare --filter=blob:none --shallow-since=2024-06-01 "https://github.com/$r.git" "$d"
done < build/repos.txt
# branches de production suivies en plus de la branche par défaut
fetch() { git -C "sources/repos/$1.git" fetch -q --filter=blob:none --shallow-since=2024-06-01 origin "+refs/heads/$2:refs/heads/$2" || true; }
fetch MTES-MCT_trackdechets master; fetch SocialGouv_code-du-travail-numerique master
fetch betagouv_france-chaleur-urbaine main; fetch tchapgouv_tchap-x-android main
fetch tchapgouv_tchap-x-ios main; fetch tchapgouv_tchap-android main; fetch tchapgouv_tchap-ios master
fetch numerique-gouv_sites-faciles production; fetch MTES-MCT_carbure dev
