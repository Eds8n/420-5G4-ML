"""Onglet Statistiques : affichage des statistiques et sauvegarde des donnees.

Toutes les valeurs viennent du module C++ `bibliotheque_core` et la sauvegarde
passe par le FileManager C++ expose par pybind11 : aucune logique metier n'est
reecrite en Python.
"""

import os

import customtkinter as ctk

ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"


class StatsTab(ctk.CTkFrame):
    def __init__(self, master, library, file_manager, data_dir):
        super().__init__(master)
        self.library = library
        self.file_manager = file_manager
        self.data_dir = data_dir

        # Etat du dernier rendu (utile pour l'affichage et les tests).
        self.rendered_stats = {}

        self.grid_columnconfigure(0, weight=1)

        self._build_stats_frame()
        self._build_actions_frame()

        self.message_label = ctk.CTkLabel(self, text="", anchor="w")
        self.message_label.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 8))

        self.refresh()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _build_stats_frame(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text="Statistiques de la bibliothèque",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 4))

        self.value_labels = {}
        lignes = [
            ("total_books", "Total des livres"),
            ("available", "Livres disponibles"),
            ("checked_out", "Livres empruntés"),
            ("users", "Total des utilisateurs"),
        ]
        for index, (cle, libelle) in enumerate(lignes, start=1):
            ctk.CTkLabel(frame, text=libelle + " :", anchor="w").grid(
                row=index, column=0, sticky="w", padx=8, pady=2
            )
            valeur = ctk.CTkLabel(frame, text="0", anchor="w", font=ctk.CTkFont(weight="bold"))
            valeur.grid(row=index, column=1, sticky="w", padx=8, pady=2)
            self.value_labels[cle] = valeur

    def _build_actions_frame(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(frame, text="Sauvegarde", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=8, pady=(8, 4)
        )
        ctk.CTkButton(
            frame, text="Sauvegarder les données", command=self.on_save
        ).pack(side="left", padx=8, pady=(0, 8))
        ctk.CTkButton(
            frame, text="Créer une sauvegarde", command=self.on_backup
        ).pack(side="left", padx=8, pady=(0, 8))

    # ------------------------------------------------------------------
    # Rendu / rafraichissement
    # ------------------------------------------------------------------
    def refresh(self):
        """Relit l'etat C++ et met a jour les valeurs affichees."""
        self.rendered_stats = {
            "total_books": self.library.get_total_books(),
            "available": self.library.get_available_book_count(),
            "checked_out": self.library.get_checked_out_book_count(),
            # Pas de getter dedie en C++ : main.cpp utilise aussi getAllUsers().size().
            "users": len(self.library.get_all_users()),
        }
        for cle, valeur in self.rendered_stats.items():
            self.value_labels[cle].configure(text=str(valeur))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def on_save(self):
        if self.file_manager.save_library_data(self.library):
            self._show_message("Données sauvegardées avec succès.", error=False)
        else:
            self._show_message("Erreur lors de la sauvegarde des données.", error=True)

    def on_backup(self):
        # copy_file du C++ refuse d'ecraser un .backup existant : on retire
        # l'ancienne sauvegarde pour pouvoir en creer une nouvelle.
        self._clear_existing_backups()
        try:
            self.file_manager.create_backup()
        except Exception as exc:
            self._show_message(f"Erreur : sauvegarde impossible ({exc}).", error=True)
            return
        self._show_message("Sauvegarde de secours créée.", error=False)

    def _clear_existing_backups(self):
        for nom in ("books.txt", "users.txt"):
            chemin = os.path.join(self.data_dir, nom + ".backup")
            if os.path.exists(chemin):
                os.remove(chemin)

    def _show_message(self, texte, error):
        self.message_label.configure(
            text=texte, text_color=ERROR_COLOR if error else SUCCESS_COLOR
        )
