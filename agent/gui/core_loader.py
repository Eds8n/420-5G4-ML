"""Localise et importe le module C++ `bibliotheque_core`.

Le module est un fichier .so produit par CMake (par ex.
`agent/build/python/bibliotheque_core.cpython-313-x86_64-linux-gnu.so`).
Ce helper ajoute son dossier a sys.path pour que `import bibliotheque_core`
fonctionne quel que soit le dossier de build.

Ordre de recherche :
1. la variable d'environnement BIBLIOTHEQUE_CORE_DIR (si definie) ;
2. <agent>/build/python et <agent>/build ;
3. <racine_depot>/build/python et <racine_depot>/build.
"""

import glob
import os
import sys


def _ensure_core_on_path() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    agent_dir = os.path.dirname(here)              # .../agent
    repo_dir = os.path.dirname(agent_dir)          # racine du depot

    candidates = []
    env_dir = os.environ.get("BIBLIOTHEQUE_CORE_DIR")
    if env_dir:
        candidates.append(env_dir)
    candidates += [
        os.path.join(agent_dir, "build", "python"),
        os.path.join(agent_dir, "build"),
        os.path.join(repo_dir, "build", "python"),
        os.path.join(repo_dir, "build"),
    ]

    for dossier in candidates:
        if dossier and glob.glob(os.path.join(dossier, "bibliotheque_core*.so")):
            if dossier not in sys.path:
                sys.path.insert(0, dossier)
            return


_ensure_core_on_path()

import bibliotheque_core  # noqa: E402  (import apres ajustement de sys.path)
