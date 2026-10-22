import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from soilclass.assets_path import EXAMPLES_DIR, IMPORT_HELP_DIR
from soilclass.gui.import_help import EXAMPLES_FOLDER, LAYOUTS
from soilclass.i18n import _EN, _TR
from soilclass.importers.csv_import import import_file


class TestImportHelpAssets(unittest.TestCase):
    def test_every_layout_has_an_example_and_a_preview(self):
        for stem, ext in LAYOUTS:
            self.assertTrue((EXAMPLES_DIR / f"{stem}.{ext}").is_file(), stem)
            self.assertTrue((IMPORT_HELP_DIR / f"{stem}.png").is_file(), stem)

    def test_every_layout_is_translated(self):
        for stem, _ext in LAYOUTS:
            for key in (f"import_layout_{stem[2:]}",
                        f"import_layout_{stem[2:]}_desc"):
                self.assertIn(key, _EN)
                self.assertIn(key, _TR)

    def test_every_example_imports(self):
        for stem, ext in LAYOUTS:
            data = import_file(str(EXAMPLES_DIR / f"{stem}.{ext}"))
            self.assertTrue(data.ok, stem)
            self.assertGreaterEqual(len(data.sieve), 5, stem)


@unittest.skipUnless(os.environ.get("DISPLAY"), "no DISPLAY available for a GUI test")
class TestImportHelpDialog(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        from soilclass.gui import theme
        self.root = tk.Tk()
        self.addCleanup(self.root.destroy)
        self.palette = theme.apply_theme(self.root, dark=False)

    def test_dialog_switches_between_layouts(self):
        from soilclass.gui.import_help import ImportHelpDialog
        dlg = ImportHelpDialog(self.root, self.palette)
        self.root.update()
        for stem, _ext in LAYOUTS:
            dlg._list.selection_set(stem)
            dlg._show()
            self.root.update()
            self.assertIsNotNone(dlg._images.get(stem), stem)
        dlg.destroy()

    def test_save_examples_copies_every_file(self):
        from soilclass.gui import import_help
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(import_help.filedialog, "askdirectory",
                                  return_value=tmp), \
                mock.patch.object(import_help.messagebox, "showinfo"), \
                mock.patch.object(import_help.os, "startfile", create=True):
            folder = import_help.save_examples(self.root)
            self.assertEqual(folder, Path(tmp) / EXAMPLES_FOLDER)
            names = sorted(p.name for p in folder.iterdir())
            self.assertEqual(names, sorted(f"{s}.{e}" for s, e in LAYOUTS))

    def test_cancelled_folder_choice_does_nothing(self):
        from soilclass.gui import import_help
        with mock.patch.object(import_help.filedialog, "askdirectory",
                               return_value=""):
            self.assertIsNone(import_help.save_examples(self.root))


if __name__ == "__main__":
    unittest.main()
