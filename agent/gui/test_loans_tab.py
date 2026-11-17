"""Tests d'integration de l'onglet Emprunts (necessitent un affichage X).

Execution : python3 agent/gui/test_loans_tab.py
"""

import unittest

from core_loader import bibliotheque_core
from gui_test_case import GuiTestCase


class TestLoansTab(GuiTestCase):
    def setUp(self):
        super().setUp()
        self.tab = self.app.tabs["Emprunts"]
        self.books = self.app.tabs["Livres"]
        self.users = self.app.tabs["Utilisateurs"]

    def _setup_data(self):
        self.app.library.add_book(bibliotheque_core.Book("Livre A", "Auteur", "ISBN-1"))
        self.app.library.add_user(bibliotheque_core.User("Marie", "USR001"))
        self.app.refresh_all_tabs()

    def test_emprunt_met_a_jour_tous_les_onglets(self):
        self._setup_data()
        self.tab.on_checkout()

        self.assertFalse(self.app.library.get_all_books()[0].available)
        # Emprunts : le livre passe des disponibles aux empruntés.
        self.assertNotIn("ISBN-1", self.tab._book_display_to_isbn.values())
        self.assertIn("ISBN-1", self.tab._return_display_to_isbn.values())
        # Livres : le statut se met a jour.
        self.assertTrue(self.books.rendered_statuses[0].startswith("Emprunté"))
        # Utilisateurs : le compteur se met a jour.
        self.assertEqual(self.users.rendered_counts[0], 1)

    def test_retour_remet_le_livre_disponible(self):
        self._setup_data()
        self.tab.on_checkout()
        self.tab.on_return()

        self.assertTrue(self.app.library.get_all_books()[0].available)
        self.assertIn("ISBN-1", self.tab._book_display_to_isbn.values())
        self.assertEqual(self.tab._return_display_to_isbn, {})
        self.assertEqual(self.users.rendered_counts[0], 0)

    def test_emprunt_sans_livre_ou_utilisateur_echoue(self):
        # Aucune donnee : les listes sont vides.
        self.tab.on_checkout()
        self.assertIn("Erreur", self.tab.message_label.cget("text"))

    def test_emprunt_livre_non_disponible_echoue(self):
        self._setup_data()
        # Emprunt direct via le C++ : le livre n'est plus disponible.
        self.assertTrue(self.app.library.check_out_book("ISBN-1", "USR001"))
        self.app.refresh_all_tabs()
        self.assertEqual(self.tab._book_display_to_isbn, {})
        self.tab.on_checkout()
        self.assertIn("Erreur", self.tab.message_label.cget("text"))

    def test_retour_livre_non_emprunte_echoue(self):
        # Livre present mais disponible (jamais emprunte).
        self.app.library.add_book(bibliotheque_core.Book("Livre A", "Auteur", "ISBN-1"))
        self.app.refresh_all_tabs()
        self.tab.on_return()
        self.assertIn("Erreur", self.tab.message_label.cget("text"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
