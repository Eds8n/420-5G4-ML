# AGENTS.md

Course project ("Atelier ML", 420-5G4-ML) split into independent parts. There is no root package manager, CI, linter, or test suite — don't go looking for one.

## Layout
- `apprentissage/` — Python data prep + analysis of a Pokémon dataset (Parts 1–2). `main.py` is the script version; `partie1_2.ipynb` is the notebook. Input CSVs are in `apprentissage/datas/`.
- `agent/` — C++17 personal library manager. Original console app (`main.cpp`, `book/user/library/filemanager`) plus a pybind11 module and a customTkinter GUI added in Part 3.
- `agent/python/` — pybind11 bindings; `agent/gui/` — customTkinter GUI.
- `chatsLogs/` — OpenCode conversation exports required for the Part 3 submission.
- `analyse_image/` — the root README calls this "Deuxième partie", but the directory does not exist in the repo.

## Python (`apprentissage/`)
- Interpreter is the repo-root venv `.venv/` (Python 3.12.3); it is also the notebook's selected kernel (`.venv (3.12.3)`). Installed: pandas 3.1.0, numpy, matplotlib, seaborn, ipykernel. No `requirements.txt`.
- Data is read with paths relative to `apprentissage/` (e.g. `datas/pokedex.csv`), so run scripts and the notebook with `apprentissage/` as the working directory.
- The notebook ends by writing `datas/dataset.csv` (tab-separated, with an index column). That file is committed, so re-running the notebook overwrites tracked output.

## C++ (`agent/`)
- Build the CLI:
  ```
  cd agent
  mkdir -p build && cd build
  cmake ..
  make
  ```
  Binary is `agent/build/bibliotheque`.
- `CMakeLists.txt` uses `file(GLOB "*.cpp")`; after adding or removing a source file, re-run `cmake ..` so it is picked up.
- Run: `./bibliotheque -d <data-dir>`. Without `-d`, the data file names are empty, so nothing is loaded or saved. Sample data is in `agent/data/`.
- Persistence is pipe-separated; neither value may contain `|`:
  - `books.txt`: `title|author|isbn|available(0|1)|borrowerId`
  - `users.txt`: `name|userId|isbn1,isbn2`
- C++17 with `-Wall -Wextra -Wpedantic`.

## pybind11 bindings (`agent/python/`)
- `bindings.cpp` builds the `bibliotheque_core` module (Book, User, Library, FileManager). It lives in a subdirectory so the root `file(GLOB "*.cpp")` does NOT compile it into the CLI.
- Built only with `-DBUILD_PYTHON_BINDINGS=ON` (default OFF), so the CLI still builds without pybind11. Compile it with the SAME interpreter that imports it:
  ```
  PY=$(command -v python3)
  cmake -S agent -B agent/build -DBUILD_PYTHON_BINDINGS=ON \
    -DPython3_EXECUTABLE="$PY" -Dpybind11_DIR="$($PY -m pybind11 --cmakedir)"
  cmake --build agent/build
  ```
  Output: `agent/build/python/bibliotheque_core.cpython-3xx-*.so`.
- `Library` owns its objects via `unique_ptr` and its methods return raw pointers. The bindings wrap every pointer-returning method to return **copies** (`std::vector<Book>`, `std::optional<Book>`, …) — otherwise pybind11 `take_ownership` would double-free. Python can only mutate the library through `Library` methods, so re-read state after every mutation.
- C++ binding tests: `agent/python/tests/test_library.py` (stdlib unittest, no display needed).

## GUI (`agent/gui/`)
- customTkinter with 4 tabs: Livres, Utilisateurs, Emprunts, Statistiques. All business logic stays in C++; the GUI only calls `bibliotheque_core`.
- Launch (module must be built first):
  ```
  python3 agent/gui/run.py                 # loads/saves agent/data
  python3 agent/gui/run.py --data-dir DIR  # custom data dir
  bash agent/gui/lancer_copie.sh           # runs on a copy (agent/data_copie/), originals untouched
  ```
- `core_loader.py` locates the built `.so` (via `BIBLIOTHEQUE_CORE_DIR`, else `agent/build/python`) and adds it to `sys.path`.
- Persistence: `Application(data_dir=..., auto_save=...)` loads through `FileManager` at startup and saves on `destroy()` (window close). Cross-tab refresh goes through `Application.refresh_all_tabs()`.
- Tests (stdlib unittest, require an X display): `agent/gui/test_*.py`, run one file at a time from `agent/gui`. They MUST NOT touch `agent/data` — `gui_test_case.py` gives each test a temporary data dir (optionally seeded from a copy of the real data).

## Devcontainer (`agent/.devcontainer/`)
- C++ image with CMake; installs `python3-tk`, `python3-pybind11` and `customtkinter` (`pip --break-system-packages`, since Debian 13 enforces PEP 668).
- Mounts the host X11 socket AND `~/.Xauthority` (env `XAUTHORITY=/tmp/.Xauthority`) and uses `--net=host`: the GUI needs the auth cookie, the socket alone is not enough.
- Example (build image once with `docker build -t biblio-devcontainer agent/.devcontainer`, then):
  ```
  docker run --rm -it -v "$PWD:/workspace" \
    -v /tmp/.X11-unix:/tmp/.X11-unix -v "$HOME/.Xauthority:/tmp/.Xauthority:ro" \
    -e DISPLAY -e XAUTHORITY=/tmp/.Xauthority --net=host \
    --user "$(id -u):$(id -g)" biblio-devcontainer \
    bash -lc 'cd /workspace && bash agent/gui/lancer_copie.sh'
  ```

## Ignored / generated
- `agent/build/`, `agent/data_copie/`, `__pycache__/` and `*.pyc` are gitignored — never commit them.
