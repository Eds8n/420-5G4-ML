"""Tests de persistance : chargement, sauvegarde et fermeture de l'application.

Les tests d'interface utilisent une copie temporaire des donnees : les fichiers
de `agent/data` ne sont jamais modifies.
Execution : python3 agent/gui/test_persistence.py
"""

import os
import tempfile
import unittest

from app import Application
from core_loader import bibliotheque_core
from gui_test_case import DATA_DIR, GuiTestCase


def _compter_lignes(chemin):
    if not os.path.exists(chemin):
        return 0
    with open(chemin) as fichier:
        return sum(1 for ligne in fichier if ligne.strip())


class TestFileManager(unittest.TestCase):
    """Tests directs du FileManager C++ (sans interface graphique)."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.books_file = os.path.join(self.tmp_dir.name, "books.txt")
        self.users_file = os.path.join(self.tmp_dir.name, "users.txt")
        self.fm = bibliotheque_core.FileManager(self.books_file, self.users_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_aller_retour_sauvegarde_chargement(self):
        lib = bibliotheque_core.Library()
        lib.add_book(bibliotheque_core.Book("Titre", "Auteur", "ISBN-1"))
        lib.add_user(bibliotheque_core.User("Marie", "USR001"))
        lib.check_out_book("ISBN-1", "USR001")
        self.assertTrue(self.fm.save_library_data(lib))

        rechargee = bibliotheque_core.Library()
        self.assertTrue(self.fm.load_library_data(rechargee))
        self.assertEqual(rechargee.get_total_books(), 1)
        self.assertEqual(len(rechargee.get_all_users()), 1)
        # L'etat d'emprunt survit a l'aller-retour fichier.
        self.assertFalse(rechargee.get_all_books()[0].available)
        self.assertEqual(rechargee.get_all_books()[0].borrower_id, "USR001")
        self.assertEqual(rechargee.get_all_users()[0].number_of_borrowed_books(), 1)

    def test_chargement_sans_fichier(self):
        vide = bibliotheque_core.Library()
        self.assertFalse(self.fm.load_library_data(vide))
        self.assertEqual(vide.get_total_books(), 0)

    def test_fichier_existe(self):
        self.assertFalse(self.fm.file_exists(self.books_file))
        lib = bibliotheque_core.Library()
        self.fm.save_library_data(lib)
        self.assertTrue(self.fm.file_exists(self.books_file))

    def test_sauvegarde_de_secours(self):
        lib = bibliotheque_core.Library()
        lib.add_book(bibliotheque_core.Book("Titre", "Auteur", "ISBN-1"))
        self.fm.save_library_data(lib)
        self.fm.create_backup()
        self.assertTrue(os.path.exists(self.books_file + ".backup"))


class TestChargementAuDemarrage(GuiTestCase):
    # Demarre a partir d'une copie de agent/data pour tester le chargement reel.
    copy_real_data = True

    def test_chargement_depuis_la_copie(self):
        attendu_livres = _compter_lignes(os.path.join(DATA_DIR, "books.txt"))
        attendu_users = _compter_lignes(os.path.join(DATA_DIR, "users.txt"))

        self.assertEqual(self.app.library.get_total_books(), attendu_livres)
        self.assertEqual(len(self.app.library.get_all_users()), attendu_users)
        # Les fichiers originaux ne sont pas touches (on lit une copie).
        self.assertEqual(
            self.app.data_dir, os.path.abspath(self.tmp_dir.name)
        )


class TestSauvegardeALaFermeture(GuiTestCase):
    def test_fermeture_ecrit_les_donnees(self):
        self.app.library.add_book(bibliotheque_core.Book("Titre X", "Auteur", "ISBN-X"))
        self.app.destroy()

        books_file = os.path.join(self.tmp_dir.name, "books.txt")
        self.assertTrue(os.path.exists(books_file))
        with open(books_file) as fichier:
            self.assertIn("ISBN-X", fichier.read())

    def test_reouverture_retrouve_les_donnees(self):
        self.app.library.add_book(bibliotheque_core.Book("Titre X", "Auteur", "ISBN-X"))
        self.app.library.add_user(bibliotheque_core.User("Marie", "USR001"))
        self.app.destroy()

        reouverte = Application(data_dir=self.tmp_dir.name)
        try:
            self.assertEqual(reouverte.library.get_total_books(), 1)
            self.assertEqual(reouverte.library.get_all_books()[0].isbn, "ISBN-X")
            self.assertEqual(len(reouverte.library.get_all_users()), 1)
        finally:
            reouverte.destroy()

    def test_aucune_ecriture_si_sauvegarde_desactivee(self):
        app = Application(data_dir=self.tmp_dir.name, auto_save=False)
        app.library.add_book(bibliotheque_core.Book("Titre X", "Auteur", "ISBN-X"))
        app.destroy()

        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir.name, "books.txt")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
