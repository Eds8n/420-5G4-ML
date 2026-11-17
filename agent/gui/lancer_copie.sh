#!/usr/bin/env bash
#
# Lance l'interface graphique sur une COPIE de agent/data.
# Les fichiers originaux (agent/data/books.txt et users.txt) ne sont JAMAIS modifies.
#
# Utilisation (dans le devcontainer, depuis n'importe quel dossier) :
#
#     bash agent/gui/lancer_copie.sh
#
# Options :
#   --reinitialiser   Recopie agent/data vers la copie avant de lancer.
#                     Sans cette option, une copie deja existante est reutilisee,
#                     ce qui permet de verifier que les donnees survivent a la
#                     fermeture puis a la reouverture de l'application.
#
set -euo pipefail

ici="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
agent="$(dirname "$ici")"
source_data="$agent/data"
copie="$agent/data_copie"

reinitialiser=0
if [ "${1:-}" = "--reinitialiser" ]; then
    reinitialiser=1
fi

if [ "$reinitialiser" -eq 1 ] || [ ! -f "$copie/books.txt" ]; then
    mkdir -p "$copie"
    cp -f "$source_data/books.txt" "$copie/books.txt"
    cp -f "$source_data/users.txt" "$copie/users.txt"
    echo "Copie des donnees : '$source_data' -> '$copie'"
else
    echo "Reutilisation de la copie existante : '$copie'"
    echo "(utilisez --reinitialiser pour repartir des donnees d'origine)"
fi

echo "Lancement de la GUI sur la copie (fichiers originaux intacts)..."
exec python3 "$ici/run.py" --data-dir "$copie"
