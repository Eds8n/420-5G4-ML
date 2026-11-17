"""Onglet Emprunts : emprunter et retourner un livre.

Les choix se font via des listes deroulantes (livres disponibles / utilisateurs)
pour eviter de saisir les ISBN et ID a la main. Toute la logique metier vient
du module C++ `bibliotheque_core` (check_out_book / return_book).
"""

import customtkinter as ctk

ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"


class LoansTab(ctk.CTkFrame):
    def __init__(self, master, library, on_change=None):
        super().__init__(master)
        self.library = library
        self.on_change = on_change

        # Correspondances libelle affiche -> identifiant C++.
        self._book_display_to_isbn = {}
        self._user_display_to_id = {}
        self._return_display_to_isbn = {}

        self.grid_columnconfigure(0, weight=1)

        self._build_borrow_frame()
        self._build_return_frame()

        self.message_label = ctk.CTkLabel(self, text="", anchor="w")
        self.message_label.grid(row=2, column=0, sticky="ew", padx=12, pady=(4, 8))

        self.refresh()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _build_borrow_frame(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Emprunter un livre", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 0)
        )

        ctk.CTkLabel(frame, text="Livre disponible").grid(
            row=1, column=0, sticky="w", padx=8, pady=(6, 0)
        )
        ctk.CTkLabel(frame, text="Utilisateur").grid(
            row=1, column=1, sticky="w", padx=8, pady=(6, 0)
        )

        self.book_menu = ctk.CTkOptionMenu(frame, values=["Aucun livre disponible"])
        self.book_menu.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.user_menu = ctk.CTkOptionMenu(frame, values=["Aucun utilisateur"])
        self.user_menu.grid(row=2, column=1, sticky="ew", padx=8, pady=(0, 8))

        ctk.CTkButton(frame, text="Emprunter", width=120, command=self.on_checkout).grid(
            row=3, column=0, columnspan=2, pady=(0, 10)
        )

    def _build_return_frame(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="ew", padx=8, pady=4)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Retourner un livre", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 0)
        )
        ctk.CTkLabel(frame, text="Livre emprunté").grid(
            row=1, column=0, sticky="w", padx=8, pady=(6, 0)
        )

        self.return_menu = ctk.CTkOptionMenu(frame, values=["Aucun livre emprunté"])
        self.return_menu.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 6))

        ctk.CTkButton(frame, text="Retourner", width=120, command=self.on_return).grid(
            row=3, column=0, pady=(0, 10)
        )

    # ------------------------------------------------------------------
    # Rendu / rafraichissement
    # ------------------------------------------------------------------
    @staticmethod
    def _set_menu(menu, valeurs, placeholder):
        if valeurs:
            menu.configure(values=valeurs)
            menu.set(valeurs[0])
        else:
            menu.configure(values=[placeholder])
            menu.set(placeholder)

    def refresh(self):
        """Reconstruit les listes deroulantes a partir de l'etat C++."""
        books = self.library.get_all_books()
        users = self.library.get_all_users()

        disponibles = [b for b in books if b.available]
        empruntes = [b for b in books if not b.available]

        self._book_display_to_isbn = {self._book_label(b): b.isbn for b in disponibles}
        self._user_display_to_id = {self._user_label(u): u.user_id for u in users}
        self._return_display_to_isbn = {self._book_label(b): b.isbn for b in empruntes}

        self._set_menu(self.book_menu, list(self._book_display_to_isbn), "Aucun livre disponible")
        self._set_menu(self.user_menu, list(self._user_display_to_id), "Aucun utilisateur")
        self._set_menu(self.return_menu, list(self._return_display_to_isbn), "Aucun livre emprunté")

    @staticmethod
    def _book_label(book):
        return f"{book.title} ({book.isbn})"

    @staticmethod
    def _user_label(user):
        return f"{user.name} ({user.user_id})"

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def on_checkout(self):
        isbn = self._book_display_to_isbn.get(self.book_menu.get())
        user_id = self._user_display_to_id.get(self.user_menu.get())

        if isbn is None or user_id is None:
            self._show_message(
                "Erreur : aucun livre disponible ou aucun utilisateur à sélectionner.",
                error=True,
            )
            return

        if not self.library.check_out_book(isbn, user_id):
            self._show_message(
                "Erreur : emprunt impossible (livre non disponible ou utilisateur inconnu).",
                error=True,
            )
            return

        self._show_message(f"Emprunt effectué : « {self.book_menu.get()} ».", error=False)
        self._notify_change()

    def on_return(self):
        isbn = self._return_display_to_isbn.get(self.return_menu.get())
        if isbn is None:
            self._show_message("Erreur : aucun livre emprunté à retourner.", error=True)
            return

        if not self.library.return_book(isbn):
            self._show_message(
                "Erreur : retour impossible (ce livre n'est pas emprunté).", error=True
            )
            return

        self._show_message(f"Retour effectué : « {self.return_menu.get()} ».", error=False)
        self._notify_change()

    def _notify_change(self):
        if self.on_change is not None:
            self.on_change()

    def _show_message(self, texte, error):
        self.message_label.configure(
            text=texte, text_color=ERROR_COLOR if error else SUCCESS_COLOR
        )
