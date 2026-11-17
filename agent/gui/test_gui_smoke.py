"""Test de fumee de la fenetre principale (necessite un affichage X).

Verifie que la fenetre se construit et que les 4 onglets existent.
Execution : python3 agent/gui/test_gui_smoke.py
"""

import unittest

import customtkinter as ctk

from app import TAB_NAMES
from gui_test_case import GuiTestCase


class TestFenetrePrincipale(GuiTestCase):
    def test_construction_et_onglets(self):
        self.app.update()  # force le rendu sans lancer mainloop()
        self.assertEqual(set(self.app.tabs.keys()), set(TAB_NAMES))
        for frame in self.app.tabs.values():
            self.assertIsInstance(frame, ctk.CTkFrame)


if __name__ == "__main__":
    unittest.main(verbosity=2)
