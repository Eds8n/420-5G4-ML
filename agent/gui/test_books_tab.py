"""Tests d'integration de l'onglet Livres (necessitent un affichage X).

Execution : python3 agent/gui/test_books_tab.py
"""

import unittest

from core_loader import bibliotheque_core
from gui_test_case import GuiTestCase


class TestBooksTab(GuiTestCase):
    def setUp(self):
        super().setUp()
        self.tab = self.app.tabs["Livres"]

    def _add(self, titre, auteur, isbn):
        self.tab.title_entry.delete(0, "end")
        self.tab.title_entry.insert(0, titre)
        self.tab.author_entry.delete(0, "end")
        self.tab.author_entry.insert(0, auteur)
        self.tab.isbn_entry.delete(0, "end")
        self.tab.isbn_entry.insert(0, isbn)
        self.tab.on_add()

    def test_ajout_met_a_jour_la_liste(self):
        self._add("Le Petit Prince", "Saint-Exupery", "ISBN-1")
        self.assertEqual(self.app.library.get_total_books(), 1)
        self.assertEqual(self.tab.rendered_isbns, ["ISBN-1"])
        # Les champs sont vides apres un ajout reussi.
        self.assertEqual(self.tab.title_entry.get(), "")

    def test_isbn_duplique_refuse(self):
        self._add("Livre A", "Auteur", "ISBN-1")
        self._add("Livre B", "Auteur", "ISBN-1")
        self.assertEqual(self.app.library.get_total_books(), 1)
        self.assertIn("existe déjà", self.tab.message_label.cget("text"))

    def test_champ_vide_refuse(self):
        self._add("", "Auteur", "ISBN-1")
        self.assertEqual(self.app.library.get_total_books(), 0)
        self.assertIn("obligatoires", self.tab.message_label.cget("text"))

    def test_recherche_par_titre(self):
        self._add("Le Petit Prince", "Saint-Exupery", "ISBN-1")
        self._add("Les Miserables", "Victor Hugo", "ISBN-2")
        self.tab.search_mode.set("Titre")
        self.tab.search_entry.delete(0, "end")
        self.tab.search_entry.insert(0, "petit")
        self.tab.on_search()
        self.assertEqual(self.tab.rendered_isbns, ["ISBN-1"])

    def test_recherche_par_auteur(self):
        self._add("Le Petit Prince", "Saint-Exupery", "ISBN-1")
        self._add("Les Miserables", "Victor Hugo", "ISBN-2")
        self.tab.search_mode.set("Auteur")
        self.tab.search_entry.delete(0, "end")
        self.tab.search_entry.insert(0, "hugo")
        self.tab.on_search()
        self.assertEqual(self.tab.rendered_isbns, ["ISBN-2"])

    def test_suppression_met_a_jour(self):
        self._add("Livre A", "Auteur", "ISBN-1")
        self.tab.on_delete("ISBN-1")
        self.assertEqual(self.app.library.get_total_books(), 0)
        self.assertEqual(self.tab.rendered_isbns, [])

    def test_statut_affiche_emprunte(self):
        self._add("Livre A", "Auteur", "ISBN-1")
        # Emprunt via le module C++ (aucune logique metier en Python).
        self.app.library.add_user(bibliotheque_core.User("Marie", "U1"))
        self.assertTrue(self.app.library.check_out_book("ISBN-1", "U1"))
        self.tab.refresh()
        self.assertTrue(self.tab.rendered_statuses[0].startswith("Emprunté"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
