cmake_minimum_required(VERSION 3.21)
project(bibliotheque)

file(GLOB SOURCES "*.cpp")
add_executable(${PROJECT_NAME} ${SOURCES})

# Specifie qu'on veut la version C++17 du langage
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

# flag pour tous les warnings possible
target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra -Wpedantic)

# Module Python (pybind11) pour l'interface graphique.
# Desactive par defaut pour que la compilation de la CLI ne depende pas de pybind11.
# Activer avec : cmake .. -DBUILD_PYTHON_BINDINGS=ON
option(BUILD_PYTHON_BINDINGS "Construire le module Python (pybind11)" OFF)
if(BUILD_PYTHON_BINDINGS)
    add_subdirectory(python)
endif()
