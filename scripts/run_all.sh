#!/usr/bin/env bash
# Régénère toutes les données depuis les dépôts publics. Durée : quelques minutes.
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/fetch_sources.sh
python3 scripts/demarche-numerique/1_extract.py
python3 scripts/demarche-numerique/2_fichiers.py
python3 scripts/demarche-numerique/3_type.py > /dev/null
python3 scripts/demarche-numerique/4_nature_public.py > /dev/null
python3 scripts/demarche-numerique/5_csv.py
python3 scripts/services-publics/1_extract.py
python3 scripts/services-publics/2_csv.py
