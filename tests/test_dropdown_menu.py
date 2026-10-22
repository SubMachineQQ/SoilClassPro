import os
import unittest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestDropdownMenuGroupRowClick(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        self.root = tk.Tk()
        self.addCleanup(self.root.destroy)
        self.btn = tk.Button(self.root, text="Menu")
        self.btn.pack()
        self.root.update()

    def _make_menu(self):
        from soilclass.gui.dropdown_menu import DropdownMenu, MenuItem
        self.import_entry = MenuItem(
            "Import", items=[MenuItem("From CSV / Excel..."),
                             MenuItem("Load example data")])
        entries = [MenuItem("Home"), self.import_entry]
        palette = dict(border="#cccccc", surface="#ffffff", fg="#222222",
                       muted_fg="#888888", note_bg="#eef4ff",
                       accent_dark="#1a4fa0")
        menu = DropdownMenu(self.btn, entries, palette)
        self.addCleanup(lambda: None if menu._closed else menu.close())
        menu.update()
        return menu

    def _import_label_widget(self, menu):
        import tkinter as tk
        col0 = menu._columns.winfo_children()[0]
        for row in col0.winfo_children():
            for child in row.winfo_children():
                if isinstance(child, tk.Label) and "Import" in str(
                        child.cget("text")):
                    return child
        return None

    def test_clicking_a_group_row_opens_it_and_stays_open(self):
        menu = self._make_menu()
        lbl = self._import_label_widget(menu)
        self.assertIsNotNone(lbl, "could not find the Import row's label")

        lbl.event_generate("<Button-1>", x=5, y=5)
        menu.update()

        self.assertTrue(menu.winfo_exists() and not menu._closed,
                        "clicking a group row must not close the menu")
        self.assertEqual(menu._expanded_path, [id(self.import_entry)])


if __name__ == "__main__":
    unittest.main()
