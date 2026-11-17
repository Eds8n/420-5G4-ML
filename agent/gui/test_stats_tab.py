"""Tests d'integration de l'onglet Statistiques (necessitent un affichage X).

Execution : python3 agent/gui/test_stats_tab.py
"""

import os
import unittest

from gui_test_case import GuiTestCase


class TestStatsTab(GuiTestCase):
    def setUp(self):
        super().setUp()
        self.stats = self.app.tabs["Statistiques"]
        self.books = self.app.tabs["Livres"]
        self.users = self.app.tabs["Utilisateurs"]
        self.loans = self.app.tabs["Emprunts"]

    def _add_book(self, titre="Livre A", isbn="ISBN-1"):
        self.books.title_entry.delete(0, "end")
        self.books.title_entry.insert(0, titre)
        self.books.author_entry.delete(0, "end")
        self.books.author_entry.insert(0, "Auteur")
        self.books.isbn_entry.delete(0, "end")
        self.books.isbn_entry.insert(0, isbn)
        self.books.on_add()

    def _add_user(self, nom="Marie", user_id="USR001"):
        self.users.name_entry.delete(0, "end")
        self.users.name_entry.insert(0, nom)
        self.users.user_id_entry.delete(0, "end")
        self.users.user_id_entry.insert(0, user_id)
        self.users.on_add()

    def test_statistiques_initiales(self):
        self.assertEqual(
            self.stats.rendered_stats,
            {"total_books": 0, "available": 0, "checked_out": 0, "users": 0},
        )

    def test_statistiques_mises_a_jour_automatiquement(self):
        self._add_book("Livre A", "ISBN-1")
        self._add_user("Marie", "USR001")

        # Mise a jour automatique apres ajout d'un livre et d'un utilisateur.
        self.assertEqual(self.stats.rendered_stats["total_books"], 1)
        self.assertEqual(self.stats.rendered_stats["available"], 1)
        self.assertEqual(self.stats.rendered_stats["users"], 1)
        # Les labels affiches refletent aussi l'etat.
        self.assertEqual(self.stats.value_labels["total_books"].cget("text"), "1")

        # Mise a jour automatique apres un emprunt.
        self.loans.on_checkout()
        self.assertEqual(self.stats.rendered_stats["available"], 0)
        self.assertEqual(self.stats.rendered_stats["checked_out"], 1)
        self.assertEqual(self.stats.value_labels["checked_out"].cget("text"), "1")

    def test_sauvegarde_ecrit_les_fichiers(self):
        self._add_book("Livre A", "ISBN-1")
        self.stats.on_save()

        books_file = os.path.join(self.tmp_dir.name, "books.txt")
        self.assertTrue(os.path.exists(books_file))
        with open(books_file) as fichier:
            self.assertIn("ISBN-1", fichier.read())
        self.assertIn("succès", self.stats.message_label.cget("text"))

    def test_sauvegarde_de_secours(self):
        self._add_book("Livre A", "ISBN-1")
        self.stats.on_save()
        self.stats.on_backup()

        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir.name, "books.txt.backup")))

    def test_sauvegarde_de_secours_repetee(self):
        self._add_book("Livre A", "ISBN-1")
        self.stats.on_save()
        self.stats.on_backup()
        # Une deuxieme sauvegarde doit remplacer la precedente sans erreur.
        self.stats.on_backup()

        self.assertIn("créée", self.stats.message_label.cget("text"))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir.name, "books.txt.backup")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
