"""Tests d'integration de l'onglet Utilisateurs (necessitent un affichage X).

Execution : python3 agent/gui/test_users_tab.py
"""

import unittest

from core_loader import bibliotheque_core
from gui_test_case import GuiTestCase


class TestUsersTab(GuiTestCase):
    def setUp(self):
        super().setUp()
        self.tab = self.app.tabs["Utilisateurs"]

    def _add(self, nom, user_id):
        self.tab.name_entry.delete(0, "end")
        self.tab.name_entry.insert(0, nom)
        self.tab.user_id_entry.delete(0, "end")
        self.tab.user_id_entry.insert(0, user_id)
        self.tab.on_add()

    def test_ajout_met_a_jour_la_liste(self):
        self._add("Marie", "USR001")
        self.assertEqual(len(self.app.library.get_all_users()), 1)
        self.assertEqual(self.tab.rendered_ids, ["USR001"])
        self.assertEqual(self.tab.name_entry.get(), "")

    def test_id_duplique_refuse(self):
        self._add("Marie", "USR001")
        self._add("Jean", "USR001")
        self.assertEqual(len(self.app.library.get_all_users()), 1)
        self.assertIn("existe déjà", self.tab.message_label.cget("text"))

    def test_champ_vide_refuse(self):
        self._add("", "USR001")
        self.assertEqual(len(self.app.library.get_all_users()), 0)
        self.assertIn("obligatoires", self.tab.message_label.cget("text"))

    def test_compteur_de_livres_empruntes(self):
        self._add("Marie", "USR001")
        # Emprunt via le module C++ (aucune logique metier en Python).
        self.app.library.add_book(bibliotheque_core.Book("Livre A", "Auteur", "ISBN-1"))
        self.assertTrue(self.app.library.check_out_book("ISBN-1", "USR001"))
        self.tab.refresh()
        self.assertEqual(self.tab.rendered_counts, [1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
