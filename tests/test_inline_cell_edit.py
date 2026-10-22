import os
import unittest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


class _FakeEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestInlineCellEdit(unittest.TestCase):
    def _make_tab(self):
        import tkinter as tk
        from soilclass.gui.input_tab import InputTab
        root = tk.Tk()
        root.geometry("900x700+0+0")
        self.addCleanup(root.destroy)
        tab = InputTab(root)
        tab.pack(fill="both", expand=True)
        return root, tab

    def _row_for_size(self, tab, size_str):
        for item in tab.tree.get_children():
            size, passing = tab.tree.item(item, "values")
            if size == size_str:
                return item, passing
        return None, None

    def _double_click(self, root, tab, item, column):
        tab.tree.see(item)
        root.update_idletasks()
        root.update()
        x, y, w, h = tab.tree.bbox(item, column)
        tab._edit_cell(_FakeEvent(x + 5, y + 5))
        root.update()
        entries = [w for w in tab.tree.winfo_children()
                  if w.winfo_class() == "TEntry"]
        self.assertEqual(len(entries), 1,
                         "exactly one edit box should appear")
        return entries[0]

    def _type_and_confirm(self, root, entry, text):
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.focus_force()
        root.update()
        entry.event_generate("<Return>")
        root.update()

    def test_double_click_passing_cell_and_retype_value(self):
        from soilclass.example_data import example_sample
        root, tab = self._make_tab()
        tab.load_sample(example_sample())
        root.update_idletasks()
        root.update()

        item, old_passing = self._row_for_size(tab, "0.106")
        self.assertEqual(old_passing, "31")

        entry = self._double_click(root, tab, item, "#2")
        self._type_and_confirm(root, entry, "27")

        _, new_passing = self._row_for_size(tab, "0.106")
        self.assertEqual(new_passing, "27")

    def test_double_click_size_cell_and_retype_value(self):
        from soilclass.example_data import example_sample
        root, tab = self._make_tab()
        tab.load_sample(example_sample())
        root.update_idletasks()
        root.update()

        item, _ = self._row_for_size(tab, "0.106")
        entry = self._double_click(root, tab, item, "#1")
        self._type_and_confirm(root, entry, "0.15")

        item2, passing = self._row_for_size(tab, "0.15")
        self.assertIsNotNone(item2)
        self.assertEqual(passing, "31")

    def test_editing_creates_an_undo_point(self):
        from soilclass.example_data import example_sample
        root, tab = self._make_tab()
        tab.load_sample(example_sample())
        root.update_idletasks()
        root.update()
        stack_before = len(tab._undo_stack)

        item, _ = self._row_for_size(tab, "0.106")
        entry = self._double_click(root, tab, item, "#2")
        self._type_and_confirm(root, entry, "27")

        self.assertEqual(len(tab._undo_stack), stack_before + 1)
        self.assertTrue(tab.undo())
        _, restored = self._row_for_size(tab, "0.106")
        self.assertEqual(restored, "31")

    def test_invalid_passing_value_rejected(self):
        from unittest import mock
        from soilclass.example_data import example_sample
        root, tab = self._make_tab()
        tab.load_sample(example_sample())
        root.update_idletasks()
        root.update()

        item, _ = self._row_for_size(tab, "0.106")
        entry = self._double_click(root, tab, item, "#2")
        with mock.patch("soilclass.gui.input_tab.messagebox.showerror") as err:
            self._type_and_confirm(root, entry, "150")
            self.assertTrue(err.called)

        _, passing = self._row_for_size(tab, "0.106")
        self.assertEqual(passing, "31", "value should be unchanged on error")

    def test_unchanged_value_does_not_push_undo_entry(self):
        from soilclass.example_data import example_sample
        root, tab = self._make_tab()
        tab.load_sample(example_sample())
        root.update_idletasks()
        root.update()
        stack_before = len(tab._undo_stack)

        item, old_passing = self._row_for_size(tab, "0.106")
        entry = self._double_click(root, tab, item, "#2")
        self._type_and_confirm(root, entry, old_passing)

        self.assertEqual(len(tab._undo_stack), stack_before)

    def test_escape_cancels_without_changing_value(self):
        from soilclass.example_data import example_sample
        root, tab = self._make_tab()
        tab.load_sample(example_sample())
        root.update_idletasks()
        root.update()

        item, _ = self._row_for_size(tab, "0.106")
        entry = self._double_click(root, tab, item, "#2")
        entry.delete(0, "end")
        entry.insert(0, "99")
        entry.event_generate("<Escape>")
        root.update()

        _, passing = self._row_for_size(tab, "0.106")
        self.assertEqual(passing, "31")


if __name__ == "__main__":
    unittest.main()
