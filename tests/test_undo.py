import os
import unittest


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestUndo(unittest.TestCase):
    def _make_tab(self):
        import tkinter as tk
        from soilclass.gui.input_tab import InputTab
        root = tk.Tk()
        self.addCleanup(root.destroy)
        tab = InputTab(root)
        return tab

    def test_undo_reverts_add(self):
        tab = self._make_tab()
        tab.size_var.set("4.75")
        tab.pass_var.set("83")
        tab.add_row()
        self.assertEqual(len(tab._table_rows()), 1)
        self.assertTrue(tab.undo())
        self.assertEqual(len(tab._table_rows()), 0)

    def test_undo_reverts_clear(self):
        tab = self._make_tab()
        for size, passing in [("4.75", "83"), ("2.0", "65")]:
            tab.size_var.set(size)
            tab.pass_var.set(passing)
            tab.add_row()
        self.assertEqual(len(tab._table_rows()), 2)

        tab.tree.selection_set(tab.tree.get_children())
        tab.clear_table()
        self.assertEqual(len(tab._table_rows()), 0)

        self.assertTrue(tab.undo())
        self.assertEqual(len(tab._table_rows()), 2)

    def test_undo_reverts_remove_selected(self):
        tab = self._make_tab()
        for size, passing in [("4.75", "83"), ("2.0", "65")]:
            tab.size_var.set(size)
            tab.pass_var.set(passing)
            tab.add_row()
        first_item = tab.tree.get_children()[0]
        tab.tree.selection_set(first_item)
        tab.remove_selected()
        self.assertEqual(len(tab._table_rows()), 1)
        self.assertTrue(tab.undo())
        self.assertEqual(len(tab._table_rows()), 2)

    def test_undo_on_empty_stack_returns_false(self):
        tab = self._make_tab()
        self.assertFalse(tab.undo())

    def test_multiple_undos_walk_back_through_history(self):
        tab = self._make_tab()
        tab.size_var.set("4.75")
        tab.pass_var.set("83")
        tab.add_row()
        tab.size_var.set("2.0")
        tab.pass_var.set("65")
        tab.add_row()
        self.assertEqual(len(tab._table_rows()), 2)

        self.assertTrue(tab.undo())
        self.assertEqual(len(tab._table_rows()), 1)
        self.assertTrue(tab.undo())
        self.assertEqual(len(tab._table_rows()), 0)
        self.assertFalse(tab.undo())


if __name__ == "__main__":
    unittest.main()
