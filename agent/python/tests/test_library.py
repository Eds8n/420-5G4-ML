"""Tests de la logique C++ exposee a Python (module bibliotheque_core).

Execution (depuis le devcontainer) :

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<build>/python python3 test_library.py

Ces tests utilisent uniquement la bibliotheque standard (unittest), donc
aucune dependance a installer.
"""

import unittest

import bibliotheque_core as bc


class TestBook(unittest.TestCase):
    def test_creation_et_champs(self):
        book = bc.Book("Le Petit Prince", "Saint-Exupery", "ISBN-1")
        self.assertEqual(book.title, "Le Petit Prince")
        self.assertEqual(book.author, "Saint-Exupery")
        self.assertEqual(book.isbn, "ISBN-1")
        self.assertTrue(book.available)
        self.assertEqual(book.borrower_id, "")

    def test_str(self):
        book = bc.Book("Titre", "Auteur", "ISBN-1")
        self.assertIn("Titre", str(book))


class TestUser(unittest.TestCase):
    def test_creation_et_champs(self):
        user = bc.User("Marie", "U1")
        self.assertEqual(user.name, "Marie")
        self.assertEqual(user.user_id, "U1")
        self.assertEqual(user.borrowed_books, [])
        self.assertEqual(user.number_of_borrowed_books(), 0)


class TestLibraryLivres(unittest.TestCase):
    def setUp(self):
        self.lib = bc.Library()
        self.lib.add_book(bc.Book("Le Petit Prince", "Saint-Exupery", "ISBN-1"))
        self.lib.add_book(bc.Book("Les Miserables", "Victor Hugo", "ISBN-2"))
        self.lib.add_book(bc.Book("Le Cid", "Corneille", "ISBN-3"))

    def test_ajouter_et_lister(self):
        books = self.lib.get_all_books()
        self.assertEqual(len(books), 3)
        self.assertIsInstance(books[0], bc.Book)

    def test_liste_renvoie_des_copies(self):
        # Modifier la liste Python ne doit pas toucher la bibliotheque C++.
        books = self.lib.get_all_books()
        books.clear()
        self.assertEqual(len(self.lib.get_all_books()), 3)

    def test_recherche_par_titre_insensible_a_la_casse(self):
        titres = {b.title for b in self.lib.search_books_by_title("le ")}
        self.assertEqual(titres, {"Le Petit Prince", "Le Cid"})

    def test_recherche_par_auteur(self):
        resultats = self.lib.search_books_by_author("hugo")
        self.assertEqual([b.isbn for b in resultats], ["ISBN-2"])

    def test_trouver_par_isbn(self):
        trouve = self.lib.find_book_by_isbn("ISBN-2")
        self.assertIsNotNone(trouve)
        self.assertEqual(trouve.title, "Les Miserables")
        self.assertIsNone(self.lib.find_book_by_isbn("INEXISTANT"))

    def test_supprimer_livre(self):
        self.assertTrue(self.lib.remove_book("ISBN-1"))
        self.assertFalse(self.lib.remove_book("ISBN-1"))  # deja supprime
        self.assertEqual(len(self.lib.get_all_books()), 2)

    def test_statistiques(self):
        self.assertEqual(self.lib.get_total_books(), 3)
        self.assertEqual(self.lib.get_available_book_count(), 3)
        self.assertEqual(self.lib.get_checked_out_book_count(), 0)


class TestLibraryEmprunts(unittest.TestCase):
    def setUp(self):
        self.lib = bc.Library()
        self.lib.add_book(bc.Book("Livre A", "Auteur", "A"))
        self.lib.add_user(bc.User("Marie", "U1"))

    def test_emprunter_et_retourner(self):
        self.assertTrue(self.lib.check_out_book("A", "U1"))
        self.assertFalse(self.lib.get_all_books()[0].available)
        self.assertEqual(self.lib.get_checked_out_book_count(), 1)

        # Deja emprunte -> refus
        self.assertFalse(self.lib.check_out_book("A", "U1"))

        self.assertTrue(self.lib.return_book("A"))
        self.assertTrue(self.lib.get_all_books()[0].available)

    def test_emprunt_utilisateur_inconnu_echoue(self):
        self.assertFalse(self.lib.check_out_book("A", "INCONNU"))

    def test_emprunt_livre_inconnu_echoue(self):
        self.assertFalse(self.lib.check_out_book("ZZZ", "U1"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
