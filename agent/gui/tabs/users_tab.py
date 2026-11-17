"""Onglet Utilisateurs : ajouter et afficher les utilisateurs.

Toute la logique metier vient du module C++ `bibliotheque_core` (objet
`Library` partage) : ce fichier ne fait que l'interface et la validation.
"""

import customtkinter as ctk

from core_loader import bibliotheque_core

ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"


class UsersTab(ctk.CTkFrame):
    def __init__(self, master, library, on_change=None):
        super().__init__(master)
        self.library = library
        self.on_change = on_change
        # Etat du dernier rendu (utile pour l'affichage et les tests).
        self.rendered_ids = []
        self.rendered_counts = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_add_form()

        self.message_label = ctk.CTkLabel(self, text="", anchor="w")
        self.message_label.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))

        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self.refresh()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _build_add_form(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        for col in range(2):
            frame.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(frame, text="Nom").grid(row=0, column=0, sticky="w", padx=4, pady=(6, 0))
        ctk.CTkLabel(frame, text="ID utilisateur").grid(
            row=0, column=1, sticky="w", padx=4, pady=(6, 0)
        )

        self.name_entry = ctk.CTkEntry(frame, placeholder_text="Nom de l'utilisateur")
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))
        self.user_id_entry = ctk.CTkEntry(frame, placeholder_text="Identifiant (ex. USR001)")
        self.user_id_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=(0, 8))

        ctk.CTkButton(frame, text="Ajouter", width=100, command=self.on_add).grid(
            row=1, column=2, padx=4, pady=(0, 8)
        )

    # ------------------------------------------------------------------
    # Rendu de la liste
    # ------------------------------------------------------------------
    @staticmethod
    def _configure_columns(frame):
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=2)
        frame.grid_columnconfigure(2, weight=2)

    def refresh(self):
        """Affiche tous les utilisateurs de la bibliotheque."""
        self._render(self.library.get_all_users())

    def _render(self, users):
        for child in self.list_frame.winfo_children():
            child.destroy()

        self.rendered_ids = []
        self.rendered_counts = []

        header = ctk.CTkFrame(self.list_frame)
        header.pack(fill="x", pady=(0, 2))
        self._configure_columns(header)
        for col, titre in enumerate(["Nom", "ID", "Livres empruntés"]):
            ctk.CTkLabel(
                header, text=titre, font=ctk.CTkFont(weight="bold"), anchor="w"
            ).grid(row=0, column=col, sticky="ew", padx=4, pady=2)

        for user in users:
            nb = user.number_of_borrowed_books()
            self.rendered_ids.append(user.user_id)
            self.rendered_counts.append(nb)

            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            self._configure_columns(row)
            ctk.CTkLabel(row, text=user.name, anchor="w").grid(
                row=0, column=0, sticky="ew", padx=4
            )
            ctk.CTkLabel(row, text=user.user_id, anchor="w").grid(
                row=0, column=1, sticky="ew", padx=4
            )
            ctk.CTkLabel(row, text=str(nb), anchor="w").grid(
                row=0, column=2, sticky="ew", padx=4
            )

    # ------------------------------------------------------------------
    # Actions (reliees au bouton)
    # ------------------------------------------------------------------
    def on_add(self):
        nom = self.name_entry.get().strip()
        user_id = self.user_id_entry.get().strip()

        if not nom or not user_id:
            self._show_message("Erreur : le nom et l'ID sont obligatoires.", error=True)
            return

        if self.library.find_user_by_id(user_id) is not None:
            self._show_message(
                f"Erreur : un utilisateur avec l'ID « {user_id} » existe déjà.", error=True
            )
            return

        self.library.add_user(bibliotheque_core.User(nom, user_id))
        for entry in (self.name_entry, self.user_id_entry):
            entry.delete(0, "end")
        self.refresh()
        self._show_message(f"Utilisateur « {nom} » ajouté.", error=False)
        self._notify_change()

    def _notify_change(self):
        if self.on_change is not None:
            self.on_change()

    def _show_message(self, texte, error):
        self.message_label.configure(
            text=texte, text_color=ERROR_COLOR if error else SUCCESS_COLOR
        )
