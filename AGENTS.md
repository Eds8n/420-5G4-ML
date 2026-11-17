# AGENTS.md

Course project ("Atelier ML", 420-5G4-ML) split into independent parts. There is no root package manager, CI, linter, or test suite — don't go looking for one.

## Layout
- `apprentissage/` — Python data prep + analysis of a Pokémon dataset (Parts 1–2). `main.py` is the script version; `partie1_2.ipynb` is the notebook. Input CSVs are in `apprentissage/datas/`.
- `agent/` — C++17 console app `bibliotheque` (personal library manager), built with CMake.
- `analyse_image/` — the root README calls this "Deuxième partie", but the directory does not exist in the repo.

## Python (`apprentissage/`)
- Interpreter is the repo-root venv `.venv/` (Python 3.12.3); it is also the notebook's selected kernel (`.venv (3.12.3)`). Installed: pandas 3.1.0, numpy, matplotlib, seaborn, ipykernel. No `requirements.txt`.
- Data is read with paths relative to `apprentissage/` (e.g. `datas/pokedex.csv`), so run scripts and the notebook with `apprentissage/` as the working directory.
- The notebook ends by writing `datas/dataset.csv` (tab-separated, with an index column). That file is committed, so re-running the notebook overwrites tracked output.

## C++ (`agent/`)
- Build:
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
- `agent/.devcontainer/` is a C++ devcontainer that mounts the host X11 socket and uses `--net=host` for GUI forwarding (the current console app draws nothing).
