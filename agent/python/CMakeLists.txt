# Module Python (pybind11) qui expose la logique C++ a l'interface graphique.
#
# Ce dossier est volontairement separe de agent/ : le file(GLOB "*.cpp") du
# CMakeLists.txt racine ne capture que les .cpp directement dans agent/, donc
# bindings.cpp n'est PAS compile dans l'executable CLI.
#
# Le module est construit uniquement si BUILD_PYTHON_BINDINGS=ON (voir
# agent/CMakeLists.txt), afin de ne pas rendre pybind11 obligatoire pour la CLI.

# Forcer le mode FindPython (utilise Python3_EXECUTABLE) : garantit que le
# module est compile pour l'interpreteur qui l'importera.
set(PYBIND11_FINDPYTHON ON)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Cree la cible bibliotheque_core et le fichier .so correspondant.
# On ajoute les sources du projet : le module doit embarquer l'implementation
# de Book/User/Library (les .h seuls ne suffisent pas au link).
pybind11_add_module(bibliotheque_core
    bindings.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../book.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../user.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/../library.cpp
)

# bindings.cpp inclut les en-tetes du projet (book.h, user.h, library.h).
target_include_directories(bibliotheque_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)

target_compile_features(bibliotheque_core PRIVATE cxx_std_17)

# Meme niveau de warnings que l'executable CLI.
target_compile_options(bibliotheque_core PRIVATE -Wall -Wextra -Wpedantic)
