"""Base commune aux tests d'interface.

Chaque test travaille dans un dossier de donnees temporaire : aucun test ne lit
ni n'ecrit dans `agent/data`, afin de ne jamais modifier les fichiers originaux.
Une sous-classe peut demander une copie du dossier reel via `copy_real_data`.
"""

import os
import shutil
import tempfile
import unittest

from app import Application

# Dossier de donnees reel (jamais modifie par les tests).
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(AGENT_DIR, "data")


class GuiTestCase(unittest.TestCase):
    # Passer a True dans une sous-classe pour partir d'une copie de agent/data.
    copy_real_data = False

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        if self.copy_real_data:
            for nom in ("books.txt", "users.txt"):
                source = os.path.join(DATA_DIR, nom)
                if os.path.exists(source):
                    shutil.copy(source, self.tmp_dir.name)
        self.app = Application(data_dir=self.tmp_dir.name)
        self.app.update()

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass
        self.tmp_dir.cleanup()
