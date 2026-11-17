"""Fenetre principale de l'application bibliotheque (customTkinter).

Contient les 4 onglets : Livres, Utilisateurs, Emprunts, Statistiques.

Persistance : les donnees sont chargees au demarrage et sauvegardees a la
fermeture via le FileManager C++ (pybind11). Par defaut le dossier de donnees
est <agent>/data ; il est parametrable pour que les tests travaillent sur une
copie temporaire sans toucher aux fichiers originaux.
"""

import os

import customtkinter as ctk

from core_loader import bibliotheque_core
from tabs.books_tab import BooksTab
from tabs.loans_tab import LoansTab
from tabs.stats_tab import StatsTab
from tabs.users_tab import UsersTab

TAB_NAMES = ("Livres", "Utilisateurs", "Emprunts", "Statistiques")

# Dossier de donnees par defaut : <agent>/data (a cote du dossier gui/).
DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)


class Application(ctk.CTk):
    def __init__(self, data_dir=None, auto_save=True):
        super().__init__()

        self.title("Bibliothèque personnelle")
        self.geometry("1000x650")

        self.data_dir = os.path.abspath(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.auto_save = auto_save
        self._destroyed = False

        # Persistance C++ : FileManager lit/ecrit books.txt et users.txt.
        os.makedirs(self.data_dir, exist_ok=True)
        self.file_manager = bibliotheque_core.FileManager(
            os.path.join(self.data_dir, "books.txt"),
            os.path.join(self.data_dir, "users.txt"),
        )

        # Objet C++ partage par les onglets.
        self.library = bibliotheque_core.Library()

        # Charge les donnees existantes au demarrage (logique C++).
        self.file_manager.load_library_data(self.library)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        for name in TAB_NAMES:
            self.tabview.add(name)

        self.tabs = {
            "Livres": BooksTab(
                self.tabview.tab("Livres"), self.library, on_change=self.refresh_all_tabs
            ),
            "Utilisateurs": UsersTab(
                self.tabview.tab("Utilisateurs"), self.library, on_change=self.refresh_all_tabs
            ),
            "Emprunts": LoansTab(
                self.tabview.tab("Emprunts"), self.library, on_change=self.refresh_all_tabs
            ),
            "Statistiques": StatsTab(
                self.tabview.tab("Statistiques"), self.library, self.file_manager, self.data_dir
            ),
        }
        for frame in self.tabs.values():
            frame.pack(fill="both", expand=True)

        self.status = ctk.CTkLabel(
            self,
            text=(
                f"Module C++ : {bibliotheque_core.__file__} "
                f"({self.library.get_total_books()} livre(s))"
            ),
            anchor="w",
        )
        self.status.pack(fill="x", padx=12, pady=(0, 10))

    def refresh_all_tabs(self):
        """Rafraichit tous les onglets qui exposent une methode refresh()."""
        for tab in self.tabs.values():
            refresh = getattr(tab, "refresh", None)
            if callable(refresh):
                refresh()
        self.status.configure(
            text=(
                f"Module C++ : {bibliotheque_core.__file__} "
                f"({self.library.get_total_books()} livre(s))"
            )
        )

    def save_data(self):
        """Sauvegarde la bibliotheque via le FileManager C++."""
        return self.file_manager.save_library_data(self.library)

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = True

        # Sauvegarde automatique a la fermeture (logique C++).
        if self.auto_save:
            try:
                self.save_data()
            except Exception:
                pass

        # Annule les callbacks "after" planifies par customTkinter afin
        # d'eviter des erreurs Tcl ("invalid command name") a la fermeture.
        try:
            for after_id in self.tk.eval("after info").split():
                self.after_cancel(after_id)
        except Exception:
            pass
        super().destroy()


def main(data_dir=None) -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    Application(data_dir=data_dir).mainloop()


if __name__ == "__main__":
    main()
