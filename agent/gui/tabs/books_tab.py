"""Onglet Livres : afficher, ajouter, rechercher et supprimer des livres.

Toute la logique metier vient du module C++ `bibliotheque_core` (via l'objet
`Library` partage) : ce fichier ne fait que l'interface et la validation des
saisies.
"""

import customtkinter as ctk

from core_loader import bibliotheque_core

ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"


class BooksTab(ctk.CTkFrame):
    def __init__(self, master, library, on_change=None):
        super().__init__(master)
        self.library = library
        self.on_change = on_change
        # Etat du dernier rendu (utile pour l'affichage et les tests).
        self.rendered_isbns = []
        self.rendered_statuses = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_add_form()
        self._build_search_bar()

        self.message_label = ctk.CTkLabel(self, text="", anchor="w")
        self.message_label.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 4))

        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self.refresh()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _build_add_form(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        for col in range(3):
            frame.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(frame, text="Titre").grid(row=0, column=0, sticky="w", padx=4, pady=(6, 0))
        ctk.CTkLabel(frame, text="Auteur").grid(row=0, column=1, sticky="w", padx=4, pady=(6, 0))
        ctk.CTkLabel(frame, text="ISBN").grid(row=0, column=2, sticky="w", padx=4, pady=(6, 0))

        self.title_entry = ctk.CTkEntry(frame, placeholder_text="Titre du livre")
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))
        self.author_entry = ctk.CTkEntry(frame, placeholder_text="Auteur")
        self.author_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=(0, 8))
        self.isbn_entry = ctk.CTkEntry(frame, placeholder_text="ISBN")
        self.isbn_entry.grid(row=1, column=2, sticky="ew", padx=4, pady=(0, 8))

        ctk.CTkButton(frame, text="Ajouter", width=100, command=self.on_add).grid(
            row=1, column=3, padx=4, pady=(0, 8)
        )

    def _build_search_bar(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(frame, text="Rechercher :").pack(side="left", padx=(8, 4), pady=8)
        self.search_entry = ctk.CTkEntry(frame, placeholder_text="terme à chercher...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=4, pady=8)
        self.search_mode = ctk.CTkOptionMenu(frame, values=["Titre", "Auteur"], width=110)
        self.search_mode.pack(side="left", padx=4, pady=8)
        ctk.CTkButton(frame, text="Rechercher", width=110, command=self.on_search).pack(
            side="left", padx=4
        )
        ctk.CTkButton(frame, text="Tout afficher", width=110, command=self.refresh).pack(
            side="left", padx=(4, 8)
        )

    # ------------------------------------------------------------------
    # Rendu de la liste
    # ------------------------------------------------------------------
    @staticmethod
    def _configure_columns(frame):
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=2)
        frame.grid_columnconfigure(2, weight=2)
        frame.grid_columnconfigure(3, weight=2)
        frame.grid_columnconfigure(4, weight=0)

    def refresh(self):
        """Affiche tous les livres de la bibliotheque."""
        self._render(self.library.get_all_books())

    def _render(self, books):
        for child in self.list_frame.winfo_children():
            child.destroy()

        self.rendered_isbns = []
        self.rendered_statuses = []

        header = ctk.CTkFrame(self.list_frame)
        header.pack(fill="x", pady=(0, 2))
        self._configure_columns(header)
        for col, titre in enumerate(["Titre", "Auteur", "ISBN", "Statut"]):
            ctk.CTkLabel(
                header, text=titre, font=ctk.CTkFont(weight="bold"), anchor="w"
            ).grid(row=0, column=col, sticky="ew", padx=4, pady=2)

        for book in books:
            statut = "Disponible" if book.available else f"Emprunté ({book.borrower_id})"
            self.rendered_isbns.append(book.isbn)
            self.rendered_statuses.append(statut)

            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            self._configure_columns(row)
            ctk.CTkLabel(row, text=book.title, anchor="w").grid(
                row=0, column=0, sticky="ew", padx=4
            )
            ctk.CTkLabel(row, text=book.author, anchor="w").grid(
                row=0, column=1, sticky="ew", padx=4
            )
            ctk.CTkLabel(row, text=book.isbn, anchor="w").grid(
                row=0, column=2, sticky="ew", padx=4
            )
            ctk.CTkLabel(row, text=statut, anchor="w").grid(
                row=0, column=3, sticky="ew", padx=4
            )
            ctk.CTkButton(
                row,
                text="Supprimer",
                width=90,
                command=lambda isbn=book.isbn: self.on_delete(isbn),
            ).grid(row=0, column=4, padx=4)

    # ------------------------------------------------------------------
    # Actions (reliees aux boutons)
    # ------------------------------------------------------------------
    def on_add(self):
        titre = self.title_entry.get().strip()
        auteur = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()

        if not titre or not auteur or not isbn:
            self._show_message(
                "Erreur : le titre, l'auteur et l'ISBN sont obligatoires.", error=True
            )
            return

        if self.library.find_book_by_isbn(isbn) is not None:
            self._show_message(
                f"Erreur : un livre avec l'ISBN « {isbn} » existe déjà.", error=True
            )
            return

        self.library.add_book(bibliotheque_core.Book(titre, auteur, isbn))
        for entry in (self.title_entry, self.author_entry, self.isbn_entry):
            entry.delete(0, "end")
        self.refresh()
        self._show_message(f"Livre « {titre} » ajouté.", error=False)
        self._notify_change()

    def on_search(self):
        terme = self.search_entry.get().strip()
        if not terme:
            self.refresh()
            self._show_message("Recherche vide : tous les livres sont affichés.", error=False)
            return

        if self.search_mode.get() == "Titre":
            books = self.library.search_books_by_title(terme)
        else:
            books = self.library.search_books_by_author(terme)

        self._render(books)
        self._show_message(f"{len(books)} résultat(s) pour « {terme} ».", error=False)

    def on_delete(self, isbn):
        if self.library.remove_book(isbn):
            self.refresh()
            self._show_message(f"Livre « {isbn} » supprimé.", error=False)
            self._notify_change()
        else:
            self._show_message(f"Erreur : livre « {isbn} » introuvable.", error=True)

    def _notify_change(self):
        if self.on_change is not None:
            self.on_change()

    def _show_message(self, texte, error):
        self.message_label.configure(
            text=texte, text_color=ERROR_COLOR if error else SUCCESS_COLOR
        )
