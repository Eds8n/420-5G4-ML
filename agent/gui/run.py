"""Point d'entree de l'application graphique.

Lancement (depuis le devcontainer), avec le dossier de donnees par defaut
(agent/data) :

    python3 agent/gui/run.py

Pour tester sur une copie sans toucher aux originaux :

    python3 agent/gui/run.py --data-dir /chemin/vers/une/copie

ou, plus simple, le script dedie :

    bash agent/gui/lancer_copie.sh

Le module C++ bibliotheque_core doit avoir ete compile au prealable :

    cmake -S agent -B agent/build -DBUILD_PYTHON_BINDINGS=ON \\
        -DPython3_EXECUTABLE=$(command -v python3) \\
        -Dpybind11_DIR=$(python3 -m pybind11 --cmakedir)
    cmake --build agent/build
"""

import argparse

from app import main


def _analyser_arguments():
    analyseur = argparse.ArgumentParser(
        description="Interface graphique de la bibliothèque personnelle."
    )
    analyseur.add_argument(
        "--data-dir",
        default=None,
        help="Dossier contenant books.txt et users.txt (défaut : agent/data).",
    )
    return analyseur.parse_args()


if __name__ == "__main__":
    arguments = _analyser_arguments()
    main(data_dir=arguments.data_dir)
